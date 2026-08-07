# The Invoker-Executor Pattern: Mitigating Hardware Monopolization and Memory Leaks in Large-Scale Distributed Deep Learning

## Abstract
Los cuellos de botella clásicos en PyTorch/YOLO (procesos zombis, fugas de memoria, mala gestión de memoria compartida) pueden colapsar clústeres enteros de GPU. Este paper presenta la arquitectura "Invoker-Celery", que utiliza contenedores efímeros Docker (Executors) con límites estrictos de hardware (`nano_cpus`, `mem_limit`, `shm_size`) para garantizar el aislamiento físico y lógico durante optimizaciones a gran escala.

## 1. Introduction
El entrenamiento profundo distribuido es susceptible a la degradación del nodo anfitrión a lo largo del tiempo. Presentamos un enfoque de desacoplamiento que delega la orquestación (Invoker) a un demonio persistente, mientras que la carga de trabajo se confina en contenedores desechables (Executor).

## 2. Related Work
- **Tiresias: A GPU Cluster Manager for Distributed Deep Learning (Gu et al., 2019):** Gestión eficiente de clústeres GPU y scheduling optimizado para evitar cuellos de botella.
- **Transparent GPU Sharing in Container Clouds for Deep Learning Workloads (2023/2024):** Operaciones a nivel de SO para compartir GPUs de manera segura entre contenedores Docker/Kubernetes y evitar memory leaks.
- **CarbonEdge: Carbon-Aware Edge Scheduling for Distributed Inference in Containerized Environments (2024/2025):** Planificación en entornos distribuidos contenerizados.

## 3. Invoker-Executor Architecture
Se describe la separación entre la cola de Celery (`wyoloservice2_invoker`) y el contenedor de entrenamiento (`wyoloservice2_worker`).

## 4. Conclusion
El aislamiento mediante el patrón Invoker-Executor elimina la necesidad de reinicios físicos y garantiza una estabilidad operativa cercana al 100%.
