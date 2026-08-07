# The Invoker-Executor Pattern: Mitigating Hardware Monopolization and Memory Leaks in Large-Scale Distributed Deep Learning

## Abstract
Classic bottlenecks in PyTorch/YOLO (zombie processes, memory leaks, poor shared memory management) can crash entire GPU clusters. This paper presents the "Invoker-Celery" architecture, which uses ephemeral Docker containers (Executors) with strict hardware limits (`nano_cpus`, `mem_limit`, `shm_size`) to guarantee physical and logical isolation during large-scale optimizations.

## 1. Introduction
Distributed deep training is susceptible to host node degradation over time. We present a decoupling approach that delegates orchestration (Invoker) to a persistent daemon, while confining the workload to disposable containers (Executor).

## 2. Related Work
- **Tiresias: A GPU Cluster Manager for Distributed Deep Learning (Gu et al., 2019):** Efficient management of GPU clusters and optimized scheduling to prevent bottlenecks.
- **Transparent GPU Sharing in Container Clouds for Deep Learning Workloads (2023/2024):** OS-level operations to securely share GPUs across Docker/Kubernetes containers and avoid memory leaks.
- **CarbonEdge: Carbon-Aware Edge Scheduling for Distributed Inference in Containerized Environments (2024/2025):** Scheduling in distributed containerized environments.

## 3. Invoker-Executor Architecture
We describe the separation between the Celery queue (`wyoloservice2_invoker`) and the training container (`wyoloservice2_worker`).

## 4. Conclusion
Isolation through the Invoker-Executor pattern eliminates the need for physical reboots and guarantees near 100% operational stability.
