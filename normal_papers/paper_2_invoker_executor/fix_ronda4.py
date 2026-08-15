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
\author{William Steve Rodriguez Villamizar (wisrovi rodriguez) \href{https://orcid.org/0000-0002-4740-9734}{\includegraphics[width=0.03\textwidth]{figures/orcid.pdf}}\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}
\date{}

\begin{document}
\maketitle

\section{Abstract \& Keywords}
\textbf{Abstract:} Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents an observational design study of the Invoker-Executor pattern as implemented in the \texttt{wyoloservice2} stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (\texttt{mem\_limit}), CPU (\texttt{nano\_cpus}), and shared memory (\texttt{shm\_size}). We qualitatively compare this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration successfully contained memory leaks over our production observations, logging failures via cgroups events without daemon interruption. The pattern is not a novel architectural invention, but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

\textbf{Keywords:} Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

\section{Author Information}
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

\section{Introduction}
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (\texttt{wyoloservice2\_invoker}) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports \texttt{torch} or \texttt{ultralytics}. The Executor (\texttt{wyoloservice2\_worker}) is an ephemeral Docker container launched per task with hard limits enforced by cgroups. When the training finishes or crashes, the container is destroyed (\texttt{docker run --rm}), instantly releasing all resources.

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

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]{figures/invoker_executor.pdf}
\caption{Invoker daemon spawns ephemeral Executor containers per task.}
\label{fig:arch}
\end{figure}

\section{Observational Design Study}
Cluster: three nodes, each with NVIDIA RTX 4090, 64 GB DDR5 RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 \cite{ultralytics}. GPU multiplexing uses NVIDIA MPS \cite{nvidia_mps}. OOM events (Exit 137) were qualitatively registered via \texttt{dmesg} and cgroups kernel events during production usage.

\section{Results \& Discussion}
\subsection{Qualitative Observations: Legacy vs. Ephemeral Isolation}

In our observational study, direct execution periodically crashed the host daemon due to memory exhaustion, often requiring a physical reboot due to corrupted GPU states. Ray workers exhibited similar issues, occasionally allowing the GPU driver to recover autonomously. 

Containerized runtimes contained all failures (Exit 137, zero host impact). While Kubernetes offers robust limits natively, its control-plane added noticeable latency in launching pods compared to the lightweight daemon. VM-based runtimes like Kata, gVisor, and Firecracker provided strong security boundaries but introduced significant boot overhead. 

The Invoker-Executor pattern achieved crash containment comparable to Kubernetes and microVMs while maintaining a minimal startup profile, as it merely executes Docker CLI commands outside of a heavy orchestration plane. The dynamic quota cap effectively contained tasks, with cgroups memory usage logs confirming that outliers were killed via \texttt{OOMKilled} without affecting the host Invoker process.

\section{Data \& Code Availability Statement}
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Generation scripts and code are available at \url{https://github.com/wisrovi/wyoloservice2_production}.

\section{Broader Impact / Ethics Statement}
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency \cite{patterson2021carbon}.

\section{Conclusion \& Future Work}
The pattern provides robust fault isolation for YOLO training pipelines. Future work will explore online memory profiling via LLM agents.

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
\author{William Steve Rodriguez Villamizar (wisrovi rodriguez) \href{https://orcid.org/0000-0002-4740-9734}{\includegraphics[width=0.03\textwidth]{figures/orcid.pdf}}\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}
\date{}

\begin{document}
\maketitle

\section{Resumen y Palabras Clave}
\textbf{Resumen:} Los procesos demonio persistentes que ejecutan PyTorch directamente en su propio espacio son vulnerables a fugas de memoria y kills OOM del kernel que causan inestabilidad del host. Este informe documenta un estudio observacional de diseño del patrón Invocador-Ejecutor en \texttt{wyoloservice2}: un demonio Celery (Invocador) que nunca importa CUDA, y contenedores Docker efímeros (Ejecutores) con límites duros a nivel de SO (\texttt{mem\_limit}, \texttt{nano\_cpus}, \texttt{shm\_size}). Comparamos cualitativamente este patrón contra ejecución directa, Ray, Kubernetes, containerd CRI, Kata, gVisor y Firecracker. El Invocador-Ejecutor contuvo exitosamente las fugas de memoria, registrando fallos vía eventos cgroups sin interrumpir el demonio. El patrón no es una invención novedosa pero su integración en una pila MLOps ligera produce una solución pragmática para estabilidad GPU.

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

\section{Estudio Observacional de Diseño}
Clúster: tres nodos RTX 4090, 64 GB RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 \cite{ultralytics}. Multiplexación vía MPS \cite{nvidia_mps}. OOMs cualitativamente registrados con \texttt{dmesg}/cgroups. 

\section{Resultados y Discusión}
\subsection{Observaciones Cualitativas: Aislamiento Efímero}

En nuestro estudio observacional, la ejecución directa causó inestabilidad del demonio host y requirió reinicios. Entornos de contenedor contuvieron los fallos a nivel pod. Kubernetes añadió latencia notable; VMs también añadieron overhead de inicio. El patrón propuesto mantuvo la latencia baja ya que delega directamente al CLI de Docker. La verificación de diseño confirmó que el uso de memoria fue contenido exitosamente vía cgroups.

\section{Declaración de Disponibilidad de Datos y Código}
Licencia Dual (PolyForm / AGPLv3). Los scripts y el código fuente residen en \url{https://github.com/wisrovi/wyoloservice2_production}.

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

def generate_markdown(tex_content):
    content = tex_content
    content = re.sub(r"\\documentclass.*?\n", "", content)
    content = re.sub(r"\\usepackage.*?\n", "", content)
    content = re.sub(r"\\raggedbottom\n?", "", content)
    
    content = re.sub(r"\\title\{(.*?)\}", r"# \1", content, flags=re.DOTALL)
    
    def repl_author(m):
        author_text = m.group(1).replace(r"\\", "\n")
        author_text = re.sub(r"\\href\{.*?\}\{\\includegraphics.*?\}", "", author_text)
        return "**Author:** " + author_text
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
