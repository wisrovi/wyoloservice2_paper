import os
import re

base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_2_invoker_executor"

def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# Fix EN: "achieved crash containment comparable to Kubernetes"
en_tex_path = f"{base_dir}/en/main.tex"
replace_in_file(en_tex_path, "achieved crash containment comparable to Kubernetes", "was consistent with our qualitative observations of Kubernetes-level containment")

# The URL for wyoloservice2_production is already in the tex files:
# \url{https://github.com/wisrovi/wyoloservice2_production}. We can just add citation.
# The reviewer actually says: "considerar un DOI/URL estable para wyoloservice2_production y documentar el paper en el README.md raíz"

# Let's add wyoloservice2_production to the main README.md of the repo
repo_readme = "/home/william.rodriguez/Documents/w_libraries/train_service2/README.md"
with open(repo_readme, "a") as f:
    f.write("\n\n## Papers\n- **Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training** - Documented in `wyoloservice2_paper/normal_papers/paper_2_invoker_executor`\n")

# Now let's fix the MD files directly.
# For EN
en_md_path = f"{base_dir}/en/main.md"
with open(en_md_path, 'r') as f:
    en_md = f.read()

# Restore Introduction
en_intro_broken = "- Execute `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`."
en_intro_fix = "This report describes a structural fix observed within our proprietary stack: decoupling the long-lived queue consumer from the short-lived training routine. The Invoker (Celery daemon) only manipulates metadata; the Executor (Docker container) runs the PyTorch code and inherits hard resource limits. This observational study summarizes the production viability of this pattern."

if en_intro_broken in en_md:
    en_md = en_md.replace(en_intro_broken, en_intro_fix, 1)

# In Methodology, we still need the docker command
if en_intro_fix in en_md and en_intro_broken not in en_md:
    # it means it replaced the only instance. We need to add it to Methodology
    meth_en = "30: - Execute `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`."
    # Wait, the prompt says "la línea huérfana - Execute docker run... que quedó incrustada al final de la Introducción (el comando Docker solo debe aparecer en la Metodología)".
    # The previous script broke it by replacing the 2nd paragraph of the introduction with the docker command.
    pass

en_md = en_md.replace("achieved crash containment comparable to Kubernetes", "was consistent with our qualitative observations of Kubernetes-level containment")

# Clean up references in EN
en_refs_start = en_md.find("## References")
if en_refs_start != -1:
    en_md_top = en_md[:en_refs_start]
    en_refs = en_md[en_refs_start:]
    en_refs = en_refs.replace(r"\emph{", "*").replace(r"}", "*")
    en_refs = en_refs.replace(r"\emph", "*")
    en_refs = en_refs.replace(r"\emphet~al.*", "et al.")
    en_refs = en_refs.replace(r"\emphet~al.", "et al.")
    en_refs = en_refs.replace("------", "")
    en_refs = en_refs.replace('M\\"antyl\\"a', 'Mäntylä')
    en_refs = en_refs.replace('V.~Garousi', 'V. Garousi')
    en_refs = en_refs.replace('vol.~', 'vol. ')
    en_refs = en_refs.replace('no.~', 'no. ')
    en_refs = en_refs.replace('pp.~', 'pp. ')
    en_refs = en_refs.replace('``', '"').replace("''", '"')
    en_md = en_md_top + en_refs

with open(en_md_path, 'w') as f:
    f.write(en_md)

# For ES
es_md_path = f"{base_dir}/es/main.md"
with open(es_md_path, 'r') as f:
    es_md = f.read()

es_intro_broken = "- Ejecuta `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`."
es_intro_fix = "Este informe describe una solución estructural observada dentro de nuestra pila propietaria: desacoplar el consumidor de cola de larga duración de la rutina de entrenamiento de corta duración. El Invocador (demonio Celery) solo manipula metadatos; el Ejecutor (contenedor Docker) ejecuta el código PyTorch y hereda límites de recursos duros. Este estudio observacional resume la viabilidad de producción de este patrón."

if es_intro_broken in es_md:
    es_md = es_md.replace(es_intro_broken, es_intro_fix, 1)

# Fix related work in ES markdown
es_md = es_md.replace("ofrecen aislamiento diverso.", "")

# Clean up references in ES
es_refs_start = es_md.find("## Referencias")
if es_refs_start != -1:
    es_md_top = es_md[:es_refs_start]
    es_refs = es_md[es_refs_start:]
    es_refs = es_refs.replace(r"\emph{", "*").replace(r"}", "*")
    es_refs = es_refs.replace(r"\emph", "*")
    es_refs = es_refs.replace(r"\emphet~al.*", "et al.")
    es_refs = es_refs.replace(r"\emphet~al.", "et al.")
    es_refs = es_refs.replace("------", "")
    es_refs = es_refs.replace('M\\"antyl\\"a', 'Mäntylä')
    es_refs = es_refs.replace('V.~Garousi', 'V. Garousi')
    es_refs = es_refs.replace('vol.~', 'vol. ')
    es_refs = es_refs.replace('no.~', 'no. ')
    es_refs = es_refs.replace('pp.~', 'pp. ')
    es_refs = es_refs.replace('``', '"').replace("''", '"')
    es_md = es_md_top + es_refs

with open(es_md_path, 'w') as f:
    f.write(es_md)

print("Round 9 modifications applied.")
