# Agentic MLOps: LLM-Driven Autonomous Orchestration of Distributed Vision Training Clusters using Model Context Protocol (MCP)

**William Steve Rodriguez Villamizar (wisrovi rodriguez)**  
AI Leader & Solutions Architect  

## Abstract & Keywords

**Abstract:** Traditional Machine Learning Operations (MLOps) architectures face scalability and stability challenges when orchestrating distributed computer vision workloads. We present an applied framework utilizing the Model Context Protocol (MCP) to interface Large Language Models (LLMs) with physical GPU clusters. By isolating cluster nodes through an Invoker-Executor pattern via task daemons, we mitigate Out-Of-Memory (OOM) failures that otherwise crash host processes during intensive YOLO training sessions. Additionally, we integrate a shift-left data validation mechanism to preemptively reject corrupt datasets before allocating GPU memory. Empirical evaluations against industry baselines (Ray Train and Kubernetes) demonstrate that this approach reduces orchestration overhead, lowers peak host memory consumption from 28GB to a capped 16GB, and prevents OOM crashes over a 72-hour stress test. The integration of LLMs for cluster management provides a reproducible methodology for the ML engineering community.

**Keywords:** Agentic MLOps, Model Context Protocol, Distributed Computing, LLM Orchestration, Shift-Left Validation.

## Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez).

## Introduction
Scaling distributed training clusters for high-resolution computer vision models presents significant engineering challenges. Memory leaks and brittle scheduling scripts can degrade cluster throughput. In distributed systems, silent Out-Of-Memory (OOM) crashes often cause the primary training daemon to allocate memory beyond the physical limits of the GPU, locking the entire node.

To address these challenges, we introduce an Agentic MLOps paradigm. We utilize a Large Language Model (LLM) equipped with specialized Model Context Protocol (MCP) tools [7], enabling dynamic node monitoring, dataset validation, and isolated job dispatch. This approach adapts workload routing dynamically, contrasting with static YAML orchestration [3].

The training execution is isolated inside ephemeral Docker containers managed by a Celery task queue, introducing an Invoker-Executor pattern. This ensures that if a training script encounters an OOM error, only the isolated container terminates, preserving the host daemon's stability.

## Related Work
The convergence of autonomous agents and ML engineering has gained traction. Recent studies [4] demonstrated that LLMs can utilize external tools to perform complex tasks, including API interactions. In MLOps [3], orchestrating distributed training efficiently remains an active area of research. Frameworks like Ray [2] and Kubernetes [5] provide robust foundations for distributed computing, but often require complex configuration and lack native LLM integration.

Data validation is critical in ML pipelines. Breck et al. [1] emphasized the importance of data validation before model training. We build upon this by enforcing a strict shift-left validation mechanism. Furthermore, the environmental impact of efficient scheduling and reducing wasted compute cycles has been well-documented [6].

## Proposed Architecture / Methodology
Our system decouples orchestration from physical execution across three layers: the LLM-MCP Interface, the Invoker Gateway, and the Ephemeral Executor.

### The LLM-MCP Interface
The cluster's API is exposed through a custom Model Context Protocol (MCP) server [7]. The LLM acts as the client, receiving natural language prompts and translating them into concrete REST payloads dispatched asynchronously. This abstraction layer simplifies user interactions with the distributed queues.

### Shift-Left Data Gatekeeping
Before job dispatch, the LLM triggers a static validation tool [1] to verify image headers and bounding box annotations. We formalize the LLM's cluster management as a Markov Decision Process (MDP) defined by the tuple $(\mathcal{S}, \mathcal{A}, P, R, \gamma)$. The state space $\mathcal{S}$ represents the health, memory availability, and dataset integrity of all nodes. The action space $\mathcal{A}$ includes dispatching jobs, isolating nodes, or preemptively rejecting corrupted datasets.

$$ \pi^*(s) = \arg\max_a \mathbb{E} \left[ \sum_{t=0}^\infty \gamma^t R(s_t, a_t) \mid s_0 = s \right] $$

The reward function $R(s,a)$ heavily penalizes OOM events and idle GPU cycles. By catching broken files at the edge of the pipeline (shift-left), the optimal policy $\pi^*$ dynamically rejects inevitably doomed processes rather than relying on static scheduling.

### The Invoker-Executor Pattern
Once validated, tasks are queued into a distributed broker. Crucially, the invoker does not run the training loop in its own process space. It spawns an ephemeral Docker container (the Executor) with a strict memory limit. If the container crashes due to a memory spike, it is destroyed, protecting the invoker daemon. 

![Invoker-Executor Architecture](figures/fig1.pdf)

## Experimental Setup & Implementation Details
We deployed the architecture across a local cluster of four nodes. The manager node ran the Redis broker and FastAPI server. Three worker nodes, each with an NVIDIA RTX 4090 GPU (24GB VRAM) and 64GB of system RAM, ran the invoker daemon. The dataset comprised 250,000 high-resolution images.

We subjected the cluster to a 72-hour continuous stress test and compared our approach against standard Ray Train [2] and Kubernetes [5] deployments running the same YOLO workloads.

## Results & Discussion

### Ablation Study: Hardware Isolation and Baselines
To validate the Invoker-Executor pattern, we compared our architecture against Ray Train, Kubernetes, and a legacy local daemon setup. In the legacy setup, we recorded 12 critical OOM crashes over 72 hours. Ray Train managed the workloads better but still suffered from 4 node-level lockups due to aggressive memory preallocation and lack of strict container limits per job. Kubernetes required significant scheduling overhead and experienced 2 OOM kills that cascaded into pod restart loops.

By enforcing the ephemeral Docker boundary, our architecture reduced daemon crashes to zero. Peak host memory consumption was capped at 16GB, compared to 28GB in the legacy setup, 24GB in Ray Train, and 22GB in Kubernetes.

| Metric | Legacy Daemon | Ray/K8s | Agentic MLOps (Ours) |
| --- | --- | --- | --- |
| OOM Host Crashes (72h) | 12 | 4 / 2 | 0 |
| Peak Host Memory Usage | 28GB | 24GB / 22GB | 16GB |
| Lost Compute Time | 18 hours | 5 hours | 0 hours |

![Comparison of crashes and memory usage](figures/fig2.pdf)

### Ablation Study: Shift-Left Validation
We introduced 500 deliberately corrupted image files. Without shift-left validation, training jobs crashed 15 minutes into the first epoch. With the validation tool enabled, the agent rejected the corrupted jobs in 3.4 seconds. This early rejection improved overall cluster throughput by 35% compared to the baseline.

## Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce the experiments, the https://github.com/wisrovi/wyoloservice2_production repository is used.

## Conclusion & Future Work
Integrating LLMs with the Model Context Protocol provides a resilient interface for distributed MLOps. The combination of shift-left data gatekeeping and the Invoker-Executor pattern eliminates common sources of cluster degradation, outperforming standard baselines in fault tolerance. Future research will explore decentralized task negotiation without a centralized broker.
