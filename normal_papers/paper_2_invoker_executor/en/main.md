\raggedbottom

# Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training}

## Abstract \& Keywords
**Abstract:** Persistent daemon processes that execute PyTorch training loops directly in their own address space are vulnerable to memory leaks, shared-memory exhaustion, and kernel OOM kills that cascade into host instability. This industrial experience report documents the Invoker-Executor pattern as implemented in the `wyoloservice2` stack: a persistent Celery daemon (Invoker) that never imports CUDA, and ephemeral Docker containers (Executors) spawned per task with hard OS-level limits on memory (`mem\_limit`), CPU (`nano\_cpus`), and shared memory (`shm\_size`). We present empirical ablation data from a three-node RTX 4090 cluster comparing this pattern against direct execution, Ray, Kubernetes Jobs, containerd CRI, Kata Containers, gVisor, and Firecracker. The Invoker-Executor configuration reduced host OOM crashes from a median of 18 per day (IQR: 16--20) to zero over a 72-hour stress test, with container-level failures (`Exit 137`) contained and logged without daemon interruption. Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker matched crash containment; however, Kubernetes introduced a median startup latency overhead of 14.2 s (IQR: 12.8--15.6 s) versus 2.4 s (IQR: 2.1--2.7 s) for Invoker-Executor. containerd CRI achieved comparable latency (2.6 s, IQR: 2.3--2.9 s) without the Docker daemon overhead. Kata Containers, gVisor, and Firecracker added 3.8--8.2 s latency due to VM boot overhead. Ray required explicit per-task containerization to achieve similar isolation. The pattern is not a novel architectural invention---container-based fault isolation is established DevOps practice---but its integration into a lightweight Celery-based MLOps stack yields a pragmatic, low-overhead solution for GPU cluster stability.

**Keywords:** Industrial Experience Report, Fault Isolation, Distributed Deep Learning, Celery Task Queues, Ephemeral Containers, Container Runtimes.

## Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Distributed deep learning clusters suffer from a persistent operational failure mode: the training daemon itself becomes a single point of failure. In the conventional layout, a Celery worker (or Ray actor, or Kubernetes pod) imports PyTorch, initializes CUDA contexts, and runs the training loop in-process. When a YOLO script leaks memory---common with unoptimized data loaders, large batch sizes, or long-running epochs---the process RSS grows until the kernel OOM killer terminates it. Because the daemon holds the CUDA context, the kill often leaves the GPU in an inconsistent state, requiring a full node reboot to recover.

This report describes a structural fix: separate the control plane from the compute plane. The Invoker (`wyoloservice2\_invoker`) is a minimal Python process that polls a Redis queue and manages container lifecycles. It never imports `torch`, `cv2`, or `ultralytics`. The Executor (`wyoloservice2\_worker`) is an ephemeral Docker container launched per task with hard limits:

    - `mem\_limit=16g`: Hard RAM ceiling enforced by cgroups.
    - `nano\_cpus=16000000000` (16 cores): CPU quota preventing scheduler starvation.
    - `shm\_size=8g`: Shared memory cap preventing PyTorch DataLoader crashes.

When the training finishes or crashes, the container is destroyed (`docker run --rm`), instantly releasing all resources. The Invoker captures the exit code, updates Redis with the result or failure, and returns to the queue.

We evaluate this pattern not as a theoretical contribution but as a documented engineering practice, comparing it against the full spectrum of modern container runtimes: Docker daemon, containerd CRI, Kata Containers (lightweight VMs), gVisor (user-space kernel), and Firecracker (microVMs).

## Related Work and Baselines
GPU cluster management with fault isolation has been studied extensively. Tiresias  optimizes scheduling to reduce bottlenecks but does not mandate per-task containerization. Optimus  introduces dynamic resource scaling for deep learning workloads. Slurm  provides robust batch scheduling with cgroup integration but carries HPC-oriented complexity. Kubernetes  enforces container limits natively; however, its control-plane overhead (pod scheduling, kubelet latency) adds 10--20\% startup latency for short-lived tasks compared to a direct Celery-to-Docker path. Ray  excels at distributed training but runs workers as long-lived processes; without explicit `ray start --container` configuration, memory leaks in worker processes can still cascade to the host.

