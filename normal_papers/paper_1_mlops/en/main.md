\IEEEoverridecommandlockouts

\raggedbottom

# NeuralForge: A Distributed MLOps Framework for Automated YOLO Hyperparameter Optimization

**Author:** \IEEEauthorblockN{William Steve Rodriguez Villamizar
\IEEEauthorblockA{\textit{AI Leader \& Solutions Architect} \\
\textit{wisrovi-suit}\\
Badajoz, Extremadura, Spain \\
wisrovi.rodriguez@gmail.com}
}

\begin{abstract}
Scaling hyperparameter optimization (HPO) for computer vision models across heterogeneous GPU clusters introduces critical bottlenecks in state isolation and task routing. We present NeuralForge, a distributed MLOps framework structured on an Invoker-Executor pattern that distributes Optuna trials across GPU worker nodes using Celery. By decoupling execution into ephemeral Docker containers, NeuralForge prevents OOM-driven host failures and dependency conflicts. Empirical experiments on a 3-node GPU cluster (designed to scale up to 30 nodes) demonstrate median task dispatch latency of 0.8ms, robust fault tolerance, and a 40\% reduction in idle GPU time compared to baseline monolithic setups. NeuralForge establishes a scalable approach for local MLOps, outperforming standard Ray Tune and Kubeflow deployments in terms of container cold-start and idle waste on edge clusters.
\end{abstract}

\begin{IEEEkeywords}
Distributed Systems, MLOps, Hyperparameter Optimization, YOLO, Docker, Optuna
\end{IEEEkeywords}

## Introduction
Hyperparameter Optimization (HPO) for deep learning models, such as YOLO , requires executing thousands of computationally intensive trials. Traditional monolithic frameworks struggle to manage state isolation across continuous trials, often culminating in Out of Memory (OOM) errors . NeuralForge refactors the standard worker paradigm into an Invoker-Executor pattern. By employing Celery  and PostgreSQL for shared Optuna state , the architecture dynamically routes tasks through prioritized GPU queues.

## Related Work
Existing HPO orchestrators like Ray Tune  and Kubeflow  provide extensive tracking but lack lightweight execution isolation tailored for raw GPU metal, introducing substantial networking overhead. Methods like Hyperband  and BOHB  improve sampling efficiency but do not solve deployment isolation. NeuralForge bridges this gap using ephemeral Docker containers  from a lightweight Celery Invoker.

## Proposed Architecture
The framework desacouples the system into three primary layers, shown in .

    - **API Gateway**: A FastAPI service  ingests configuration payloads via Redis.
    - **Manager Node**: Orchestrates the Optuna study (TPE  or CMA-ES ).
    - **Invoker-Executor Node**: A Celery Invoker spawns an ephemeral Docker Executor bound strictly by `shm\_size` and GPU ID. It writes results to CIFS and terminates.

## Experimental Setup
Empirical experiments were conducted on a cluster of N=3 GPU nodes. The architecture is designed to scale up to 30 nodes (validated via synthetic stress tests), but full 30-node empirical evaluation remains future work. Hardware and software specifications are detailed in .

## Results and Discussion
### Performance Metrics and SoA Comparison
NeuralForge achieved median task dispatch latency of 0.8ms (IQR 0.05ms) across 1000 simulated dispatches (). Compared to Ray Tune (TorchTrainer) and Kubeflow, NeuralForge eliminated cold-start orchestration overhead by leveraging persistent Invokers, improving GPU utilization by 40\%. 

### Bottleneck Analysis \& Fault Tolerance
We analyzed shared bottlenecks: under heavy load, PostgreSQL connection pooling maintained P99 ask/tell latency under 15ms. Redis broker throughput exceeded 5000 tasks/sec. In fault tolerance evaluation, a simulated Executor OOM (exit 137) resulted in 100\% graceful requeuing via Celery (MTTR $\approx$ 2s) with zero data loss. Watchtower updates the cluster image silently (polling interval: 60s) with zero interrupted tasks.

### Ablation Study on Memory Limits
Disabling Docker memory limits resulted in host OOM kills in a median of 4.2 hours (P95: 5.1h) due to PyTorch memory leaks. With ephemeral limits active, the host remained stable for 72 hours (max RAM 11.5 GB).

## Data \& Code Availability
Scripts for latency and ablation benchmarks are in `wyoloservice2\_production/benchmarks`.

## Broader Impact
Efficient GPU orchestration mitigates carbon footprint .

## Conclusion
NeuralForge scales HPO workloads efficiently on bare-metal GPUs.

## Acknowledgments
We acknowledge the wisrovi-suit project.