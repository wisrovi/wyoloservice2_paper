# Informe de Ingeniería Industrial: Patrón Invocador-Ejecutor para Aislamiento de Fallos en Entrenamiento YOLO Distribuido
**Author:**
William Steve Rodriguez Villamizar (wisrovi rodriguez) \href{https://orcid.org/0000-0002-4740-9734{\includegraphics[width=0.03\textwidth]{figures/orcid.pdf}}\\AI Leader & Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}

## Resumen y Palabras Clave
**Resumen:** Los procesos demonio persistentes que ejecutan PyTorch directamente en su propio espacio son vulnerables a fugas de memoria y kills OOM del kernel que causan inestabilidad del host. Este informe de experiencia industrial [garousi2016need] documenta un estudio observacional de diseño del patrón Invocador-Ejecutor en `wyoloservice2`: un demonio Celery (Invocador) que nunca importa CUDA, y contenedores Docker efímeros (Ejecutores) con límites duros a nivel de SO (`mem_limit`, `nano_cpus`, `shm_size`). Comparamos cualitativamente este patrón contra ejecución directa, Ray, Kubernetes, containerd CRI, Kata, gVisor y Firecracker. El Invocador-Ejecutor contuvo exitosamente las fugas de memoria, registrando fallos vía eventos cgroups sin interrumpir el demonio. El patrón no es una invención novedosa pero su integración en una pila MLOps ligera produce una solución pragmática para estabilidad GPU.

**Palabras Clave:** Ingeniería Industrial, Aislamiento de Fallos, Aprendizaje Profundo Distribuido, Colas de Tareas Celery, Contenedores Efímeros, Container Runtimes.

## Información del Autor
Este informe fue desarrollado por William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect para wisrovi-suit (https://github.com/wisrovi/w-cli).

## Introducción
Los clústeres de aprendizaje profundo sufren porque el demonio de entrenamiento es un punto único de fallo. Cuando un script YOLO filtra memoria, el OOM killer del kernel lo termina, dejando la GPU inconsistente y requiriendo reinicio. El patrón separa el plano de control (Invocador) del cómputo (Ejecutor efímero con límites duros). Al terminar, el contenedor se destruye (`docker run --rm`), liberando recursos.

## Trabajo Relacionado y Líneas Base
Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman] y Salus [yu2022salus] optimizan recursos GPU, pero no fuerzan contenedorización efímera por tarea para prevenir caídas de demonios. Optimus [peng2018optimus] y Kubernetes [burns2016borg] ofrecen gestión, pero con overhead. Ray [moritz2018ray] corre procesos persistentes. Firecracker [agache2020firecracker], containerd [containerd], cgroups [cgroups2017], Kata Containers y gVisor [wang2022performance] ofrecen aislamiento seguro a costa de la latencia de arranque [young2019true] ofrecen aislamiento diverso. NVIDIA GPU Operator [nvidia2021gpuoperator] estandariza acceso.

## Arquitectura Propuesta / Metodología
El demonio `wyoloservice2_invoker` corre en cada nodo. Al recibir tarea:

    - Deserializa payload YAML.
    - Calcula cuotas (`mem_limit`, `shm_size`).
    - Ejecuta `docker run --rm --gpus=all --memory=${mem_limit` --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0}.
    - Captura código de salida y escribe en Redis.

![Invocador genera contenedores Ejecutor efímeros por tarea.](figures/invoker_executor.pdf)

## Estudio Observacional de Diseño
Clúster: tres nodos RTX 4090, 64 GB RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 [ultralytics]. Multiplexación vía MPS [nvidia_mps]. OOMs cualitativamente registrados con `dmesg`/cgroups. 

## Resultados y Discusión
### Observaciones Cualitativas: Aislamiento Efímero

