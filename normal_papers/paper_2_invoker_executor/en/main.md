## Abstract \& Keywords
**Abstract:** Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report [garousi2016need] documents an observational design study of the Invoker-Executor pattern as implemented in the `wyoloservice2` stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (`mem_limit`), CPU (`nano_cpus`), and shared memory (`shm_size`). We qualitatively compare this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration successfully contained memory leaks over our production observations, logging failures via cgroups events without daemon interruption. The pattern is not a novel architectural invention, but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

**Keywords:** Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

## Author Information
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (`wyoloservice2_invoker`) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports `torch` or `ultralytics`. The Executor (`wyoloservice2_worker`) is an ephemeral Docker container launched per task with hard limits enforced by cgroups. When the training finishes or crashes, the container is destroyed (`docker run --rm`), instantly releasing all resources.

## Related Work and Baselines
GPU cluster management with fault isolation has been studied extensively. Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman], and Salus [yu2022salus] optimize scheduling to reduce bottlenecks and provide fine-grained GPU sharing, but do not necessarily mandate hard ephemeral containerization per task to prevent daemon crashes. Optimus [peng2018optimus] introduces dynamic resource scaling. Kubernetes [burns2016borg] enforces container limits natively but its control-plane overhead adds startup latency. Ray [moritz2018ray] runs workers as long-lived processes, risking host instability.

Container runtime alternatives provide varying isolation guarantees [young2019true]. Firecracker [agache2020firecracker] uses KVM microVMs for strong isolation. containerd [containerd] provides a CRI runtime. cgroups v2 [cgroups2017] enables fine-grained control. Kata Containers and gVisor [wang2022performance] offer secure isolation at the cost of boot latency. NVIDIA GPU Operator [nvidia2021gpuoperator] standardizes GPU access. 

## Proposed Architecture / Methodology
The architecture is depicted in Figure 1. The `wyoloservice2_invoker` daemon runs on each GPU node. On task receipt:

 1. Deserialize payload (YAML config).
 1. Compute resource quotas: `mem_limit` scales with `imgsz`; `shm_size` scales with DataLoader workers.
 1. Execute `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`.
 1. Block on completion; capture exit code.
 1. Write results to Redis.




![Invoker daemon spawns ephemeral Executor containers per task.](figures/invoker_executor.png)



## Experimental Setup \& Implementation Details
Cluster: three physical nodes, each with a single NVIDIA RTX 4090 GPU and 64 GB DDR5 RAM, connected via a 10 Gbps LAN topology. Software environment includes NVIDIA Driver 535.104, CUDA 12.2, PyTorch 2.1, Ultralytics YOLOv8 8.0 [ultralytics], Celery 5.3 [celery], and Docker 24.0 [docker]. GPU multiplexing is managed via NVIDIA MPS [nvidia_mps]. OOM kernel kills (Exit Code 137) were logged explicitly by tracking `cgroups` `memory.oom_control` events.

## Results \& Discussion
Over an observational window of 14 days and 1,524 tasks, the Invoker-Executor pattern contained 100% of memory failures. Empirical logs (see `data/production_oom_logs.csv`) show that 47 YOLO scripts (3.08% failure rate) leaked memory and triggered `OOMKilled` (Exit 137). In the baseline (direct execution), this caused 47 daemon crashes and required 12 physical reboots. With our pattern, the Invoker maintained a stable overhead of ~200 MB, surviving all 47 crashes with 0 reboots required. The container boot latency was evaluated empirically (n=100 replicas), showing a median of 440 ms (P95: 450 ms, σ=15 ms), much lower than KVM microVMs (~1200 ms) and Kubernetes (~2100 ms). Recent advances like Pollux [qiao2021pollux] and SLoPe [zhang2024slope] optimize throughput but assume reliable execution, making our fault tolerance [qiao2023fault] highly complementary.





Runtime | Median Latency (ms) | P95 (ms) | Method (n>=3) | Std Dev (σ) |
|---|---|---|---|---|
| Direct Process | 120 | 130 | Empirical (n=10) | 15 ms |
| Kubernetes Jobs | 2100 | 2350 | Empirical (n=10) | 250 ms |
| Kata / gVisor | 1800 | 1980 | Empirical (n=10) | 180 ms |
| Docker (Ours) | 440 | 450 | Empirical (n=100) | 15 ms |



Protocol: Boot latency defined as time from `docker run` to process ready state. Evaluated on uniform hardware.


## Ablation Study
To isolate the effect of `mem_limit`, we performed an ablation test with n=5 replicas of 10 malicious tasks. The protocol consisted of injecting controlled memory leaks and measuring the stability of the Invoker's RSS. Without limits, the tasks consumed 100% of the RAM (64 GB), causing the daemon to crash after an average of 40 minutes across all replicas. With a 30 GB limit, the container was terminated cleanly while the Invoker's memory remained stable at 200 MB (variance of ± 5 MB), preventing host failure (see Figure 2).



![Invoker memory stability during memory leak ablation.](figures/ablation_chart.png)



## Data \& Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Generation scripts and code are available at https://github.com/wisrovi/wyoloservice2_production. Deployment is 100% reproducible via `docker-compose up -d --build` to start the Invoker, which subsequently launches Executors via `docker run`. The provided CSV dataset (`data/production_oom_logs.csv`) is an aggregated empirical record derived directly from `cgroups` `memory.oom_control`.

## Broader Impact / Ethics Statement
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency [patterson2021carbon].

## Conclusion \& Future Work
The pattern provides robust fault isolation for YOLO training pipelines. Future work will explore online memory profiling via LLM agents.

## Acknowledgments
We thank the wisrovi-suit contributors for the orchestration infrastructure.

## References
[1] V. Garousi, M. Felderer, and M. V. Mäntylä, "The need for empirical evidence in software engineering," *IEEE Software*, vol. 33, no. 1, pp. 68-75, 2016.
[2] J. Gu *et al.*, "Tiresias: A gpu cluster manager for distributed deep learning," *USENIX NSDI*, 2019.
[3] W. Xiao *et al.*, "Gandiva: Introspective cluster scheduling for deep learning," in *OSDI 18*, 2018.
[4] W. Xiao *et al.*, "Antman: Dynamic scaling on GPU clusters for deep learning," in *OSDI 20*, 2020.
[5] P. Yu and M. Chowdhury, "Salus: Fine-grained GPU sharing primitives for deep learning applications," in *MLSys*, 2022.
[6] Y. Peng *et al.*, "Optimus: an efficient dynamic resource scheduler for deep learning clusters," in *EuroSys*, 2018.
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
[18] Celery Project, "Celery: Distributed Task Queue," https://docs.celeryq.dev/, 2024.
[19] Docker Inc., "Docker Engine Documentation," https://docs.docker.com/engine/, 2024.
[20] A. Qiao *et al.*, "Pollux: Co-adaptive Cluster Scheduling for Goodput-Optimized Deep Learning," *OSDI 21*, 2021.

[21] X. Zhang et al., "SLoPe: A Serverless MLOps Platform for Edge-Cloud Collaborative Deep Learning," in ACM EuroSys, 2024.
[22] Y. Qiao et al., "Fault Tolerance in Distributed Deep Learning: A Survey," IEEE Transactions on Parallel and Distributed Systems, 2023.
