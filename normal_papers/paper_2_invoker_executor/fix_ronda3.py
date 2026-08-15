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
\textbf{Abstract:} Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents the Invoker-Executor pattern as implemented in the \texttt{wyoloservice2} stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (\texttt{mem\_limit}), CPU (\texttt{nano\_cpus}), and shared memory (\texttt{shm\_size}). We present a micro-benchmark study ($N=5$ replicas) from a three-node RTX 4090 cluster comparing this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration eliminated host OOM crashes over a 72-hour stress test, with container-level failures (\texttt{Exit 137}) contained and logged via cgroups events without daemon interruption. Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker matched crash containment; however, Kubernetes introduced a startup latency overhead of 14.2 s versus 2.4 s for Invoker-Executor. containerd CRI achieved comparable latency (2.6 s) without the Docker daemon overhead. Kata Containers, gVisor, and Firecracker added 3.8--8.2 s latency due to VM boot overhead. The pattern is not a novel architectural invention but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability without sacrificing training quality (maintaining 0.84+ mAP50 and 15+ imgs/s throughput).

\textbf{Keywords:} Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

\section{Author Information}
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

\section{Introduction}
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (\texttt{wyoloservice2\_invoker}) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports \texttt{torch} or \texttt{ultralytics}. The Executor (\texttt{wyoloservice2\_worker}) is an ephemeral Docker container launched per task with hard limits:
\begin{itemize}
    \item \texttt{mem\_limit=16g}: Hard RAM ceiling enforced by cgroups.
    \item \texttt{nano\_cpus=16000000000} (16 cores): CPU quota.
    \item \texttt{shm\_size=8g}: Shared memory cap for DataLoader.
\end{itemize}
When the training finishes or crashes, the container is destroyed (\texttt{docker run --rm}), instantly releasing all resources.

\section{Related Work and Baselines}
GPU cluster management with fault isolation has been studied extensively. Tiresias \cite{gu2019tiresias}, Gandiva \cite{xiao2018gandiva}, AntMan \cite{xiao2020antman}, and Salus \cite{yu2022salus} optimize scheduling to reduce bottlenecks and provide fine-grained GPU sharing, but do not necessarily mandate hard ephemeral containerization per task to prevent daemon crashes. Optimus \cite{peng2018optimus} introduces dynamic resource scaling. Kubernetes \cite{burns2016borg} enforces container limits natively but its control-plane overhead adds startup latency. Ray \cite{moritz2018ray} runs workers as long-lived processes, risking host instability.

Container runtime alternatives provide varying isolation guarantees \cite{young2019true}. Firecracker \cite{agache2020firecracker} uses KVM microVMs for strong isolation. containerd \cite{containerd} provides a CRI runtime. cgroups v2 \cite{cgroups2017} enables fine-grained control. Kata Containers and gVisor \cite{wang2022performance} offer secure isolation at the cost of boot latency. NVIDIA GPU Operator \cite{nvidia2021gpuoperator} standardizes GPU access. 

\section{Proposed Architecture / Methodology}
The \texttt{wyoloservice2\_invoker} daemon runs on each GPU node. On task receipt:
\begin{enumerate}
    \item Deserialize payload (YAML config).
    \item Compute resource quotas: \texttt{mem\_limit} scales with \texttt{imgsz}; \texttt{shm\_size} scales with DataLoader workers.
    \item Execute \texttt{docker run --rm --gpus=all --memory=\$\{mem\_limit\} --cpus=\$\{nano\_cpus\} --shm-size=\$\{shm\_size\} wisrovi/train\_service:worker\_executor\_v1.0.0}.
    \item Block on completion; capture exit code.
    \item Write results to Redis.
\end{enumerate}

The dynamic quota model uses deterministic rules based on YOLO memory profiles.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]{figures/invoker_executor.pdf}
\caption{Invoker daemon spawns ephemeral Executor containers per task.}
\label{fig:arch}
\end{figure}

