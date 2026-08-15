# Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training
**Author:**
William Steve Rodriguez Villamizar (wisrovi rodriguez) [ORCID](https://orcid.org/0000-0002-4740-9734)
AI Leader & Solutions Architect
wisrovi-suit (https://github.com/wisrovi/w-cli)

## Abstract & Keywords
**Abstract:** Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report [garousi2016need] documents an observational design study of the Invoker-Executor pattern as implemented in the `wyoloservice2` stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (`mem_limit`), CPU (`nano_cpus`), and shared memory (`shm_size`). We qualitatively compare this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration successfully contained memory leaks over our production observations, logging failures via cgroups events without daemon interruption. The pattern is not a novel architectural invention, but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

**Keywords:** Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

## Author Information
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix observed within our proprietary stack: decoupling the long-lived queue consumer from the short-lived training routine. The Invoker (Celery daemon) only manipulates metadata; the Executor (Docker container) runs the PyTorch code and inherits hard resource limits. This observational study summarizes the production viability of this pattern.

## Related Work and Baselines
GPU cluster management with fault isolation has been studied extensively. Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman], and Salus [yu2022salus] optimize scheduling to reduce bottlenecks and provide fine-grained GPU sharing, but do not necessarily mandate hard ephemeral containerization per task to prevent daemon crashes. Optimus [peng2018optimus] introduces dynamic resource scaling. Kubernetes [burns2016borg] enforces container limits natively but its control-plane overhead adds startup latency. Ray [moritz2018ray] runs workers as long-lived processes, risking host instability.

Container runtime alternatives provide varying isolation guarantees [young2019true]. Firecracker [agache2020firecracker] uses KVM microVMs for strong isolation. containerd [containerd] provides a CRI runtime. cgroups v2 [cgroups2017] enables fine-grained control. Kata Containers and gVisor [wang2022performance] offer secure isolation at the cost of boot latency. NVIDIA GPU Operator [nvidia2021gpuoperator] standardizes GPU access. 

## Proposed Architecture / Methodology
The architecture is depicted in \Cref{fig:arch}. The `wyoloservice2_invoker` daemon runs on each GPU node. On task receipt:

    - Deserialize payload (YAML config).
    - Compute resource quotas: `mem_limit` scales with `imgsz`; `shm_size` scales with DataLoader workers.
    - Execute `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`.
    - Block on completion; capture exit code.
    - Write results to Redis.

![Invoker daemon spawns ephemeral Executor containers per task.](figures/invoker_executor.pdf)

## Observational Design Study
Cluster: three nodes, each with NVIDIA RTX 4090, 64 GB DDR5 RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 [ultralytics]. GPU multiplexing uses NVIDIA MPS [nvidia_mps]. OOM events (Exit 137) were qualitatively registered via `dmesg` and cgroups kernel events during production usage.

## Results & Discussion
### Qualitative Observations: Legacy vs. Ephemeral Isolation

In our observational study, direct execution periodically crashed the host daemon due to memory exhaustion, often requiring a physical reboot due to corrupted GPU states. Ray workers exhibited similar issues, occasionally allowing the GPU driver to recover autonomously. 

Over an observational window of 14 days and approximately 1,500 training tasks, containerized runtimes qualitatively isolated failures, allowing individual tasks to fail without seemingly affecting the host daemon. While Kubernetes offers robust limits natively, its control-plane added noticeably higher startup latency in our observations in launching pods compared to the lightweight daemon. VM-based runtimes like Kata, gVisor, and Firecracker provided strong security boundaries but introduced measurable boot overhead in our setup. 

The Invoker-Executor pattern was consistent with our qualitative observations of Kubernetes-level containment and microVMs while maintaining a minimal startup profile, as it merely executes Docker CLI commands outside of a heavy orchestration plane. The dynamic quota cap effectively contained tasks, with cgroups memory usage logs confirming that outliers were typically terminated via `OOMKilled`, which generally avoided a cascade of host instability.

## Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Generation scripts and code are available at [https://github.com/wisrovi/wyoloservice2_production](https://github.com/wisrovi/wyoloservice2_production).

## Broader Impact / Ethics Statement
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency [patterson2021carbon].

## Conclusion & Future Work
The pattern provides robust fault isolation for YOLO training pipelines. Future work will explore online memory profiling via LLM agents.

## Acknowledgments
We thank the wisrovi-suit contributors for the orchestration infrastructure.


## References

[1] V. Garousi, M. Felderer, and M. V. Mäntylä, "The need for empirical evidence in software engineering," *IEEE Software*, vol. 33, no. 1, pp. 68-75, 2016.

[2] J. Gu *et al.*, "Tiresias: A gpu cluster manager for distributed deep learning," *USENIX NSDI*, 2019.

[3] W. Xiao *et al.*, "Gandiva: Introspective cluster scheduling for deep learning," in *13th USENIX Symposium on Operating Systems Design and Implementation (OSDI 18)*, 2018.

[4] W. Xiao *et al.*, "Antman: Dynamic scaling on GPU clusters for deep learning," in *14th USENIX Symposium on Operating Systems Design and Implementation (OSDI 20)*, 2020.

[5] P. Yu and M. Chowdhury, "Salus: Fine-grained GPU sharing primitives for deep learning applications," in *Proceedings of the 3rd Conference on Machine Learning and Systems (MLSys)*, 2022.

[6] Y. Peng *et al.*, "Optimus: an efficient dynamic resource scheduler for deep learning clusters," in *Proceedings of the Thirteenth EuroSys Conference*, 2018, pp. 1-14.

[7] B. Burns *et al.*, "Borg, omega, and kubernetes," in *ACM Queue*, 2016.

[8] P. Moritz *et al.*, "Ray: A distributed framework for emerging ai applications," in *USENIX OSDI*, 2018.

[9] T. Young *et al.*, "The true cost of containing: A performance study of container runtimes," in *USENIX HotCloud*, 2019.

[10] A. Agache *et al.*, "Firecracker: Lightweight virtualization for serverless applications," *USENIX NSDI*, 2020.

[11] M. Crosby *et al.*, "containerd: An industry-standard container runtime," in *CNCF*, 2017.

[12] T. Heo, "Control groups v2," *Linux Kernel Documentation*, 2017.

[13] Y. Wang *et al.*, "Performance and isolation analysis of runc, gvisor and kata containers," *Cluster Computing*, 2022.

[14] NVIDIA, "Nvidia gpu operator," https://github.com/NVIDIA/gpu-operator, 2021.

[15] G. Jocher *et al.*, "Ultralytics yolov8," 2023. [Online]. Available: https://github.com/ultralytics/ultralytics 

[16] NVIDIA, "Multi-process service (mps)," https://docs.nvidia.com/deploy/mps/index.html, 2023.

[17] D. Patterson *et al.*, "Carbon emissions and large neural network training," *arXiv preprint arXiv:2104.10350*, 2021.