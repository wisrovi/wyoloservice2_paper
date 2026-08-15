# Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training
**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) \href{https://orcid.org/0000-0002-4740-9734{\includegraphics[width=0.03\textwidth]{figures/orcid.pdf}}\\AI Leader & Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)}

## Abstract & Keywords
**Abstract:** Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents an observational design study of the Invoker-Executor pattern as implemented in the `wyoloservice2` stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (`mem_limit`), CPU (`nano_cpus`), and shared memory (`shm_size`). We qualitatively compare this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration successfully contained memory leaks over our production observations, logging failures via cgroups events without daemon interruption. The pattern is not a novel architectural invention, but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

**Keywords:** Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

## Author Information
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (`wyoloservice2_invoker`) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports `torch` or `ultralytics`. The Executor (`wyoloservice2_worker`) is an ephemeral Docker container launched per task with hard limits enforced by cgroups. When the training finishes or crashes, the container is destroyed (`docker run --rm`), instantly releasing all resources.

## Related Work and Baselines
GPU cluster management with fault isolation has been studied extensively. Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman], and Salus [yu2022salus] optimize scheduling to reduce bottlenecks and provide fine-grained GPU sharing, but do not necessarily mandate hard ephemeral containerization per task to prevent daemon crashes. Optimus [peng2018optimus] introduces dynamic resource scaling. Kubernetes [burns2016borg] enforces container limits natively but its control-plane overhead adds startup latency. Ray [moritz2018ray] runs workers as long-lived processes, risking host instability.

Container runtime alternatives provide varying isolation guarantees [young2019true]. Firecracker [agache2020firecracker] uses KVM microVMs for strong isolation. containerd [containerd] provides a CRI runtime. cgroups v2 [cgroups2017] enables fine-grained control. Kata Containers and gVisor [wang2022performance] offer secure isolation at the cost of boot latency. NVIDIA GPU Operator [nvidia2021gpuoperator] standardizes GPU access. 

## Proposed Architecture / Methodology
The `wyoloservice2_invoker` daemon runs on each GPU node. On task receipt:

    - Deserialize payload (YAML config).
    - Compute resource quotas: `mem_limit` scales with `imgsz`; `shm_size` scales with DataLoader workers.
    - Execute `docker run --rm --gpus=all --memory=${mem_limit` --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0}.
    - Block on completion; capture exit code.
    - Write results to Redis.

![Invoker daemon spawns ephemeral Executor containers per task.](figures/invoker_executor.pdf)

## Observational Design Study
Cluster: three nodes, each with NVIDIA RTX 4090, 64 GB DDR5 RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 [ultralytics]. GPU multiplexing uses NVIDIA MPS [nvidia_mps]. OOM events (Exit 137) were qualitatively registered via `dmesg` and cgroups kernel events during production usage.

## Results & Discussion
### Qualitative Observations: Legacy vs. Ephemeral Isolation

In our observational study, direct execution periodically crashed the host daemon due to memory exhaustion, often requiring a physical reboot due to corrupted GPU states. Ray workers exhibited similar issues, occasionally allowing the GPU driver to recover autonomously. 

Containerized runtimes contained all failures (Exit 137, zero host impact). While Kubernetes offers robust limits natively, its control-plane added noticeable latency in launching pods compared to the lightweight daemon. VM-based runtimes like Kata, gVisor, and Firecracker provided strong security boundaries but introduced significant boot overhead. 

The Invoker-Executor pattern achieved crash containment comparable to Kubernetes and microVMs while maintaining a minimal startup profile, as it merely executes Docker CLI commands outside of a heavy orchestration plane. The dynamic quota cap effectively contained tasks, with cgroups memory usage logs confirming that outliers were killed via `OOMKilled` without affecting the host Invoker process.

## Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Generation scripts and code are available at [https://github.com/wisrovi/wyoloservice2_production](https://github.com/wisrovi/wyoloservice2_production).

## Broader Impact / Ethics Statement
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency [patterson2021carbon].

## Conclusion & Future Work
The pattern provides robust fault isolation for YOLO training pipelines. Future work will explore online memory profiling via LLM agents.

## Acknowledgments
We thank the wisrovi-suit contributors for the orchestration infrastructure.