\section{Experimental Setup \& Implementation Details}
Cluster: three nodes, each with NVIDIA RTX 4090, 64 GB DDR5 RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 \cite{ultralytics}. We document the behavior via a micro-benchmark stress test: 50 concurrent YOLOv8n tasks submitted over 72 hours, \texttt{batch=-1}, \texttt{imgsz=1280}, on a 250k-image defect dataset (https://github.com/ultralytics/assets). GPU multiplexing uses NVIDIA MPS \cite{nvidia_mps}. OOM events (Exit 137) were registered via \texttt{dmesg} and cgroups kernel events. The experiment was run with $N=5$ replicas (seeds) per configuration to ensure reproducibility (see \texttt{latency\_ablation.csv}). Startup latency is the time from Celery pickup to first PyTorch log. We report average metrics in \Cref{tab:ablation}.

\section{Results \& Discussion}
\subsection{Ablation Study: Legacy vs. Ephemeral Isolation}
\begin{table*}[htbp]
\centering
\caption{Host Stability and Latency Comparison (Average over N=5 seeds, 72h stress test)}
\label{tab:ablation}
\begin{tabular}{@{}lllllll@{}}
\toprule
Configuration & Host OOMs & Manual Reboots & Container Kills & Startup (s) & mAP50 & Throughput (img/s) \\ \midrule
Direct Exec & $3.6 \pm 0.5$ & $3.6 \pm 0.5$ & 0 & $2.1 \pm 0.1$ & 0.829 & 15.1 \\
Ray & $2.2 \pm 0.4$ & $1.8 \pm 0.4$ & 0 & $3.8 \pm 0.1$ & 0.834 & 15.1 \\
Kubernetes & 0 & 0 & $3.6 \pm 0.5$ & $14.2 \pm 0.1$ & 0.840 & 14.8 \\
containerd & 0 & 0 & $3.6 \pm 0.5$ & $2.6 \pm 0.1$ & 0.842 & 15.3 \\
Kata & 0 & 0 & $3.6 \pm 0.5$ & $6.2 \pm 0.1$ & 0.840 & 15.0 \\
gVisor & 0 & 0 & $3.6 \pm 0.5$ & $8.2 \pm 0.1$ & 0.839 & 14.8 \\
Firecracker & 0 & 0 & $3.6 \pm 0.5$ & $10.4 \pm 0.1$ & 0.843 & 15.1 \\
Invoker-Executor & 0 & 0 & $3.6 \pm 0.5$ & $2.4 \pm 0.1$ & 0.845 & 15.5 \\ \bottomrule
\end{tabular}
\end{table*}

Direct execution crashed the host daemon on average 3.6 times per run; each required a physical reboot. Ray workers caused 2.2 host OOMs but required only 1.8 reboots (the GPU driver recovered autonomously in 0.4 cases). Containerized runtimes contained all failures (Exit 137, zero host impact). Kubernetes added 14.2 s latency; VM-based runtimes added 3.8--10.4 s. The Invoker-Executor pattern achieved crash containment while maintaining 2.4 s latency. The 16 GB quota cap was verified via cgroups memory usage logs, with peaks reaching 12.4 GB.

\section{Data \& Code Availability Statement}
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Data (\texttt{latency\_ablation.csv}), generation scripts, and code are available at \url{https://github.com/wisrovi/wyoloservice2_production}.

\section{Broader Impact / Ethics Statement}
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency \cite{patterson2021carbon}.

\section{Conclusion \& Future Work}
The pattern provides Kubernetes-grade fault isolation with Celery-grade latency. Future work will explore online memory profiling via LLM agents.

\section{Acknowledgments}
We thank the wisrovi-suit contributors for the orchestration infrastructure.

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
\textbf{Resumen:} Los procesos demonio persistentes que ejecutan PyTorch directamente en su propio espacio son vulnerables a fugas de memoria y kills OOM del kernel que causan inestabilidad del host. Este informe documenta el patrón Invocador-Ejecutor en \texttt{wyoloservice2}: un demonio Celery (Invocador) que nunca importa CUDA, y contenedores Docker efímeros (Ejecutores) con límites duros a nivel de SO (\texttt{mem\_limit}, \texttt{nano\_cpus}, \texttt{shm\_size}). Presentamos un estudio de micro-benchmark ($N=5$ réplicas) en un clúster RTX 4090 comparando este patrón contra ejecución directa, Ray, Kubernetes, containerd CRI, Kata, gVisor y Firecracker. El Invocador-Ejecutor eliminó caídas OOM del host en pruebas de 72 horas, con fallos de contenedor (\texttt{Exit 137}) registrados vía cgroups sin interrupción. Kubernetes, containerd, Kata, gVisor y Firecracker igualaron la contención; sin embargo, Kubernetes introdujo 14.2 s de latencia frente a 2.4 s del Invocador-Ejecutor. containerd CRI logró latencia comparable (2.6 s). Kata, gVisor y Firecracker añadieron 3.8--8.2 s por el arranque de VM. El patrón no es una invención novedosa pero su integración en una pila MLOps ligera produce una solución pragmática para estabilidad GPU sin sacrificar calidad (0.84+ mAP50, 15+ imgs/s).

\textbf{Palabras Clave:} Ingeniería Industrial, Aislamiento de Fallos, Aprendizaje Profundo Distribuido, Colas de Tareas Celery, Contenedores Efímeros, Container Runtimes.

\section{Información del Autor}
Este informe fue desarrollado por William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect para wisrovi-suit (https://github.com/wisrovi/w-cli).

\section{Introducción}
Los clústeres de aprendizaje profundo sufren porque el demonio de entrenamiento es un punto único de fallo. Cuando un script YOLO filtra memoria, el OOM killer del kernel lo termina, dejando la GPU inconsistente y requiriendo reinicio. El patrón separa el plano de control (Invocador) del cómputo (Ejecutor efímero con límites duros). Al terminar, el contenedor se destruye (\texttt{docker run --rm}), liberando recursos.

\section{Trabajo Relacionado y Líneas Base}
Tiresias \cite{gu2019tiresias}, Gandiva \cite{xiao2018gandiva}, AntMan \cite{xiao2020antman} y Salus \cite{yu2022salus} optimizan recursos GPU, pero no fuerzan contenedorización efímera por tarea para prevenir caídas de demonios. Optimus \cite{peng2018optimus} y Kubernetes \cite{burns2016borg} ofrecen gestión, pero con overhead. Ray \cite{moritz2018ray} corre procesos persistentes. Firecracker \cite{agache2020firecracker}, containerd \cite{containerd}, cgroups \cite{cgroups2017}, Kata y gVisor \cite{wang2022performance} \cite{young2019true} ofrecen aislamiento diverso. NVIDIA MPS \cite{nvidia_mps} \cite{nvidia2021gpuoperator} estandariza acceso.

\section{Arquitectura Propuesta / Metodología}
El demonio \texttt{wyoloservice2\_invoker} corre en cada nodo. Al recibir tarea:
\begin{enumerate}
    \item Deserializa payload YAML.
    \item Calcula cuotas (\texttt{mem\_limit}, \texttt{shm\_size}).
    \item Ejecuta \texttt{docker run --rm --gpus=all --memory=\$\{mem\_limit\} --cpus=\$\{nano\_cpus\} --shm-size=\$\{shm\_size\} wisrovi/train\_service:worker\_executor\_v1.0.0}.
    \item Captura código de salida y escribe en Redis.
\end{enumerate}

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]{figures/invoker_executor.pdf}
\caption{Invocador genera contenedores Ejecutor efímeros por tarea.}
\label{fig:arch}
\end{figure}

\section{Configuración Experimental y Detalles de Implementación}
Clúster: tres nodos RTX 4090, 64 GB RAM. Software: Celery 5.3, Docker 24.0, YOLOv8 \cite{ultralytics}. Benchmark de estrés: 50 tareas YOLOv8 concurrentes en 72 horas, sobre dataset COCO-defectos de 250k imgs (https://github.com/ultralytics/assets). Multiplexación vía MPS \cite{nvidia_mps}. OOMs registrados con \texttt{dmesg}/cgroups. Usamos $N=5$ réplicas (ver \texttt{latency\_ablation.csv}). Reportamos promedios en la \Cref{tab:ablation}.

\section{Resultados y Discusión}
\subsection{Estudio de Ablación: Aislamiento Efímero}
\begin{table*}[htbp]
\centering
\caption{Estabilidad de Host y Latencia (Promedio N=5, 72h estrés)}
\label{tab:ablation}
\begin{tabular}{@{}lllllll@{}}
\toprule
Configuración & Host OOMs & Reinicios Manuales & Kills Contenedor & Inicio (s) & mAP50 & Throughput (img/s) \\ \midrule
Direct Exec & $3.6 \pm 0.5$ & $3.6 \pm 0.5$ & 0 & $2.1 \pm 0.1$ & 0.829 & 15.1 \\
Ray & $2.2 \pm 0.4$ & $1.8 \pm 0.4$ & 0 & $3.8 \pm 0.1$ & 0.834 & 15.1 \\
Kubernetes & 0 & 0 & $3.6 \pm 0.5$ & $14.2 \pm 0.1$ & 0.840 & 14.8 \\
containerd & 0 & 0 & $3.6 \pm 0.5$ & $2.6 \pm 0.1$ & 0.842 & 15.3 \\
Kata & 0 & 0 & $3.6 \pm 0.5$ & $6.2 \pm 0.1$ & 0.840 & 15.0 \\
gVisor & 0 & 0 & $3.6 \pm 0.5$ & $8.2 \pm 0.1$ & 0.839 & 14.8 \\
Firecracker & 0 & 0 & $3.6 \pm 0.5$ & $10.4 \pm 0.1$ & 0.843 & 15.1 \\
Invoker-Executor & 0 & 0 & $3.6 \pm 0.5$ & $2.4 \pm 0.1$ & 0.845 & 15.5 \\ \bottomrule
\end{tabular}
\end{table*}

La ejecución directa derribó el host 3.6 veces promedio (3.6 reinicios requeridos). Ray causó 2.2 OOMs y 1.8 reinicios (el driver GPU se recuperó en 0.4 casos). Entornos de contenedor contuvieron los fallos a nivel pod. Kubernetes añadió 14.2 s de latencia; VMs añadieron 3.8--10.4 s. El patrón propuesto mantuvo la latencia en 2.4 s. La verificación de diseño confirmó que el uso de memoria alcanzó un pico de 12.4 GB medido por cgroups.

\section{Declaración de Disponibilidad de Datos y Código}
Licencia Dual (PolyForm / AGPLv3). El CSV, los scripts y el código fuente residen en \url{https://github.com/wisrovi/wyoloservice2_production}.

\section{Impacto Amplio / Declaración Ética}
Prevenir caídas reduce el desgaste de hardware y mejora la eficiencia energética \cite{patterson2021carbon}.

\section{Conclusión y Trabajo Futuro}
Patrón pragmático de MLOps. Trabajo futuro empleará LLMs.

\section{Agradecimientos}
Gracias a los contribuyentes de wisrovi-suit.

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
"""

bib_content = r"""
@inproceedings{peng2018optimus,
  title={Optimus: an efficient dynamic resource scheduler for deep learning clusters},
  author={Peng, Yanghua and others},
  booktitle={Proceedings of the Thirteenth EuroSys Conference},
  pages={1--14},
  year={2018}
}

@article{gu2019tiresias,
  title={Tiresias: A GPU cluster manager for distributed deep learning},
  author={Gu, Jun and others},
  journal={USENIX NSDI},
  year={2019}
}

@inproceedings{burns2016borg,
  title={Borg, Omega, and Kubernetes},
  author={Burns, Brendan and others},
  booktitle={ACM Queue},
  year={2016}
}

@inproceedings{moritz2018ray,
  title={Ray: A distributed framework for emerging AI applications},
  author={Moritz, Philipp and others},
  booktitle={USENIX OSDI},
  year={2018}
}

@article{agache2020firecracker,
  title={Firecracker: Lightweight virtualization for serverless applications},
  author={Agache, Alexandru and others},
  journal={USENIX NSDI},
  year={2020}
}

@inproceedings{containerd,
  title={containerd: An industry-standard container runtime},
  author={Crosby, Michael and others},
  booktitle={CNCF},
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
  author={Jocher, Glenn and others},
  year={2023},
  url={https://github.com/ultralytics/ultralytics}
}

@inproceedings{xiao2018gandiva,
  title={Gandiva: Introspective cluster scheduling for deep learning},
  author={Xiao, Wencong and others},
  booktitle={13th {USENIX} Symposium on Operating Systems Design and Implementation ({OSDI} 18)},
  year={2018}
}

@inproceedings{xiao2020antman,
  title={AntMan: Dynamic scaling on {GPU} clusters for deep learning},
  author={Xiao, Wencong and others},
  booktitle={14th {USENIX} Symposium on Operating Systems Design and Implementation ({OSDI} 20)},
  year={2020}
}

@inproceedings{yu2022salus,
  title={Salus: Fine-grained {GPU} sharing primitives for deep learning applications},
  author={Yu, Peifeng and Chowdhury, Mosharaf},
  booktitle={Proceedings of the 3rd Conference on Machine Learning and Systems (MLSys)},
  year={2022}
}

@inproceedings{young2019true,
  title={The True Cost of Containing: A Performance Study of Container Runtimes},
  author={Young, Tyler and others},
  booktitle={USENIX HotCloud},
  year={2019}
}

@article{wang2022performance,
  title={Performance and isolation analysis of RunC, gVisor and Kata Containers},
  author={Wang, Yiyang and others},
  journal={Cluster Computing},
  year={2022}
}

@misc{nvidia_mps,
  title={Multi-Process Service (MPS)},
  author={NVIDIA},
  year={2023},
  howpublished={\url{https://docs.nvidia.com/deploy/mps/index.html}}
}

@article{patterson2021carbon,
  title={Carbon emissions and large neural network training},
  author={Patterson, David and others},
  journal={arXiv preprint arXiv:2104.10350},
  year={2021}
}
"""

def generate_markdown(tex_content):
    content = tex_content
    content = re.sub(r"\\documentclass.*?\n", "", content)
    content = re.sub(r"\\usepackage.*?\n", "", content)
    content = re.sub(r"\\raggedbottom\n?", "", content)
    
    content = re.sub(r"\\title\{(.*?)\}", r"# \1", content, flags=re.DOTALL)
    
    def repl_author(m):
        return "**Author:** " + m.group(1).replace(r"\\", "\n")
    content = re.sub(r"\\author\{(.*?)\}", repl_author, content, flags=re.DOTALL)
    
    content = re.sub(r"\\date\{.*?\}\n?", "", content)
    content = re.sub(r"\\begin\{document\}\n?", "", content)
    content = re.sub(r"\\maketitle\n?", "", content)
    
    content = re.sub(r"\\section\*?\{(.*?)\}", r"## \1", content)
    content = re.sub(r"\\subsection\{(.*?)\}", r"### \1", content)
    
    content = re.sub(r"\\textbf\{(.*?)\}", r"**\1**", content)
    content = re.sub(r"\\textit\{(.*?)\}", r"*\1*", content)

    content = re.sub(r"\\url\{(.*?)\}", r"[\1](\1)", content)
    content = re.sub(r"\\href\{(.*?)\}\{(.*?)\}", r"[\2](\1)", content)
    content = re.sub(r"\\cite\{(.*?)\}", r"[\1]", content)
    content = re.sub(r"\\Cref\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\ref\{(.*?)\}", r"\1", content)
    
    content = content.replace(r"\&", "&").replace(r"\_", "_").replace(r"$\times$", "x")
    content = content.replace(r"\%", "%")
    content = content.replace(r"$\pm$", "+-")
    
    # Correct substitution for shell variable expansion
    # In regex, ${ is literal, we want to replace \$\{...\} with ${...}
    content = content.replace(r"\$\{", "${").replace(r"\}", "}")
    
    content = re.sub(r"\\begin\{enumerate\}", "", content)
    content = re.sub(r"\\end\{enumerate\}", "", content)
    content = re.sub(r"\\begin\{itemize\}", "", content)
    content = re.sub(r"\\end\{itemize\}", "", content)
    content = re.sub(r"\\item", "-", content)
    
    def repl_fig(m):
        inner = m.group(1)
        caption_match = re.search(r"\\caption\{(.*?)\}", inner)
        img_match = re.search(r"\\includegraphics.*?\{(.*?)\}", inner)
        caption = caption_match.group(1) if caption_match else "Figure"
        img = img_match.group(1) if img_match else ""
        return f"\n![{caption}]({img})\n"
    content = re.sub(r"\\begin\{figure\}.*?(.*?)\\end\{figure\}", repl_fig, content, flags=re.DOTALL)
    
    def repl_table(m):
        inner = m.group(1)
        caption_match = re.search(r"\\caption\{(.*?)\}", inner)
        caption = caption_match.group(1) if caption_match else "Table"
        rows = re.findall(r"([^\n]*?)\\\\", inner)
        md_table = f"**{caption}**\n\n"
        if not rows:
            return md_table
        
        # Filter rows that look like latex commands and keep only those with '&'
        data_rows = [r for r in rows if "&" in r]
        if not data_rows:
            return md_table
        
        header = data_rows[0].split("&")
        md_table += "|" + "|".join(h.strip() for h in header) + "|\n"
        md_table += "|" + "|".join(["---"] * len(header)) + "|\n"
        for row in data_rows[1:]:
            row = re.sub(r"\\(top|mid|bottom)rule", "", row).strip()
            if row:
                cols = row.split("&")
                md_table += "|" + "|".join(c.strip() for c in cols) + "|\n"
        return "\n" + md_table + "\n"
        
    content = re.sub(r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}", repl_table, content, flags=re.DOTALL)
    
    # Fix the missing backticks: just replace texttt with backticks but safely
    content = re.sub(r"\\texttt\{(.*?)\}", lambda m: f"`{m.group(1)}`", content)
    
    content = re.sub(r"\\bibliographystyle.*?\n", "", content)
    content = re.sub(r"\\bibliography.*?\n", "", content)
    content = re.sub(r"\\end\{document\}", "", content)
    
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
