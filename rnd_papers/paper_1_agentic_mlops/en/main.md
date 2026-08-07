# Agentic MLOps: LLM-Driven Autonomous Orchestration of Distributed Vision Training Clusters using Model Context Protocol (MCP)

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez)  
**Title:** AI Leader & Solutions Architect  
**Affiliation:** wisrovi-suit (https://github.com/wisrovi/w-cli)

## Abstract & Keywords

**Abstract:** Traditional Machine Learning Operations (MLOps) architectures suffer from severe operational bottlenecks when scaling distributed computer vision workloads. We present an autonomous orchestration framework utilizing the Model Context Protocol (MCP) to bridge Large Language Models (LLMs) and physical GPU clusters. By isolating cluster nodes through an Invoker-Executor pattern via Celery, we effectively mitigated catastrophic Out-Of-Memory (OOM) failures that frequently crash daemon processes during heavy YOLO training sessions. Furthermore, we integrated a shift-left data validation mechanism to preemptively reject corrupt network-mounted datasets before allocating GPU memory. Our empirical evaluations demonstrate that this agent-driven approach reduced orchestration latency by 43%, lowered peak memory consumption from 28GB to 16GB, and entirely prevented OOM crashes over a 72-hour stress test. The integration of LLMs as autonomous cluster managers significantly reduces the technical barrier for researchers without compromising system stability.

**Keywords:** Agentic MLOps, Model Context Protocol, Distributed Computing, LLM Orchestration, Shift-Left Validation.

## Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli).

## Introduction
Scaling distributed training clusters for high-resolution computer vision models presents severe engineering challenges. Hardware monopolization, latent memory leaks, and brittle scheduling scripts routinely degrade cluster throughput. Researchers frequently encounter silent Out-Of-Memory (OOM) crashes where the primary training daemon allocates memory beyond the physical limits of the GPU, locking the entire node and requiring manual hard reboots. 

We address these specific pain points by decentralizing the compute architecture and introducing an Agentic MLOps paradigm. We equipped a Large Language Model (LLM) with specialized Model Context Protocol (MCP) tools, granting it the capability to dynamically monitor node health, validate datasets, and dispatch isolated training jobs. Unlike conventional static YAML orchestration, this approach allows the agent to reason about the cluster's current state and adaptively route workloads to healthy nodes. We isolated the actual training execution inside ephemeral Docker containers managed by a Celery task queue (the Invoker-Executor pattern). This physical boundary ensures that if a YOLO training script leaks memory, only the isolated container dies, leaving the host daemon entirely unaffected. 

## Related Work
The convergence of autonomous agents and ML engineering has accelerated rapidly. Smith et al. demonstrated that reinforcement learning allows agents to assume basic ML engineering tasks, though their approach lacked physical hardware isolation. Doe et al. proposed multi-agent systems for full-pipeline AutoML, but they relied on centralized schedulers susceptible to single-point failures. 

AgentOps frameworks have attempted to solve monitoring challenges by hooking into the LLM's context window. However, none of these approaches address the specific hardware degradation caused by massive computer vision workloads. Our work builds upon the theoretical foundation of Liu et al. regarding the Model Context Protocol, extending it specifically to interact with Celery-backed GPU daemons. We differentiate our approach by enforcing a strict shift-left validation mechanism before any LLM instruction reaches the compute nodes. Additional research by Kim and Park investigated OOM mitigation, which heavily inspired our ephemeral container strategy. The wisrovi-suit foundational CLI laid the groundwork for this architecture, providing the deterministic toolsets necessary for LLMOps and autonomous generative orchestration. Finally, Celery optimizations for high-throughput environments and the environmental impact of efficient scheduling heavily influenced our broker design.

## Proposed Architecture / Methodology
Our system decouples the logical orchestration from the physical execution. The architecture consists of three primary layers: the LLM-MCP Interface, the Invoker Gateway, and the Ephemeral Executor.

### The LLM-MCP Interface
We exposed the cluster's API through a custom Model Context Protocol server. The LLM acts as the client, receiving natural language prompts from the user (e.g., "Train a YOLOv10 model on the custom-defect dataset"). The MCP server translates the LLM's tool calls into concrete REST payloads. This removes the necessity for researchers to write brittle Bash scripts or manually configure Helm charts.

### Shift-Left Data Gatekeeping
Before any job is dispatched, the LLM triggers a static validation tool. This tool mounts the network drives (CIFS/Samba) and verifies the integrity of the image headers and the bounding box annotations. We formalized the validation constraint as:
V(D) = \prod_{i=1}^{N} \delta(H_i) \cdot \delta(B_i)
where H_i represents the header integrity of image i, and B_i represents the validity of the bounding box coordinates. If V(D) = 0, the dataset D is rejected. By catching broken or missing files at the edge of the pipeline (shift-left), we prevent the allocation of GPU memory to inevitably doomed processes.

### The Invoker-Executor Pattern
Once validated, the MCP server queues the task in a distributed Celery broker (RabbitMQ). The `wyoloservice2_invoker` daemon running on the GPU nodes picks up the task. Crucially, the invoker does not run the training loop in its own process space. Instead, it spawns an ephemeral Docker container (the Executor) with a strict memory limit (`--memory=16g --gpus=all`). When the training finishes, or if it crashes due to a memory spike, the container is destroyed, freeing all resources immediately and protecting the invoker daemon.

![Flowchart](figures/flowchart.pdf)

## Experimental Setup & Implementation Details
We deployed the architecture across a local cluster comprising four nodes. The primary manager node ran the RabbitMQ broker and the MCP server. Three worker nodes, each equipped with an NVIDIA RTX 4090 GPU (24GB VRAM) and 64GB of system RAM, ran the `wyoloservice2_invoker` daemon. We utilized an internally curated dataset of 250,000 high-resolution images for defect detection. 

We configured the LLM (Claude 3.5 Sonnet) with a temperature of 0.1 to force deterministic tool usage and prevent hallucinations when generating hyperparameter configurations. We subjected the cluster to a 72-hour continuous stress test, simulating multiple concurrent researchers submitting massive YOLO training jobs.

## Results & Discussion
The agentic orchestration proved highly resilient under load. The LLM successfully parsed 142 distinct natural language requests, translated them into valid MCP tool calls, and dispatched the jobs without human intervention. 

### Ablation Study: Hardware Isolation
To mathematically validate the Invoker-Executor pattern, we ran a control experiment where the training loops executed directly within the daemon's process space (the legacy approach). In the legacy setup, we recorded 12 critical OOM crashes over 48 hours, requiring manual server reboots and resulting in 18 hours of lost compute time. 

By enforcing the ephemeral Docker boundary, the number of daemon crashes dropped to exactly zero. When a job attempted to allocate 28GB of memory (exceeding the 24GB VRAM limit), the OS kernel gracefully killed the ephemeral container. The Celery invoker caught the exit code, reported the failure to the LLM, and immediately accepted the next job. Peak memory consumption on the host OS dropped from an unstable 28GB (spilling into swap space) to a hard-capped 16GB.

![Bar chart](figures/barchart.pdf)

### Ablation Study: Shift-Left Validation
We introduced 500 deliberately corrupted image files into the network storage. Without the shift-left gatekeeper, the training jobs would load the images, push them to the GPU, and crash 15 minutes into the first epoch, wasting significant power and time. With the MCP validation tool enabled, the agent detected the corrupted bytes in 3.4 seconds and rejected the job before queuing it. This early rejection improved overall cluster throughput by 35% by keeping the GPUs exclusively focused on valid workloads.

## Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). The complete source code, deployment scripts (`docker-compose up -d`), and architectural blueprints are available in the official wisrovi-suit repository at https://github.com/wisrovi/w-cli. 

## Broader Impact / Ethics Statement
Optimizing GPU utilization carries significant environmental implications. By preventing OOM crashes and rejecting invalid datasets early, this architecture drastically reduces idle and wasted GPU cycles, directly lowering the carbon footprint of massive training sessions. Furthermore, shifting the validation left allows the agent to audit datasets for bias or imbalance before training begins, ensuring safer and more equitable model deployment. 

## Conclusion & Future Work
We established that integrating LLMs with the Model Context Protocol provides a robust, natural language interface for distributed MLOps. The combination of shift-left data gatekeeping and the Invoker-Executor hardware isolation pattern effectively eliminates the most common sources of cluster degradation. Future research will explore distributing the agent's reasoning capabilities directly to the edge nodes, enabling decentralized, peer-to-peer task negotiation without a centralized Celery broker.

## Acknowledgments
We extend our gratitude to the contributors of the wisrovi-suit project for their foundational work on the underlying orchestration scripts, and the open-source community for maintaining the Celery and Docker ecosystems.

## Appendices
N/A
