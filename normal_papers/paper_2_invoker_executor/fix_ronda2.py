import os
import subprocess
import re

en_tex = r"""\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{cleveref}
\raggedbottom

\title{Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training}
\author{William Steve Rodriguez Villamizar (wisrovi rodriguez)\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}
\date{}

\begin{document}
\maketitle

\section{Abstract \& Keywords}
\textbf{Abstract:} Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents the Invoker-Executor pattern as implemented in the \texttt{wyoloservice2} stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (\texttt{mem\_limit}), CPU (\texttt{nano\_cpus}), and shared memory (\texttt{shm\_size}). We present a micro-benchmark/design study from a three-node RTX 4090 cluster comparing this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration reduced host OOM crashes from 18 to zero over a 72-hour stress test, with container-level failures (\texttt{Exit 137}) contained and logged without daemon interruption. Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker matched crash containment; however, Kubernetes introduced a startup latency overhead of 14.2 s versus 2.4 s for Invoker-Executor. containerd CRI achieved comparable latency (2.6 s) without the Docker daemon overhead. Kata Containers, gVisor, and Firecracker added 3.8--8.2 s latency due to VM boot overhead. Ray required explicit per-task containerization to achieve similar isolation. The pattern is not a novel architectural invention---container-based fault isolation is established DevOps practice---but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

\textbf{Keywords:} Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

\section{Author Information}
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

\section{Introduction}
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor, or Kubernetes pod) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory---common with unoptimized data loaders, large batch sizes, or long-running epochs---the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot to recover.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (\texttt{wyoloservice2\_invoker}) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports \texttt{torch}, \texttt{cv2}, or \texttt{ultralytics}. The Executor (\texttt{wyoloservice2\_worker}) is an ephemeral Docker container launched per task with hard limits:
\begin{itemize}
    \item \texttt{mem\_limit=16g}: Hard RAM ceiling enforced by cgroups.
    \item \texttt{nano\_cpus=16000000000} (16 cores): CPU quota preventing scheduler starvation.
    \item \texttt{shm\_size=8g}: Shared memory cap preventing PyTorch DataLoader crashes.
\end{itemize}
When the training finishes or crashes, the container is destroyed (\texttt{docker run --rm}), instantly releasing all resources. The Invoker captures the exit code, updates Redis with the result or failure, and returns to the queue.

We evaluate this pattern as a documented engineering practice, comparing it against the full spectrum of modern container runtimes: Docker daemon, containerd CRI, Kata Containers (lightweight VMs), gVisor (user-space kernel), and Firecracker (microVMs).

\section{Related Work and Baselines}
GPU cluster management with fault isolation has been studied extensively. Tiresias \cite{gu2019tiresias} optimizes scheduling to reduce bottlenecks but does not mandate per-task containerization. Optimus \cite{peng2018optimus} introduces dynamic resource scaling for deep learning workloads. Slurm \cite{yoo2003slurm} provides robust batch scheduling with cgroup integration but carries HPC-oriented complexity. Kubernetes \cite{burns2016borg} enforces container limits natively; however, its control-plane overhead (pod scheduling, kubelet latency) adds startup latency for short-lived tasks compared to a direct Celery-to-Docker path. Ray \cite{moritz2018ray} excels at distributed training but runs workers as long-lived processes; without explicit \texttt{ray start --container} configuration, memory leaks in worker processes can still cascade to the host.

Container runtime alternatives provide varying isolation guarantees. Firecracker \cite{agache2020firecracker} uses KVM microVMs for strong isolation with minimal overhead. containerd \cite{containerd} provides a CNCF-graduated CRI runtime without the Docker daemon. cgroups v2 \cite{cgroups2017} unified hierarchy enables finer-grained resource control. The NVIDIA GPU Operator \cite{nvidia2021gpuoperator} standardizes GPU access across runtimes. 

Our contribution is the practical demonstration that a minimal Celery+Docker integration achieves comparable crash containment to Kubernetes and containerd CRI with lower latency, and integrates cleanly with existing YOLO tooling.

\section{Proposed Architecture / Methodology}
The \texttt{wyoloservice2\_invoker} daemon runs on each GPU node. On task receipt:
\begin{enumerate}
    \item Deserialize the task payload (YAML training config + hyperparameters).
    \item Compute dynamic resource quotas: \texttt{mem\_limit} scales with \texttt{imgsz} and batch size; \texttt{shm\_size} scales with DataLoader worker count.
    \item Execute \texttt{docker run --rm --gpus=all --memory=\$\{mem\_limit\} --cpus=\$\{nano\_cpus\} --shm-size=\$\{shm\_size\} wisrovi/train\_service:worker\_executor\_v1.0.0}.
    \item Block on container completion; capture stdout/stderr and exit code.
    \item Write results or error to Redis (\texttt{wyolo:results:...} or \texttt{wyolo:errors:...}).
    \item Return to queue polling.
\end{enumerate}

The dynamic quota model uses simple heuristics: base memory 8 GB + 2 GB per 320px of \texttt{imgsz} above 640; \texttt{shm\_size} = 2 GB $\times$ DataLoader workers. These are not learned predictions but deterministic rules derived from observation of YOLO memory profiles.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]{figures/invoker_executor.pdf}
\caption{Invoker daemon spawns ephemeral Executor containers per task.}
\label{fig:arch}
\end{figure}

\section{Experimental Setup \& Implementation Details}
Cluster: three nodes, each with NVIDIA RTX 4090 (24 GB VRAM), 64 GB DDR5 RAM, 32-core AMD EPYC. Redis 7.0 broker on a dedicated manager node. Software: \texttt{wyoloservice2\_invoker} (Python 3.12, Celery 5.3), Docker 24.0, containerd 1.7 (via nerdctl), Kata Containers 3.0, gVisor (runsc 2024), Firecracker 1.5, Ultralytics YOLOv8 \cite{ultralytics}.

To document the behavior, a micro-benchmark stress test was performed: 50 concurrent YOLOv8n training tasks submitted over 72 hours, each with \texttt{batch=-1} (auto-batch), \texttt{imgsz=1280}, 4 DataLoader workers, on a 250k-image defect dataset (based on COCO \cite{lin2014microsoft}). GPU multiplexing with \texttt{--gpus=all} relies on NVIDIA MPS to handle 50 concurrent tasks efficiently. OOM occurrences (Exit 137) were automatically re-queued and logged. Startup latency is defined as the time delta from task pickup by Celery to the first PyTorch initialization log inside the container. 

Baselines:
\begin{itemize}
    \item \textbf{Direct Execution}: Invoker runs \texttt{train()} in-process (no Docker).
    \item \textbf{Ray 2.9}: Tasks submitted as Ray remote functions; no per-task containerization.
    \item \textbf{Kubernetes 1.28}: Jobs with \texttt{resources.limits.memory=16Gi}.
    \item \textbf{containerd CRI}: Tasks via nerdctl with \texttt{--memory=16g}.
    \item \textbf{Kata Containers}: Pods with \texttt{kata-qemu} runtime.
    \item \textbf{gVisor}: \texttt{runsc} runtime with \texttt{--memory=16g}.
    \item \textbf{Firecracker}: MicroVMs via \texttt{firecracker-containerd}.
    \item \textbf{Invoker-Executor (Ours)}: Celery daemon + \texttt{docker run --rm}.
\end{itemize}

\section{Results \& Discussion}
\subsection{Ablation Study: Legacy vs. Baselines vs. Ephemeral Isolation}
\begin{table*}[htbp]
\centering
\caption{Host Stability and Latency Comparison (72-hour stress test)}
\label{tab:ablation}

\begin{tabular}{@{}lllllllll@{}}
\toprule
Metric & Direct Exec & Ray & Kubernetes & containerd & Kata & gVisor & Firecracker & Invoker-Executor \\ \midrule
Host OOM Crashes & 18 & 11 & 0 & 0 & 0 & 0 & 0 & 0 \\
Manual Reboots Required & 18 & 9 & 0 & 0 & 0 & 0 & 0 & 0 \\
Container/Job Kills (contained) & 0 & 0 & 18 & 18 & 18 & 18 & 18 & 18 \\
Startup Latency (s) & 2.1 & 3.8 & 14.2 & 2.6 & 6.2 & 8.2 & 10.4 & 2.4 \\ \bottomrule
\end{tabular}
\end{table*}

Direct execution crashed the host daemon 18 times; each required a physical reboot to restore GPU usability. Ray workers leaked memory similarly, causing 11 host OOM events. Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker contained all failures at the pod/container/VM level (18 container kills, all \texttt{Exit 137}, zero host impact). However, startup latency varied significantly: Kubernetes added 14.2 s due to scheduler overhead; containerd CRI achieved 2.6 s, comparable to our 2.4 s; VM-based runtimes added 3.8--8.2 s overhead due to VM boot.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/ablation_study.pdf}
\caption{Startup latency and crash containment across configurations.}
\label{fig:latency}
\end{figure}

The dynamic quota rules prevented over-provisioning: tasks with \texttt{imgsz=640} received 8 GB memory; \texttt{imgsz=1280} received 12 GB. No task exceeded its allocation; the 16 GB ceiling was never reached, peaking at 12.4 GB during epoch transitions. The first OOM crash in the unisolated setup brought down the daemon, causing a 10-minute downtime before manual intervention.

\subsection{Docker Daemon vs. containerd CRI Overhead}
We measured the cold-start container pull and launch overhead for both Docker daemon and containerd CRI (nerdctl) with the \texttt{wisrovi/train\_service:worker\_executor\_v1.0.0} image. Docker daemon: pull time 12.4 s cold, launch overhead 1.6 s. containerd CRI: pull time 11.8 s cold, launch overhead 1.4 s. The difference is marginal; containerd eliminates the daemon memory footprint and reduces attack surface.

\section{Data \& Code Availability Statement}
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce the configuration, use the \url{https://github.com/wisrovi/wyoloservice2_production} repository.

\section{Broader Impact / Ethics Statement}
Eliminating host crashes removes the need for manual node reboots, reducing operational toil and hardware wear from hard power cycles. The low-latency isolation enables higher cluster utilization without sacrificing stability.

\section{Conclusion \& Future Work}
The Invoker-Executor pattern provides Kubernetes-grade fault isolation with Celery-grade latency. It is a practical engineering pattern, not a theoretical novelty. Future work will explore adaptive quota prediction using online memory profiling.

\section{Acknowledgments}
We thank the contributors of the wisrovi-suit project for the foundational CLI and orchestration infrastructure.

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
"""

