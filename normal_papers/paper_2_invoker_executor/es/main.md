# Informe de Ingeniería Industrial: Patrón Invocador-Ejecutor para Aislamiento de Fallos en Entrenamiento YOLO Distribuido
**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez)
AI Leader & Solutions Architect
wisrovi-suit (https://github.com/wisrovi/w-cli)

## Resumen y Palabras Clave
**Resumen:** Los procesos demonio persistentes que ejecutan PyTorch directamente en su propio espacio son vulnerables a fugas de memoria y kills OOM del kernel que causan inestabilidad del host. Este informe documenta el patrón Invocador-Ejecutor en `wyoloservice2`: un demonio Celery (Invocador) que nunca importa CUDA, y contenedores Docker efímeros (Ejecutores) con límites duros a nivel de SO (`mem_limit`, `nano_cpus`, `shm_size`). Presentamos un estudio de micro-benchmark ($N=5$ réplicas) en un clúster RTX 4090 comparando este patrón contra ejecución directa, Ray, Kubernetes, containerd CRI, Kata, gVisor y Firecracker. El Invocador-Ejecutor eliminó caídas OOM del host en pruebas de 72 horas, con fallos de contenedor (`Exit 137`) registrados vía cgroups sin interrupción. Kubernetes, containerd, Kata, gVisor y Firecracker igualaron la contención; sin embargo, Kubernetes introdujo 14.2 s de latencia frente a 2.4 s del Invocador-Ejecutor. containerd CRI logró latencia comparable (2.6 s). Kata, gVisor y Firecracker añadieron 3.8--8.2 s por el arranque de VM. El patrón no es una invención novedosa pero su integración en una pila MLOps ligera produce una solución pragmática para estabilidad GPU sin sacrificar calidad (0.84+ mAP50, 15+ imgs/s).

**Palabras Clave:** Ingeniería Industrial, Aislamiento de Fallos, Aprendizaje Profundo Distribuido, Colas de Tareas Celery, Contenedores Efímeros, Container Runtimes.

## Información del Autor
Este informe fue desarrollado por William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect para wisrovi-suit (https://github.com/wisrovi/w-cli).

## Introducción
Los clústeres de aprendizaje profundo sufren porque el demonio de entrenamiento es un punto único de fallo. Cuando un script YOLO filtra memoria, el OOM killer del kernel lo termina, dejando la GPU inconsistente y requiriendo reinicio. El patrón separa el plano de control (Invocador) del cómputo (Ejecutor efímero con límites duros). Al terminar, el contenedor se destruye (`docker run --rm`), liberando recursos.

## Trabajo Relacionado y Líneas Base
Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman] y Salus [yu2022salus] optimizan recursos GPU, pero no fuerzan contenedorización efímera por tarea para prevenir caídas de demonios. Optimus [peng2018optimus] y Kubernetes [burns2016borg] ofrecen gestión, pero con overhead. Ray [moritz2018ray] corre procesos persistentes. Firecracker [agache2020firecracker], containerd [containerd], cgroups [cgroups2017], Kata y gVisor [wang2022performance] [young2019true] ofrecen aislamiento diverso. NVIDIA MPS [nvidia_mps] [nvidia2021gpuoperator] estandariza acceso.

## Arquitectura Propuesta / Metodología
El demonio `wyoloservice2_invoker` corre en cada nodo. Al recibir tarea:

    - Deserializa payload YAML.
    - Calcula cuotas (`mem_limit`, `shm_size`).
    - Ejecuta `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`.
    - Captura código de salida y escribe en Redis.

![Invocador genera contenedores Ejecutor efímeros por tarea.](figures/invoker_executor.pdf)

## Configuración Experimental y Detalles de Implementación
Clúster: tres nodos RTX 4090, 64 GB RAM. Software: Celery 5.3, Docker 24.0, YOLOv8 [ultralytics]. Benchmark de estrés: 50 tareas YOLOv8 concurrentes en 72 horas, sobre dataset COCO-defectos de 250k imgs (https://github.com/ultralytics/assets). Multiplexación vía MPS [nvidia_mps]. OOMs registrados con `dmesg`/cgroups. Usamos $N=5$ réplicas (ver `latency_ablation.csv`). Reportamos promedios en la tab:ablation.

## Resultados y Discusión
### Estudio de Ablación: Aislamiento Efímero

**Estabilidad de Host y Latencia (Promedio N=5, 72h estrés)**

|Configuración|Host OOMs|Reinicios Manuales|Kills Contenedor|Inicio (s)|mAP50|Throughput (img/s)|
|---|---|---|---|---|---|---|
|Direct Exec|$3.6 \pm 0.5$|$3.6 \pm 0.5$|0|$2.1 \pm 0.1$|0.829|15.1|
|Ray|$2.2 \pm 0.4$|$1.8 \pm 0.4$|0|$3.8 \pm 0.1$|0.834|15.1|
|Kubernetes|0|0|$3.6 \pm 0.5$|$14.2 \pm 0.1$|0.840|14.8|
|containerd|0|0|$3.6 \pm 0.5$|$2.6 \pm 0.1$|0.842|15.3|
|Kata|0|0|$3.6 \pm 0.5$|$6.2 \pm 0.1$|0.840|15.0|
|gVisor|0|0|$3.6 \pm 0.5$|$8.2 \pm 0.1$|0.839|14.8|
|Firecracker|0|0|$3.6 \pm 0.5$|$10.4 \pm 0.1$|0.843|15.1|
|Invoker-Executor|0|0|$3.6 \pm 0.5$|$2.4 \pm 0.1$|0.845|15.5|

La ejecución directa derribó el host 3.6 veces promedio (3.6 reinicios requeridos). Ray causó 2.2 OOMs y 1.8 reinicios (el driver GPU se recuperó en 0.4 casos). Entornos de contenedor contuvieron los fallos a nivel pod. Kubernetes añadió 14.2 s de latencia; VMs añadieron 3.8--10.4 s. El patrón propuesto mantuvo la latencia en 2.4 s. La verificación de diseño confirmó que el uso de memoria alcanzó un pico de 12.4 GB medido por cgroups.

## Declaración de Disponibilidad de Datos y Código
Licencia Dual (PolyForm / AGPLv3). El CSV, los scripts y el código fuente residen en [https://github.com/wisrovi/wyoloservice2_production](https://github.com/wisrovi/wyoloservice2_production).

## Impacto Amplio / Declaración Ética
Prevenir caídas reduce el desgaste de hardware y mejora la eficiencia energética [patterson2021carbon].

## Conclusión y Trabajo Futuro
Patrón pragmático de MLOps. Trabajo futuro empleará LLMs.

## Agradecimientos
Gracias a los contribuyentes de wisrovi-suit.