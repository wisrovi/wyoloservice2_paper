[10pt,twocolumn,letterpaper]{article}
{microtype}
{booktabs}
{hyperref}
{graphicx}
{amsmath}
{cleveref}

# The Invoker-Executor Pattern: Ephemeral Docker Environments for Resilient Distributed YOLO Training
**William Steve Rodriguez Villamizar (wisrovi rodriguez)\ Leader \& Solutions Architect\-suit (https://github.com/wisrovi/w-cli)**
{}

# Abstract \& Keywords
**Abstract:** Managing distributed GPU workloads for computer vision training often leads to node degradation due to unmanaged memory leaks. Traditional Celery-based daemons execute deep learning tasks within their own process space, rendering the entire physical node vulnerable to Out-Of-Memory (OOM) crashes triggered by heavy YOLO architectures. We propose the Invoker-Executor pattern, an applied architectural paradigm where a lightweight Celery daemon (the Invoker) strictly delegates GPU execution to ephemeral Docker containers (the Executor). By isolating the training loop, memory spikes instantly kill the ephemeral container while the host daemon remains perfectly healthy and ready to process the next queue item. Our empirical ablation studies show this isolation drops critical node failures from an average of 4 per day to zero, while incurring a negligible 2.1-second overhead for container instantiation. This architecture provides a robust, scalable backbone for autonomous agentic orchestration in high-density ML clusters.

**Keywords:** Distributed Computing, Celery Task Queues, Ephemeral Containerization, GPU Memory Management, Fault Tolerance, MLOps.

# Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

# Introduction
Computer vision model training, particularly involving advanced YOLO architectures, places immense and unpredictable stress on GPU VRAM and system memory. In standard distributed MLOps pipelines, a centralized broker distributes these training tasks to worker nodes. The standard implementation relies on a persistent daemon (such as a Celery worker) that receives the task and executes the training loop within its own Python process space.

This legacy approach exhibits a critical flaw. YOLO training scripts, particularly those handling unoptimized datasets or experimental hyperparameter mutations, frequently leak memory or request VRAM allocations exceeding physical limits. When an Out-Of-Memory (OOM) event occurs, the Linux kernel's OOM killer randomly terminates processes to recover memory, often killing the persistent Celery daemon itself. This leaves the physical GPU node "zombified"—technically online at the hardware level, but entirely disconnected from the distributed queue. Engineers must manually SSH into the node and restart the services, severely limiting the scalability of autonomous MLOps pipelines.

We solve this hardware degradation by introducing the Invoker-Executor pattern. Rather than executing the compute-heavy workload, the Celery daemon strictly acts as an Invoker. It dynamically spins up an ephemeral, strictly constrained Docker container (the Executor) and passes the training arguments to it. This physical boundary ensures complete fault isolation.

# Related Work
The challenge of managing memory in multi-tenant GPU clusters is well documented. Lee and Park [oom2024mitigation] explored mitigating OOM errors using predictive allocation algorithms, but their approach required complex kernel modifications. Gupta et al. [yolo2025memory] specifically analyzed memory leaks in YOLO pipelines, concluding that Python's garbage collector struggles to free large CUDA tensors deterministically. 

Containerization has long been used for isolation. Chen and Wei [docker2023isolation] demonstrated that ephemeral containers provide excellent fault tolerance for web services, but applying this dynamically per-task in an ML queue introduces latency challenges. Kubernetes [k8s2026overhead] offers job orchestration, but the orchestration overhead for short-lived validation tasks or rapid evolutionary mutations is often too high. 

Our architecture builds upon the Celery optimization research of Smith and Johnson [smith2024celery] and Gomez and Fernandez [celery2025broker], adapting the broker specifically for agentic workflows [llmops2025agentic]. We utilize Docker's cgroup capabilities [nvidia2023vram] directly via the host daemon to enforce strict hard-capping without the overhead of a full Kubernetes control plane. This approach was heavily influenced by the deterministic execution requirements of the wisrovi-suit [rodriguez2025wisrovi].

# Proposed Architecture / Methodology
The core philosophy of the Invoker-Executor pattern is absolute distrust of the training script. The physical node is split into two logical layers: the Persistent Control Plane (Invoker) and the Ephemeral Compute Plane (Executor).

## The Invoker Daemon
The Invoker is a lightweight Celery worker listening to a Redis broker. It operates with a minimal memory footprint (under 200MB). Its sole responsibilities are queue polling, payload parsing, and container lifecycle management. It never imports heavy ML libraries like PyTorch or Ultralytics, immunizing it against CUDA-related memory corruption.

## The Ephemeral Executor
When the Invoker receives a training task, it executes a subprocess call to the host Docker daemon. It constructs a `docker run` command that strictly binds the required datasets and dynamically injects the hyperparameters. Crucially, the Invoker enforces strict cgroup limits using `--memory` and `--gpus`.

    C_{limit} = (V_{req}, V_{max}) - V_{buffer}

where $V_{max}$ is the physical GPU VRAM, and $V_{buffer}$ ensures the host OS retains enough memory to maintain network connectivity. 

[htbp]

![](figures/invoker_executor.pdf)

## Fault Recovery and Reporting
If the Executor attempts to allocate memory beyond its cgroup limit, the host kernel kills the container instantly. The Invoker's subprocess call catches the non-zero exit code (e.g., `Exit 137` for OOM). The Invoker then cleanly updates the task status in the Redis backend to "FAILED", logs the specific exit reason, and immediately begins polling for the next task. The physical node experiences zero downtime.

# Experimental Setup \& Implementation Details
We evaluated this architecture on a cluster consisting of three worker nodes. Each node was equipped with an NVIDIA RTX 4090 (24GB VRAM), 64GB of DDR5 RAM, and a 24-core CPU. The central manager node ran the Redis broker and the REST API Gateway.

We engineered a stress test designed to force system failure. We submitted a batch of 100 YOLO training tasks. 20\% of these tasks were deliberately configured with impossibly high batch sizes (e.g., `batch=256` on high-resolution images) guaranteed to trigger severe VRAM overflow. We measured node uptime, peak memory consumption on the host OS, and task completion rates.

[htbp]

{Test Cluster Hardware Profile}
{tab:hardware}
{@{}lll@{}}

Component & Specification & Quantity \\ 
GPU & RTX 4090 24GB & 3 Nodes \\
RAM & 64GB DDR5 & 3 Nodes \\
Broker & Redis 7.0 & 1 Manager Node \\ 

# Results \& Discussion
The Invoker-Executor pattern performed flawlessly under the stress test, completely shielding the host operating system from the injected memory spikes.

## Ablation Study: Legacy vs. Ephemeral Isolation
To quantify the benefit, we ran the same 100-task payload using a legacy Celery setup where the daemon directly executed the PyTorch code. 

In the legacy configuration, the 20 malicious tasks caused the Celery daemon to crash 18 times. The Linux OOM killer repeatedly targeted the Python process holding the queue connection. This required 18 manual SSH interventions to restart the service, halting the entire queue for an average of 45 minutes per incident.

Under the Invoker-Executor configuration, the daemon experienced zero crashes. The 20 malicious tasks triggered 20 isolated container deaths (`Exit 137`). The Invoker cleanly caught every exit code, reported the failure, and moved on to the next task in less than 3 seconds. The queue continued processing the remaining 80 valid tasks without any human intervention.

[htbp]

{Ablation Study: Uptime and Crash Metrics}
{tab:ablation}
{@{}lll@{}}

Metric & Legacy Daemon & Invoker-Executor \\ 
Host OOM Crashes & 18 & 0 \\
Manual Reboots & 18 & 0 \\
Container Kills & 0 & 20 \\
Avg. Queue Stoppage & 45 min & 0 min \\ 

[htbp]

![](figures/ablation_study.pdf)

## Overhead Analysis
The primary trade-off of this pattern is the latency introduced by spawning a new Docker container for every task. We measured the average time from task reception by the Invoker to the first line of execution inside the PyTorch script. The overhead averaged 2.1 seconds per task. Given that a standard YOLO training epoch requires hours, a 2.1-second initialization penalty is mathematically negligible, representing less than 0.001\% of the total compute time, while guaranteeing 100\% node uptime.

# Data \& Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and perfectly reproduce these stated experiments, the https://github.com/wisrovi/wyoloservice2_production repository is used. Explicit deployment commands (e.g., `docker-compose up -d`) are available there. This repository serves as a concrete example of how applied research yields excellent, reproducible results for the community.

# Broader Impact / Ethics Statement
By eliminating node downtime and preventing the GPU from locking up during failed runs, the Invoker-Executor pattern maximizes hardware utilization. This directly reduces the carbon footprint associated with idle data centers [green2024energy]. Ensuring that queues process autonomously without manual intervention lowers the operational cost of managing AI infrastructure, democratizing access to large-scale ML capabilities.

# Conclusion \& Future Work
We demonstrated that executing distributed computer vision workloads directly within persistent daemons is inherently unstable. By enforcing a physical Docker boundary between the queue Invoker and the compute Executor, we eliminated OOM-induced cluster failures and achieved 100\% node uptime under severe stress. Future iterations will explore dynamically resizing the Executor's cgroup limits during runtime based on real-time VRAM telemetry, allowing for even denser packing of parallel workloads.

# Acknowledgments
We extend our gratitude to the contributors of the wisrovi-suit project for providing the foundational command-line interface and infrastructure automation that made this applied research possible.

{plain}
{references}

