# An Empirical Performance Study of the Invoker-Executor Pattern for Resilient MLOps Orchestration

# Abstract & Keywords
**Abstract:** Managing distributed GPU workloads for computer vision training presents challenges in maintaining node stability under high VRAM demands. Traditional daemon-based task execution can lead to physical node failures due to Out-Of-Memory (OOM) events triggered by heavy workloads. In this empirical performance study, we evaluate the Invoker-Executor pattern—an orchestration approach where a lightweight Celery daemon (Invoker) delegates GPU execution to ephemeral Docker containers (Executor). We compare this approach against standard Kubernetes Jobs, Ray, and Slurm in terms of orchestration overhead and fault tolerance. Our results indicate that this isolation strategy eliminates critical node failures caused by workload memory spikes, while introducing a predictable 2.1-second overhead for container instantiation, providing a viable alternative for lightweight, resilient MLOps orchestration.

**Keywords:** Distributed Computing, Ephemeral Containerization, GPU Memory Management, Fault Tolerance, MLOps, Empirical Study.

# Introduction
Computer vision model training, particularly involving advanced architectures, places significant stress on GPU VRAM and system memory. In standard distributed MLOps pipelines, a centralized broker distributes training tasks to worker nodes. A common implementation relies on a persistent daemon that receives the task and executes the training loop within its own process space.

When an Out-Of-Memory (OOM) event occurs, the Linux kernel's OOM killer terminates processes to recover memory, which may include the persistent daemon itself. This leaves the physical GPU node online at the hardware level but disconnected from the distributed queue, requiring manual intervention and limiting scalability.

To address this, we analyze the Invoker-Executor pattern. Rather than executing the compute-heavy workload directly, the daemon acts strictly as an Invoker. It dynamically creates an ephemeral, resource-constrained Docker container (the Executor) and delegates the training workload to it, ensuring fault isolation.

# Related Work
Resource management in multi-tenant GPU clusters has been widely studied. Tiresias [gu2019tiresias] and Optimus [peng2018optimus] present cluster managers tailored for distributed deep learning. For distributed AI applications, Ray [moritz2018ray] offers a robust framework, though its centralized state management differs from lightweight daemon-based approaches. 

Kubernetes [burns2016borg] provides extensive container orchestration capabilities, including Job management, which ensures isolated execution environments. Slurm [yoo2003slurm] remains a standard for high-performance computing workload scheduling. Our study compares the Invoker-Executor approach against these established systems to evaluate its viability as a lightweight alternative for specific MLOps workflows.

# Proposed Architecture / Methodology
The physical node is divided into two logical layers: the Persistent Control Plane (Invoker) and the Ephemeral Compute Plane (Executor).

## The Invoker Daemon
The Invoker is a lightweight worker operating with a minimal memory footprint. Its responsibilities are queue polling, payload parsing, and container lifecycle management. It does not import heavy machine learning libraries, mitigating the risk of CUDA-related memory corruption in the control process.

## The Ephemeral Executor
Upon receiving a task, the Invoker executes a subprocess call to the host Docker daemon. It constructs a container execution command that binds the required datasets and enforces strict cgroup limits using memory and GPU constraints.

If the Executor attempts to allocate memory beyond its cgroup limit, the host kernel terminates the container. The Invoker catches the non-zero exit code, updates the task status to failed, logs the reason, and resumes queue polling. The physical node experiences no downtime.

# Experimental Setup & Implementation Details
We evaluated this architecture on a cluster of three worker nodes. Each node was equipped with an NVIDIA RTX 4090 (24GB VRAM), 64GB of RAM, and a 24-core CPU. 

We engineered a stress test to evaluate system resilience. We submitted a batch of 100 training tasks, configuring 20% of them with excessively high batch sizes to trigger VRAM overflow. We measured node uptime, peak memory consumption, and task completion rates across different orchestration methods: Legacy Daemon, Invoker-Executor, Kubernetes Jobs, Ray, and Slurm.

# Results & Discussion
The Invoker-Executor pattern successfully shielded the host operating system from the injected memory spikes.

## Benchmark: Resilience and Overhead
We compared the Invoker-Executor pattern against Kubernetes Jobs, Ray, and Slurm under the same stress test conditions.

| Metric | Legacy Daemon | Invoker-Executor | Kubernetes Jobs | Ray | Slurm |
|---|---|---|---|---|---|
| Host OOM Crashes | 18 | 0 | 0 | 2 | 0 |
| Container/Task Kills | 0 | 20 | 20 | 18 | 20 |
| Orchestration Overhead | N/A | ~2.1s | ~5.4s | ~1.8s | ~3.2s |

In the legacy configuration, the malicious tasks caused the daemon to crash 18 times, requiring manual intervention. The Invoker-Executor pattern experienced zero crashes, properly isolating the 20 failures to the ephemeral containers.

Kubernetes Jobs provided equivalent fault isolation (zero host crashes) but exhibited a higher orchestration overhead (5.4 seconds) due to control plane communication. Ray showed lower overhead (1.8 seconds) but experienced 2 host-level failures when worker processes failed to isolate memory spikes effectively. Slurm offered strong isolation but required more complex configuration and exhibited a 3.2-second scheduling overhead.

The Invoker-Executor pattern balances low orchestration overhead (2.1 seconds) with robust fault isolation, making it suitable for environments where deploying a full Kubernetes control plane is undesirable.

# Conclusion & Future Work
This empirical study evaluates the performance and resilience of the Invoker-Executor pattern for MLOps orchestration. By enforcing a strict container boundary between the queue Invoker and the compute Executor, the system mitigates OOM-induced cluster failures. Compared to Kubernetes Jobs, Ray, and Slurm, this pattern offers a lightweight alternative with minimal orchestration overhead. Future work will investigate dynamic resizing of container resource limits during runtime based on real-time telemetry.
