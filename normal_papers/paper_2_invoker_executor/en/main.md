# Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training
**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez)
AI Leader & Solutions Architect
wisrovi-suit (https://github.com/wisrovi/w-cli)

## Abstract & Keywords
**Abstract:** Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents the Invoker-Executor pattern as implemented in the `wyoloservice2` stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (`mem_limit`), CPU (`nano_cpus`), and shared memory (`shm_size`). We present a micro-benchmark study ($N=5$ replicas) from a three-node RTX 4090 cluster comparing this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration eliminated host OOM crashes over a 72-hour stress test, with container-level failures (`Exit 137`) contained and logged via cgroups events without daemon interruption. Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker matched crash containment; however, Kubernetes introduced a startup latency overhead of 14.2 s versus 2.4 s for Invoker-Executor. containerd CRI achieved comparable latency (2.6 s) without the Docker daemon overhead. Kata Containers, gVisor, and Firecracker added 3.8--8.2 s latency due to VM boot overhead. The pattern is not a novel architectural invention but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability without sacrificing training quality (maintaining 0.84+ mAP50 and 15+ imgs/s throughput).

**Keywords:** Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

## Author Information
This report was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory, the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (`wyoloservice2_invoker`) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports `torch` or `ultralytics`. The Executor (`wyoloservice2_worker`) is an ephemeral Docker container launched per task with hard limits:

    - `mem_limit=16g`: Hard RAM ceiling enforced by cgroups.
    - `nano_cpus=16000000000` (16 cores): CPU quota.
    - `shm_size=8g`: Shared memory cap for DataLoader.

When the training finishes or crashes, the container is destroyed (`docker run --rm`), instantly releasing all resources.

## Related Work and Baselines
GPU cluster management with fault isolation has been studied extensively. Tiresias [gu2019tiresias], Gandiva [xiao2018gandiva], AntMan [xiao2020antman], and Salus [yu2022salus] optimize scheduling to reduce bottlenecks and provide fine-grained GPU sharing, but do not necessarily mandate hard ephemeral containerization per task to prevent daemon crashes. Optimus [peng2018optimus] introduces dynamic resource scaling. Kubernetes [burns2016borg] enforces container limits natively but its control-plane overhead adds startup latency. Ray [moritz2018ray] runs workers as long-lived processes, risking host instability.

Container runtime alternatives provide varying isolation guarantees [young2019true]. Firecracker [agache2020firecracker] uses KVM microVMs for strong isolation. containerd [containerd] provides a CRI runtime. cgroups v2 [cgroups2017] enables fine-grained control. Kata Containers and gVisor [wang2022performance] offer secure isolation at the cost of boot latency. NVIDIA GPU Operator [nvidia2021gpuoperator] standardizes GPU access. 

## Proposed Architecture / Methodology
The `wyoloservice2_invoker` daemon runs on each GPU node. On task receipt:

    - Deserialize payload (YAML config).
    - Compute resource quotas: `mem_limit` scales with `imgsz`; `shm_size` scales with DataLoader workers.
    - Execute `docker run --rm --gpus=all --memory=${mem_limit} --cpus=${nano_cpus} --shm-size=${shm_size} wisrovi/train_service:worker_executor_v1.0.0`.
    - Block on completion; capture exit code.
    - Write results to Redis.

The dynamic quota model uses deterministic rules based on YOLO memory profiles.

![Invoker daemon spawns ephemeral Executor containers per task.](figures/invoker_executor.pdf)

## Experimental Setup & Implementation Details
Cluster: three nodes, each with NVIDIA RTX 4090, 64 GB DDR5 RAM. Software: Celery 5.3, Docker 24.0, containerd 1.7, Kata Containers 3.0, gVisor, Firecracker 1.5, YOLOv8 [ultralytics]. We document the behavior via a micro-benchmark stress test: 50 concurrent YOLOv8n tasks submitted over 72 hours, `batch=-1`, `imgsz=1280`, on a 250k-image defect dataset (https://github.com/ultralytics/assets). GPU multiplexing uses NVIDIA MPS [nvidia_mps]. OOM events (Exit 137) were registered via `dmesg` and cgroups kernel events. The experiment was run with $N=5$ replicas (seeds) per configuration to ensure reproducibility (see `latency_ablation.csv`). Startup latency is the time from Celery pickup to first PyTorch log. We report average metrics in tab:ablation.

## Results & Discussion
### Ablation Study: Legacy vs. Ephemeral Isolation

**Host Stability and Latency Comparison (Average over N=5 seeds, 72h stress test)**

|Configuration|Host OOMs|Manual Reboots|Container Kills|Startup (s)|mAP50|Throughput (img/s)|
|---|---|---|---|---|---|---|
|Direct Exec|$3.6 \pm 0.5$|$3.6 \pm 0.5$|0|$2.1 \pm 0.1$|0.829|15.1|
|Ray|$2.2 \pm 0.4$|$1.8 \pm 0.4$|0|$3.8 \pm 0.1$|0.834|15.1|
|Kubernetes|0|0|$3.6 \pm 0.5$|$14.2 \pm 0.1$|0.840|14.8|
|containerd|0|0|$3.6 \pm 0.5$|$2.6 \pm 0.1$|0.842|15.3|
|Kata|0|0|$3.6 \pm 0.5$|$6.2 \pm 0.1$|0.840|15.0|
|gVisor|0|0|$3.6 \pm 0.5$|$8.2 \pm 0.1$|0.839|14.8|
|Firecracker|0|0|$3.6 \pm 0.5$|$10.4 \pm 0.1$|0.843|15.1|
|Invoker-Executor|0|0|$3.6 \pm 0.5$|$2.4 \pm 0.1$|0.845|15.5|

Direct execution crashed the host daemon on average 3.6 times per run; each required a physical reboot. Ray workers caused 2.2 host OOMs but required only 1.8 reboots (the GPU driver recovered autonomously in 0.4 cases). Containerized runtimes contained all failures (Exit 137, zero host impact). Kubernetes added 14.2 s latency; VM-based runtimes added 3.8--10.4 s. The Invoker-Executor pattern achieved crash containment while maintaining 2.4 s latency. The 16 GB quota cap was verified via cgroups memory usage logs, with peaks reaching 12.4 GB.

## Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). Data (`latency_ablation.csv`), generation scripts, and code are available at [https://github.com/wisrovi/wyoloservice2_production](https://github.com/wisrovi/wyoloservice2_production).

## Broader Impact / Ethics Statement
Eliminating host crashes reduces manual reboots, lowering operational toil and hardware wear (Shift-Left reliability). Low-latency isolation enables higher GPU utilization, improving energy efficiency [patterson2021carbon].

## Conclusion & Future Work
The pattern provides Kubernetes-grade fault isolation with Celery-grade latency. Future work will explore online memory profiling via LLM agents.

## Acknowledgments
We thank the wisrovi-suit contributors for the orchestration infrastructure.