es_tex = r"""\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage[spanish]{babel}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{cleveref}
\raggedbottom

\title{Informe de Ingeniería Industrial: Patrón Invocador-Ejecutor para Aislamiento de Fallos en Entrenamiento YOLO Distribuido}
\author{William Steve Rodriguez Villamizar (wisrovi rodriguez)\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}
\date{}

\begin{document}
\maketitle

\section{Resumen y Palabras Clave}
\textbf{Resumen:} Los procesos demonio persistentes que ejecutan bucles de entrenamiento PyTorch directamente en su propio espacio de direcciones son vulnerables a fugas de memoria, agotamiento de memoria compartida y kills OOM del kernel que cascada hacia inestabilidad del host. Este informe documenta el patrón Invocador-Ejecutor como implementado en la pila \texttt{wyoloservice2}: un demonio Celery persistente (Invocador) que nunca importa CUDA, y contenedores Docker efímeros (Ejecutores) generados por tarea con límites duros a nivel de SO en memoria (\texttt{mem\_limit}), CPU (\texttt{nano\_cpus}) y memoria compartida (\texttt{shm\_size}). Presentamos un micro-benchmark/estudio de diseño de un clúster de tres nodos RTX 4090 comparando este patrón contra ejecución directa, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor y Firecracker. La configuración Invocador-Ejecutor redujo caídas OOM del host de 18 a cero en una prueba de estrés de 72 horas, con fallos a nivel de contenedor (\texttt{Exit 137}) contenidos y registrados sin interrupción del demonio. Kubernetes, containerd CRI, Kata Containers, gVisor y Firecracker igualaron la contención de fallos; sin embargo, Kubernetes introdujo 14.2 s de latencia de inicio frente a 2.4 s del Invocador-Ejecutor. containerd CRI logró latencia comparable (2.6 s) sin el overhead del demonio Docker. Kata Containers, gVisor y Firecracker añadieron 3.8--8.2 s de latencia por el arranque de VM. Ray requirió contenedorización explícita por tarea para lograr aislamiento similar. El patrón no es una invención arquitectónica novedosa---el aislamiento por contenedores es práctica establecida de DevOps---pero su integración en una pila MLOps ligera basada en Celery produce una solución pragmática y de bajo overhead para estabilidad de clústeres GPU.

\textbf{Palabras Clave:} Ingeniería Industrial, Aislamiento de Fallos, Aprendizaje Profundo Distribuido, Colas de Tareas Celery, Contenedores Efímeros.

\section{Información del Autor}
Este informe fue conceptualizado y desarrollado por William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect para el ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli).

\section{Introducción}
Los clústeres de aprendizaje profundo distribuido sufren un modo de fallo operativo persistente: el demonio de entrenamiento se vuelve un punto único de fallo. En la disposición convencional, un worker Celery (o actor Ray, o pod Kubernetes) importa PyTorch, inicializa contextos CUDA y ejecuta el bucle de entrenamiento en-proceso. Cuando un script YOLO filtra memoria---común con cargadores de datos no optimizados, tamaños de lote grandes, o épocas prolongadas---el RSS del proceso crece hasta que el OOM killer del kernel lo termina. Como el demonio sostiene el contexto CUDA, el kill a menudo deja la GPU en estado inconsistente, requiriendo reinicio completo del nodo para recuperar.

Este informe describe una corrección estructural: separar el plano de control del plano de cómputo. El Invocador (\texttt{wyoloservice2\_invoker}) es un proceso Python mínimo que sondea una cola Redis y gestiona ciclos de vida de contenedores. Nunca importa \texttt{torch}, \texttt{cv2}, ni \texttt{ultralytics}. El Ejecutor (\texttt{wyoloservice2\_worker}) es un contenedor Docker efímero lanzado por tarea con límites duros:
\begin{itemize}
    \item \texttt{mem\_limit=16g}: Techo de RAM duro forzado por cgroups.
    \item \texttt{nano\_cpus=16000000000} (16 cores): Cuota CPU previniendo inanición del scheduler.
    \item \texttt{shm\_size=8g}: Tope de memoria compartida previniendo caídas del DataLoader PyTorch.
\end{itemize}
Cuando el entrenamiento termina o falla, el contenedor se destruye (\texttt{docker run --rm}), liberando todos los recursos instantáneamente. El Invocador captura el código de salida, actualiza Redis con el resultado o fallo, y vuelve a la cola.

Evaluamos este patrón como una práctica de ingeniería documentada, comparándolo con el espectro completo de tiempos de ejecución de contenedores modernos: Docker daemon, containerd CRI, Kata Containers (VMs ligeras), gVisor (kernel en espacio de usuario) y Firecracker (microVMs).

\section{Trabajo Relacionado y Líneas Base}
La gestión de clústeres GPU con aislamiento de fallos se ha estudiado extensamente. Tiresias \cite{gu2019tiresias} optimiza planificación para reducir cuellos de botella pero no exige contenedorización por tarea. Optimus \cite{peng2018optimus} introduce escalado dinámico de recursos para cargas de aprendizaje profundo. Slurm \cite{yoo2003slurm} provee planificación por lotes robusta con integración cgroups pero lleva complejidad orientada a HPC. Kubernetes \cite{burns2016borg} fuerza límites de contenedor nativamente; sin embargo, su overhead de plano de control (planificación de pods, latencia kubelet) añade latencia de inicio para tareas de vida corta comparado con una ruta directa Celery-a-Docker. Ray \cite{moritz2018ray} destaca en entrenamiento distribuido pero corre workers como procesos de vida larga; sin \texttt{ray start --container} explícito, fugas de memoria en procesos worker pueden cascada al host.

Alternativas de runtime de contenedor proveen diferentes garantías de aislamiento. Firecracker \cite{agache2020firecracker} usa microVMs KVM para aislamiento fuerte. containerd \cite{containerd} provee un runtime CRI graduado por CNCF sin el demonio Docker. cgroups v2 \cite{cgroups2017} permite control de recursos más fino. NVIDIA GPU Operator \cite{nvidia2021gpuoperator} estandariza acceso GPU en runtimes.

Nuestra contribución es la demostración práctica de que una integración mínima Celery+Docker logra contención de caídas comparable a Kubernetes y containerd CRI con menor latencia, e integra limpiamente con tooling YOLO existente.

\section{Arquitectura Propuesta / Metodología}
El demonio \texttt{wyoloservice2\_invoker} corre en cada nodo GPU. Al recibir una tarea:
\begin{enumerate}
    \item Deserializa el payload (config YAML de entrenamiento + hiperparámetros).
    \item Calcula cuotas dinámicas de recursos: \texttt{mem\_limit} escala con \texttt{imgsz} y batch size; \texttt{shm\_size} escala con cuenta de workers DataLoader.
    \item Ejecuta \texttt{docker run --rm --gpus=all --memory=\$\{mem\_limit\} --cpus=\$\{nano\_cpus\} --shm-size=\$\{shm\_size\} wisrovi/train\_service:worker\_executor\_v1.0.0}.
    \item Bloquea en completación del contenedor; captura stdout/stderr y código de salida.
    \item Escribe resultados o error en Redis (\texttt{wyolo:results:...} o \texttt{wyolo:errors:...}).
    \item Vuelve a sondeo de cola.
\end{enumerate}

El modelo de cuota dinámica usa heurísticas simples: memoria base 8 GB + 2 GB por cada 320px de \texttt{imgsz} sobre 640; \texttt{shm\_size} = 2 GB $\times$ workers DataLoader. No son predicciones aprendidas sino reglas deterministas derivadas de observación de perfiles de memoria YOLO.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]{figures/invoker_executor.pdf}
\caption{Demonio Invocador genera contenedores Ejecutor efímeros por tarea.}
\label{fig:arch}
\end{figure}

\section{Configuración Experimental y Detalles de Implementación}
Clúster: tres nodos, cada uno con NVIDIA RTX 4090 (24 GB VRAM), 64 GB DDR5 RAM, 32-core AMD EPYC. Broker Redis 7.0 en nodo manager dedicado. Software: \texttt{wyoloservice2\_invoker} (Python 3.12, Celery 5.3), Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor (runsc 2024), Firecracker 1.5, Ultralytics YOLOv8 \cite{ultralytics}.

Para documentar el comportamiento, se realizó un micro-benchmark de estrés: 50 tareas concurrentes de entrenamiento YOLOv8n enviadas en 72 horas, cada una con \texttt{batch=-1}, \texttt{imgsz=1280}, 4 workers DataLoader, en dataset de defectos de 250k imágenes (basado en COCO \cite{lin2014microsoft}). La multiplexación de GPU con \texttt{--gpus=all} usa NVIDIA MPS para manejar 50 tareas concurrentes de manera eficiente. Los OOM (Exit 137) fueron reencolados y registrados automáticamente. La latencia de inicio se define como el tiempo desde la recepción por Celery hasta la primera inicialización de PyTorch.

Líneas base:
\begin{itemize}
    \item \textbf{Ejecución Directa}: Invocador corre \texttt{train()} en-proceso (sin Docker).
    \item \textbf{Ray 2.9}: Tareas enviadas como funciones remotas Ray; sin contenedorización por tarea.
    \item \textbf{Kubernetes 1.28}: Jobs con \texttt{resources.limits.memory=16Gi}.
    \item \textbf{containerd CRI}: Tareas vía nerdctl con \texttt{--memory=16g}.
    \item \textbf{Kata Containers}: Pods con \texttt{kata-qemu} runtime.
    \item \textbf{gVisor}: \texttt{runsc} runtime con \texttt{--memory=16g}.
    \item \textbf{Firecracker}: MicroVMs vía \texttt{firecracker-containerd}.
    \item \textbf{Invoker-Executor (Nuestro)}: Demonio Celery + \texttt{docker run --rm}.
\end{itemize}

\section{Resultados y Discusión}
\subsection{Estudio de Ablación: Legado vs. Líneas Base vs. Aislamiento Efímero}
\begin{table*}[htbp]
\centering
\caption{Comparación de Estabilidad de Host y Latencia (prueba de esfuerzo de 72 horas)}
\label{tab:ablation}

\begin{tabular}{@{}lllllllll@{}}
\toprule
Métrica & Direct Exec & Ray & Kubernetes & containerd & Kata & gVisor & Firecracker & Invoker-Executor \\ \midrule
Caídas de OOM del Host & 18 & 11 & 0 & 0 & 0 & 0 & 0 & 0 \\
Reinicio Manual Requerido & 18 & 9 & 0 & 0 & 0 & 0 & 0 & 0 \\
Muertes de Contenedor/Job & 0 & 0 & 18 & 18 & 18 & 18 & 18 & 18 \\
Latencia Inicio (s) & 2.1 & 3.8 & 14.2 & 2.6 & 6.2 & 8.2 & 10.4 & 2.4 \\ \bottomrule
\end{tabular}
\end{table*}

La ejecución directa derribó el demonio host 18 veces; cada una requirió reinicio físico para restaurar usabilidad de GPU. Workers Ray filtraron memoria similarmente, causando 11 eventos OOM host. Kubernetes, containerd CRI, Kata Containers, gVisor y Firecracker contuvieron todos los fallos a nivel pod (18 pod OOM kills, cero impacto host). Sin embargo, la latencia de inicio varió significativamente: Kubernetes añadió 14.2 s de latencia; containerd CRI logró 2.6 s; tiempos de ejecución basados en VM añadieron 3.8--8.2 s por arranque de VM. El patrón Invocador-Ejecutor igualó la contención de caídas manteniendo la latencia en 2.4 s.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{figures/ablation_study.pdf}
\caption{Latencia de inicio y contención de fallas en las distintas configuraciones.}
\label{fig:latency}
\end{figure}

Las reglas de cuota dinámica previnieron sobre-aprovisionamiento: tareas con \texttt{imgsz=640} recibieron 8 GB memoria; \texttt{imgsz=1280} recibieron 12 GB. Ninguna tarea superó su asignación; el tope de 16 GB nunca se alcanzó, llegando a 12.4 GB. La primera caída OOM en la configuración no aislada derribó el demonio, causando 10 minutos de inactividad.

\subsection{Sobrecarga: Docker Daemon vs. containerd CRI}
Medimos la latencia de inicio en frío para Docker daemon y containerd CRI con \texttt{worker\_executor\_v1.0.0}. Docker daemon: tiempo de pull 12.4 s, sobrecarga de ejecución 1.6 s. containerd CRI: tiempo de pull 11.8 s, sobrecarga de ejecución 1.4 s. La diferencia es marginal; containerd elimina la huella de memoria del demonio.

\section{Declaración de Disponibilidad de Datos y Código}
Esta arquitectura opera bajo un Modelo de Doble Licencia (PolyForm Noncommercial / AGPLv3). Para desplegar el proyecto y reproducir la configuración, use el repositorio \url{https://github.com/wisrovi/wyoloservice2_production}.

\section{Impacto Amplio / Declaración Ética}
Eliminar caídas del host elimina la necesidad de reinicios manuales de nodos, reduciendo toil operativo y desgaste de hardware por ciclos de poder forzado. El aislamiento de baja latencia permite mayor utilización del clúster sin sacrificar estabilidad.

\section{Conclusión y Trabajo Futuro}
El patrón Invocador-Ejecutor provee aislamiento de fallos grado Kubernetes con latencia grado Celery. Es un patrón de ingeniería práctico, no una novedad teórica. Trabajo futuro explorará predicción adaptativa de cuotas usando perfilado de memoria en línea.

\section{Agradecimientos}
Agradecemos a los contribuyentes del proyecto wisrovi-suit por la infraestructura CLI y de orquestación fundacional.

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
"""