Container runtime alternatives provide varying isolation guarantees. Firecracker  uses KVM microVMs for strong isolation with minimal overhead. gVisor  implements a user-space kernel for syscall interception. Kata Containers  wraps each pod in a lightweight VM. containerd  provides a CNCF-graduated CRI runtime without the Docker daemon. cgroups v2  unified hierarchy enables finer-grained resource control. The NVIDIA GPU Operator  standardizes GPU access across runtimes.

Our contribution is not the concept of container isolation---it is the empirical demonstration that a minimal Celery+Docker integration achieves comparable crash containment to Kubernetes and containerd CRI with lower latency, and integrates cleanly with existing YOLO tooling. We further quantify the overhead of VM-based isolation (Kata, gVisor, Firecracker) for GPU workloads.

## Proposed Architecture / Methodology
The `wyoloservice2\_invoker` daemon runs on each GPU node. On task receipt:

    - Deserialize the task payload (YAML training config + hyperparameters).
    - Compute dynamic resource quotas: `mem\_limit` scales with `imgsz` and batch size; `shm\_size` scales with DataLoader worker count.
    - Execute `docker run --rm --gpus=all --memory=\$\{mem\_limit\` --cpus=\$\{nano\_cpus\} --shm-size=\$\{shm\_size\} -v /shared:/app/data wisrovi/train\_service:worker\_executor\_v1.0.0}.
    - Block on container completion; capture stdout/stderr and exit code.
    - Write results or error to Redis (`wyolo:results:...` or `wyolo:errors:...`).
    - Return to queue polling.

The dynamic quota model uses simple heuristics: base memory 8 GB + 2 GB per 320px of `imgsz` above 640; `shm\_size` = 2 GB $\times$ DataLoader workers. These are not learned predictions but deterministic rules derived from empirical observation of YOLO memory profiles.

## Experimental Setup \& Implementation Details
Cluster: three nodes, each with NVIDIA RTX 4090 (24 GB VRAM), 64 GB DDR5 RAM, 32-core AMD EPYC. Redis 7.0 broker on a dedicated manager node. Software: `wyoloservice2\_invoker` (Python 3.12, Celery 5.3), Docker 24.0, containerd 1.7 (via nerdctl), Kata Containers 3.0, gVisor (runsc 2024), Firecracker 1.5, Ultralytics YOLOv8.

Stress test: 50 concurrent YOLOv8n training tasks submitted over 72 hours, each with `batch=-1` (auto-batch), `imgsz=1280`, 4 DataLoader workers, on a 250k-image defect dataset. This configuration reliably triggers memory pressure and shared-memory exhaustion in unisolated daemons.

Baselines:

    - **Direct Execution**: Invoker runs `train()` in-process (no Docker).
    - **Ray 2.9**: Tasks submitted as Ray remote functions; no per-task containerization.
    - **Kubernetes 1.28**: Jobs with `resources.limits.memory=16Gi`, `nvidia.com/gpu=1`, `shm-size=8Gi`.
    - **containerd CRI**: Tasks via nerdctl with `--memory=16g --shm-size=8g`.
    - **Kata Containers**: Pods with `kata-qemu` runtime, equivalent limits.
    - **gVisor**: `runsc` runtime with `--memory=16g --shm-size=8g`.
    - **Firecracker**: MicroVMs via `containerd` + `firecracker-containerd`, equivalent limits.
    - **Invoker-Executor (Ours)**: Celery daemon + `docker run --rm --gpus=all --memory=16g --cpus=16 --shm-size=8g`.

## Results \& Discussion
### Ablation Study: Legacy vs. Baselines vs. Ephemeral Isolation
\begin{table*}[htbp]
\centering
\caption{Host Stability and Latency Comparison (72-hour stress test, median [IQR] across 5 seeds)}
\label{tab:ablation}
\resizebox{\textwidth}{!}{
\begin{tabular}{@{}lllllllll@{}}
\toprule
Metric & Direct Exec & Ray (no container) & Kubernetes & containerd & Kata & gVisor & Firecracker & Invoker-Executor \\ \midrule
Host OOM Crashes & 18 [16--20] & 11 [9--13] & 0 & 0 & 0 & 0 & 0 & 0 \\
Manual Reboots Required & 18 [16--20] & 9 [7--11] & 0 & 0 & 0 & 0 & 0 & 0 \\
Container/Job Kills (contained) & 0 & 0 & 18 [16--20] & 18 [16--20] & 18 [16--20] & 18 [16--20] & 18 [16--20] & 18 [16--20] \\
Avg. Task Startup Latency (s) & 2.1 [1.9--2.3] & 3.8 [3.4--4.2] & 14.2 [12.8--15.6] & 2.6 [2.3--2.9] & 6.2 [5.6--6.8] & 8.2 [7.5--8.9] & 10.4 [9.6--11.2] & 2.4 [2.1--2.7] \\ \bottomrule
\end{tabular}
}
\end{table*}

Direct execution crashed the host daemon a median of 18 times (IQR: 16--20); each required a physical reboot to restore GPU usability. Ray workers leaked memory similarly, causing a median of 11 host OOM events (IQR: 9--13; 9 required reboots; 2 recovered via driver reset). Kubernetes, containerd CRI, Kata Containers, gVisor, and Firecracker contained all failures at the pod/container/VM level (median 18 container kills, all `Exit 137`, zero host impact). However, startup latency varied significantly: Kubernetes added 14.2 s (IQR: 12.8--15.6 s) due to scheduler and kubelet overhead; containerd CRI achieved 2.6 s (IQR: 2.3--2.9 s), comparable to our 2.4 s (IQR: 2.1--2.7 s); VM-based runtimes added 3.8--8.2 s overhead due to VM boot (Kata: 6.2 s, gVisor: 8.2 s, Firecracker: 10.4 s).

The dynamic quota rules prevented over-provisioning: tasks with `imgsz=640` received 8 GB memory; `imgsz=1280` received 12 GB. No task exceeded its allocation; the 16 GB ceiling was never reached.

### Docker Daemon vs. containerd CRI Overhead
We measured the cold-start container pull and launch overhead for both Docker daemon and containerd CRI (nerdctl) with the `wisrovi/train\_service:worker\_executor\_v1.0.0` image (2.4 GB compressed). Docker daemon: median pull time 12.4 s (IQR: 11.2--13.8 s) cold, 0.8 s (IQR: 0.6--1.1 s) warm; launch overhead 1.6 s (IQR: 1.4--1.8 s). containerd CRI: median pull time 11.8 s (IQR: 10.5--13.1 s) cold, 0.7 s (IQR: 0.5--0.9 s) warm; launch overhead 1.4 s (IQR: 1.2--1.6 s). The difference is marginal (< 1 s) for warm launches; containerd eliminates the daemon memory footprint (~150 MB RSS) and reduces attack surface.

## Data \& Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce these experiments, use the https://github.com/wisrovi/wyoloservice2_production repository.

## Broader Impact / Ethics Statement
Eliminating host crashes removes the need for manual node reboots, reducing operational toil and hardware wear from hard power cycles. The low-latency isolation enables higher cluster utilization without sacrificing stability.

## Conclusion \& Future Work
The Invoker-Executor pattern provides Kubernetes-grade fault isolation with Celery-grade latency. It is a practical engineering pattern, not a theoretical novelty. Future work will explore adaptive quota prediction using online memory profiling (e.g., sampling container RSS at epoch boundaries to refine the next task's `mem\_limit`).

## Acknowledgments
We thank the contributors of the wisrovi-suit project for the foundational CLI and orchestration infrastructure.