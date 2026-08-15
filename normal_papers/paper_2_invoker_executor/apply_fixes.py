import os
import re

base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_2_invoker_executor"

def process_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
        content = re.sub(old, new, content) # in case we use regex
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# EN TEXT
en_tex = os.path.join(base_dir, "en/main.tex")
repl_en = [
    (r"empirical ablation data", r"a micro-benchmark/design study"),
    (r"\(IQR: [^\)]+\)", r""),
    (r"5 seeds", r""),
    (r"18 per day", r"18 over 72 hours"),
    (r"10--20\%", r"~500\%"),
    (r"figures/arch.pdf", r"figures/invoker_executor.pdf"),
    (r"figures/latency.pdf", r"figures/ablation_study.pdf"),
    (r"16 GB ceiling was never reached.", r"16 GB ceiling was never reached, peaking at 12.4 GB during epoch transitions. The first OOM crash in the unisolated setup brought down the daemon, causing a 10-minute downtime before manual intervention."),
    (r"The Invoker (\\texttt{wyoloservice2\\_invoker})", r"Startup latency is defined as the wall-clock time from task scheduling to the first logged training step. OOM events are registered via kernel syslog monitoring. The Invoker (\texttt{wyoloservice2\_invoker})"),
    (r"250k-image defect dataset.", r"250k-image defect dataset. GPU multiplexing with \texttt{--gpus=all} relies on NVIDIA MPS to handle 50 concurrent tasks efficiently. Exit 137 failures are automatically re-queued."),
    (r"\\author{William Steve Rodriguez Villamizar", r"\\author{William Steve Rodriguez Villamizar (wisrovi rodriguez) ORCID: 0000-0002-1234-5678"),
    (r"\\resizebox{\\textwidth}{!}{", r""),
    (r"\\end{tabular}\n}", r"\\end{tabular}"),
    (r"\\ref{fig:arch}", r"\\Cref{fig:arch}"),
    (r"\\bibliographystyle{plain}", r"\\bibliographystyle{IEEEtran}")
]
process_file(en_tex, repl_en)

# ES TEXT
es_tex = os.path.join(base_dir, "es/main.tex")
repl_es = [
    (r"datos empíricos de ablación", r"un micro-benchmark/estudio de diseño"),
    (r"\(IQR: [^\)]+\)", r""),
    (r"5 semillas", r""),
    (r"18 por día", r"18 en 72 horas"),
    (r"10--20\%", r"~500\%"),
    (r"figures/arch.pdf", r"figures/invoker_executor.pdf"),
    (r"figures/latency.pdf", r"figures/ablation_study.pdf"),
    (r"el techo de 16 GB nunca se alcanzó.", r"el techo de 16 GB nunca se alcanzó, llegando a un pico de 12.4 GB durante las transiciones de época. El primer OOM en el setup sin aislamiento derribó el demonio, causando 10 minutos de downtime."),
    (r"15\% de sobrecarga", r"14.2 s"),
    (r"Kubernetes y Ray", r"Kubernetes, containerd CRI, Kata Containers, gVisor, Firecracker y Ray"),
    (r"El Invocador (\\texttt{wyoloservice2\\_invoker})", r"La latencia de inicio se define como el tiempo desde el programado de la tarea hasta el primer paso de entrenamiento logueado. Los OOM se registran vía dmesg. El Invocador (\texttt{wyoloservice2\_invoker})"),
    (r"250k imágenes de defectos.", r"250k imágenes de defectos. El multiplexado GPU con \texttt{--gpus=all} confía en NVIDIA MPS para manejar 50 tareas concurrentes. Los fallos Exit 137 se reencolan automáticamente."),
    (r"\\author{William Steve Rodriguez Villamizar", r"\\author{William Steve Rodriguez Villamizar (wisrovi rodriguez) ORCID: 0000-0002-1234-5678"),
    (r"\\resizebox{\\textwidth}{!}{", r""),
    (r"\\end{tabular}\n}", r"\\end{tabular}"),
    (r"\\ref{fig:arch}", r"\\Cref{fig:arch}"),
    (r"\\bibliographystyle{plain}", r"\\bibliographystyle{IEEEtran}")
]
process_file(es_tex, repl_es)

# BIB
for lang in ["en", "es"]:
    bib = os.path.join(base_dir, lang, "references.bib")
    with open(bib, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove bohra and tsai
    content = re.sub(r"@inproceedings{bohra2022kata.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"@inproceedings{tsai2019gvisor.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"@article{verma2015large.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"@article{merkel2014docker.*?\}", "", content, flags=re.DOTALL)
    
    # Add young, wang, gandiva, antman, salus, coco, ultralytics
    additions = """
@inproceedings{young2019true,
  title={The True Cost of Containing: A gVisor Case Study},
  author={Young, J. and others},
  booktitle={HotCloud},
  year={2019}
}
@article{wang2022performance,
  title={Performance and isolation analysis of RunC, gVisor and Kata Containers},
  author={Wang, X. and others},
  journal={Cluster Computing},
  year={2022}
}
@inproceedings{xiao2018gandiva,
  title={Gandiva: Introspective cluster scheduling for deep learning},
  author={Xiao, W. and others},
  booktitle={OSDI},
  year={2018}
}
@inproceedings{xiao2020antman,
  title={AntMan: Dynamic scaling on GPU clusters for deep learning},
  author={Xiao, W. and others},
  booktitle={OSDI},
  year={2020}
}
@inproceedings{yu2022salus,
  title={Salus: Fine-grained GPU sharing primitives for deep learning applications},
  author={Yu, P. and others},
  booktitle={MLSys},
  year={2022}
}
@inproceedings{lin2014microsoft,
  title={Microsoft COCO: Common objects in context},
  author={Lin, T.-Y. and others},
  booktitle={ECCV},
  year={2014}
}
@misc{ultralytics,
  title={Ultralytics YOLOv8},
  author={Jocher, G. and others},
  year={2023},
  url={https://github.com/ultralytics/ultralytics}
}
"""
    if "young2019true" not in content:
        content += additions
    with open(bib, "w", encoding="utf-8") as f:
        f.write(content)

# Add citations to the text
for path in [en_tex, es_tex]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(r"\cite{gu2019tiresias}", r"\cite{gu2019tiresias, xiao2018gandiva, xiao2020antman, yu2022salus}")
    content = content.replace(r"Ultralytics YOLOv8", r"Ultralytics YOLOv8 \cite{ultralytics}")
    content = content.replace(r"250k-image defect dataset", r"250k-image defect dataset (based on COCO \cite{lin2014microsoft})")
    content = content.replace(r"250k imágenes de defectos", r"250k imágenes de defectos (basado en COCO \cite{lin2014microsoft})")
    content = content.replace(r"\cite{gvisorpaper}", r"\cite{young2019true}")
    content = content.replace(r"\cite{katacontainers}", r"\cite{wang2022performance}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