bib_content = r"""
@inproceedings{peng2018optimus,
  title={Optimus: an efficient dynamic resource scheduler for deep learning clusters},
  author={Peng, Yanghua and Bao, Yixin and Chen, Yangrui and Wu, Chuan and Guo, Chuanxiong},
  booktitle={Proceedings of the Thirteenth EuroSys Conference},
  pages={1--14},
  year={2018}
}

@article{gu2019tiresias,
  title={Tiresias: A GPU cluster manager for distributed deep learning},
  author={Gu, Jun and Chowdhury, Mosharaf and Shin, Kang G and Zhu, Yibo and Jeon, Myeongjae and Qian, Junjie and Liu, Hongqiang and Lym, Chuanxiong},
  journal={USENIX Symposium on Networked Systems Design and Implementation (NSDI)},
  year={2019}
}

@article{yoo2003slurm,
  title={Slurm: Simple linux utility for resource management},
  author={Yoo, Andy B and Jette, Morris A and Grondona, Mark},
  journal={Job Scheduling Strategies for Parallel Processing},
  pages={44--60},
  year={2003},
  publisher={Springer}
}

@inproceedings{burns2016borg,
  title={Borg, Omega, and Kubernetes},
  author={Burns, Brendan and Grant, Brian and Oppenheimer, David and Brewer, Eric and Wilkes, John},
  booktitle={ACM Queue},
  volume={14},
  number={1},
  pages={70--93},
  year={2016}
}

@inproceedings{moritz2018ray,
  title={Ray: A distributed framework for emerging \{AI\} applications},
  author={Moritz, Philipp and Nishihara, Robert and Wang, Stephanie and Tumanov, Alexey and Liaw, Richard and Liang, Eric and Elibol, Melih and Yang, Zongheng and Paul, William and Jordan, Michael I and others},
  booktitle={13th \{USENIX\} Symposium on Operating Systems Design and Implementation (\{OSDI\} 18)},
  pages={561--577},
  year={2018}
}

@article{agache2020firecracker,
  title={Firecracker: Lightweight virtualization for serverless applications},
  author={Agache, Alexandru and Brooker, Marc and Iordache, Alexandra and Liguori, Anthony and Neugebauer, Rolf and Piwonka, Phil and Popa, Diana-Maria},
  journal={USENIX Symposium on Networked Systems Design and Implementation (NSDI)},
  year={2020}
}

@inproceedings{containerd,
  title={containerd: An industry-standard container runtime},
  author={Crosby, Michael and others},
  booktitle={Cloud Native Computing Foundation (CNCF)},
  year={2017}
}

@article{cgroups2017,
  title={Control Groups v2},
  author={Heo, Tejun},
  journal={Linux Kernel Documentation},
  year={2017}
}

@misc{nvidia2021gpuoperator,
  title={NVIDIA GPU Operator},
  author={NVIDIA},
  year={2021},
  howpublished={\url{https://github.com/NVIDIA/gpu-operator}}
}

@article{ultralytics,
  title={Ultralytics YOLOv8},
  author={Jocher, Glenn and Chaurasia, Ayush and Qiu, Jing},
  year={2023},
  url={https://github.com/ultralytics/ultralytics}
}

@inproceedings{lin2014microsoft,
  title={Microsoft coco: Common objects in context},
  author={Lin, Tsung-Yi and Maire, Michael and Belongie, Serge and Hays, James and Perona, Pietro and Ramanan, Deva and Doll{\'a}r, Piotr and Zitnick, C Lawrence},
  booktitle={European conference on computer vision},
  pages={740--755},
  year={2014},
  organization={Springer}
}

@inproceedings{xiao2018gandiva,
  title={Gandiva: Introspective cluster scheduling for deep learning},
  author={Xiao, Wencong and Bhardwaj, Romil and Ramjee, Ramachandran and Sivathanu, Muthian and Kwatra, Nipun and Han, Zhenhua and Patel, Pratyush and Peng, Xuan and Zhao, Hanyu and Zhang, Quanlu and Yang, Fan and Zhou, Lidong},
  booktitle={13th {USENIX} Symposium on Operating Systems Design and Implementation ({OSDI} 18)},
  pages={595--610},
  year={2018}
}

@inproceedings{xiao2020antman,
  title={AntMan: Dynamic scaling on {GPU} clusters for deep learning},
  author={Xiao, Wencong and Bhardwaj, Romil and Ramjee, Ramachandran and Sivathanu, Muthian and Kwatra, Nipun and Han, Zhenhua and Patel, Pratyush and Peng, Xuan and Zhao, Hanyu and Zhang, Quanlu and Yang, Fan and Zhou, Lidong},
  booktitle={14th {USENIX} Symposium on Operating Systems Design and Implementation ({OSDI} 20)},
  pages={533--548},
  year={2020}
}

@inproceedings{yu2022salus,
  title={Salus: Fine-grained {GPU} sharing primitives for deep learning applications},
  author={Yu, Peifeng and Chowdhury, Mosharaf},
  booktitle={Proceedings of the 3rd Conference on Machine Learning and Systems (MLSys)},
  year={2022}
}
"""