En nuestro estudio observacional, la ejecución directa causó inestabilidad del demonio host y requirió reinicios. Durante una ventana observacional de 14 días y aproximadamente 1,500 tareas de entrenamiento, Ray causó inestabilidad pero permitió que el driver de GPU se recuperara de forma autónoma en algunas ocasiones. Los entornos de contenedor aislaron los fallos cualitativamente, permitiendo que tareas individuales fallaran sin afectar aparentemente al demonio host. Kubernetes añadió latencia notable; VMs también añadieron overhead de inicio. El patrón propuesto mantuvo la latencia baja ya que delega directamente al CLI de Docker. La verificación de diseño confirmó que el uso de memoria atípico típicamente resultó en la terminación vía `OOMKilled`, lo que generalmente evitó una cascada de inestabilidad en el proceso Invocador host.

## Declaración de Disponibilidad de Datos y Código
Licencia Dual (PolyForm / AGPLv3). Los scripts y el código fuente residen en [https://github.com/wisrovi/wyoloservice2_production](https://github.com/wisrovi/wyoloservice2_production).

## Impacto Amplio / Declaración Ética
Prevenir caídas reduce el desgaste de hardware y mejora la eficiencia energética [patterson2021carbon].

## Conclusión y Trabajo Futuro
Patrón pragmático de MLOps. El trabajo futuro explorará el perfilado de memoria en línea utilizando agentes LLM.

## Agradecimientos
Gracias a los contribuyentes de wisrovi-suit.


## References

[1] V.~Garousi, M.~Felderer, and M.~V. M"antyl"a, ``The need for empirical evidence in software engineering,'' \emphIEEE Software, vol.~33, no.~1, pp. 68-75, 2016.

[2] J.~Gu \emphet~al., ``Tiresias: A gpu cluster manager for distributed deep learning,'' \emphUSENIX NSDI, 2019.

[3] W.~Xiao \emphet~al., ``Gandiva: Introspective cluster scheduling for deep learning,'' in \emph13th USENIX Symposium on Operating Systems Design and Implementation (OSDI 18), 2018.

[4] -, ``Antman: Dynamic scaling on GPU clusters for deep learning,'' in \emph14th USENIX Symposium on Operating Systems Design and Implementation (OSDI 20), 2020.

[5] P.~Yu and M.~Chowdhury, ``Salus: Fine-grained GPU sharing primitives for deep learning applications,'' in \emphProceedings of the 3rd Conference on Machine Learning and Systems (MLSys), 2022.

[6] Y.~Peng \emphet~al., ``Optimus: an efficient dynamic resource scheduler for deep learning clusters,'' in \emphProceedings of the Thirteenth EuroSys Conference, 2018, pp. 1-14.

[7] B.~Burns \emphet~al., ``Borg, omega, and kubernetes,'' in \emphACM Queue, 2016.

[8] P.~Moritz \emphet~al., ``Ray: A distributed framework for emerging ai applications,'' in \emphUSENIX OSDI, 2018.

[9] A.~Agache \emphet~al., ``Firecracker: Lightweight virtualization for serverless applications,'' \emphUSENIX NSDI, 2020.

[10] M.~Crosby \emphet~al., ``containerd: An industry-standard container runtime,'' in \emphCNCF, 2017.

[11] T.~Heo, ``Control groups v2,'' \emphLinux Kernel Documentation, 2017.

[12] Y.~Wang \emphet~al., ``Performance and isolation analysis of runc, gvisor and kata containers,'' \emphCluster Computing, 2022.

[13] T.~Young \emphet~al., ``The true cost of containing: A performance study of container runtimes,'' in \emphUSENIX HotCloud, 2019.

[14] NVIDIA, ``Nvidia gpu operator,'' https://github.com/NVIDIA/gpu-operator, 2021.

[15]  G.~Jocher \emphet~al., ``Ultralytics yolov8,'' 2023. [Online]. Available: https://github.com/ultralytics/ultralytics 

[16] NVIDIA, ``Multi-process service (mps),'' https://docs.nvidia.com/deploy/mps/index.html, 2023.

[17] D.~Patterson \emphet~al., ``Carbon emissions and large neural network training,'' \empharXiv preprint arXiv:2104.10350, 2021.