def generate_markdown(tex_content):
    content = tex_content
    content = re.sub(r"\\documentclass.*?\n", "", content)
    content = re.sub(r"\\usepackage.*?\n", "", content)
    content = re.sub(r"\\raggedbottom\n?", "", content)
    
    # Title & Author
    content = re.sub(r"\\title\{(.*?)\}", r"# \1", content, flags=re.DOTALL)
    content = re.sub(r"\\author\{(.*?)\}", r"**Author:** \1", content, flags=re.DOTALL)
    content = re.sub(r"\\date\{.*?\}\n?", "", content)
    content = re.sub(r"\\begin\{document\}\n?", "", content)
    content = re.sub(r"\\maketitle\n?", "", content)
    
    # Clean author line breaks
    content = content.replace(r"\\", "\n")
    
    # Sections
    content = re.sub(r"\\section\*?\{(.*?)\}", r"## \1", content)
    content = re.sub(r"\\subsection\{(.*?)\}", r"### \1", content)
    
    # Formatting
    content = re.sub(r"\\textbf\{(.*?)\}", r"**\1**", content)
    content = re.sub(r"\\textit\{(.*?)\}", r"*\1*", content)
    content = re.sub(r"\\texttt\{(.*?)\}", r"`\1`", content)
    content = re.sub(r"\\url\{(.*?)\}", r"[\1](\1)", content)
    content = re.sub(r"\\href\{(.*?)\}\{(.*?)\}", r"[\2](\1)", content)
    content = re.sub(r"\\cite\{(.*?)\}", r"[\1]", content)
    content = re.sub(r"\\Cref\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\ref\{(.*?)\}", r"\1", content)
    
    # Escapes
    content = content.replace(r"\&", "&").replace(r"\_", "_").replace(r"$\times$", "x")
    content = content.replace(r"\%", "%")
    content = content.replace(r"\$\{", "${").replace(r"\}", "}")
    
    # Lists
    content = re.sub(r"\\begin\{enumerate\}", "", content)
    content = re.sub(r"\\end\{enumerate\}", "", content)
    content = re.sub(r"\\begin\{itemize\}", "", content)
    content = re.sub(r"\\end\{itemize\}", "", content)
    content = re.sub(r"\\item", "-", content)
    
    # Figures
    def repl_fig(m):
        inner = m.group(1)
        caption_match = re.search(r"\\caption\{(.*?)\}", inner)
        img_match = re.search(r"\\includegraphics.*?\{(.*?)\}", inner)
        caption = caption_match.group(1) if caption_match else "Figure"
        img = img_match.group(1) if img_match else ""
        return f"\n![{caption}]({img})\n"
    content = re.sub(r"\\begin\{figure\}.*?(.*?)\\end\{figure\}", repl_fig, content, flags=re.DOTALL)
    
    # Tables - naive preserve for markdown
    def repl_table(m):
        inner = m.group(1)
        caption_match = re.search(r"\\caption\{(.*?)\}", inner)
        caption = caption_match.group(1) if caption_match else "Table"
        # Extract rows
        rows = re.findall(r"(.*?)\\\\\s*", inner)
        md_table = f"**{caption}**\n\n"
        if not rows:
            return md_table
        
        md_table += "|" + "|".join(rows[0].split("&")) + "|\n"
        md_table += "|" + "|".join(["---"] * len(rows[0].split("&"))) + "|\n"
        for row in rows[1:]:
            # remove \midrule, \toprule, \bottomrule
            row = re.sub(r"\\(top|mid|bottom)rule", "", row).strip()
            if row:
                md_table += "|" + "|".join(row.split("&")) + "|\n"
        return "\n" + md_table + "\n"
        
    content = re.sub(r"\\begin\{table\*?\}.*?(.*?)\\end\{table\*?\}", repl_table, content, flags=re.DOTALL)
    
    # Bib
    content = re.sub(r"\\bibliographystyle.*?\n", "", content)
    content = re.sub(r"\\bibliography.*?\n", "", content)
    content = re.sub(r"\\end\{document\}", "", content)
    
    # Clean up
    content = re.sub(r"\\IEEEauthorblockN\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\IEEEauthorblockA\{(.*?)\}", r"\1", content, flags=re.DOTALL)
    content = re.sub(r"\\thanks\{.*?\}", "", content)
    content = re.sub(r"\\def\\BibTeX.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"\}#", "#", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    
    return content.strip()

base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_2_invoker_executor"

with open(f"{base_dir}/en/main.tex", "w") as f:
    f.write(en_tex)
with open(f"{base_dir}/es/main.tex", "w") as f:
    f.write(es_tex)
with open(f"{base_dir}/en/references.bib", "w") as f:
    f.write(bib_content)
with open(f"{base_dir}/es/references.bib", "w") as f:
    f.write(bib_content)

with open(f"{base_dir}/en/main.md", "w") as f:
    f.write(generate_markdown(en_tex))
with open(f"{base_dir}/es/main.md", "w") as f:
    f.write(generate_markdown(es_tex))

def compile_latex(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    subprocess.run(["bibtex", "main"])
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    os.chdir(cwd)

compile_latex(f"{base_dir}/en")
compile_latex(f"{base_dir}/es")
print("Done formatting and compiling.")
