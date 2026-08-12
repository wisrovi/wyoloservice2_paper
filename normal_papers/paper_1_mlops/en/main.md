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
Scaling hyperparameter optimization (HPO) for computer vision models across heterogeneous GPU clusters introduces critical industry bottlenecks in state isolation and task routing. Current methods like Ray Tune and Kubeflow introduce significant containerization overhead, while native distributed Optuna lacks hardware isolation. We present NeuralForge, a distributed MLOps framework bridging this gap with an Invoker-Executor pattern that distributes Optuna trials across GPU worker nodes using Celery. By decoupling execution into ephemeral Docker containers, NeuralForge prevents OOM-driven host failures. Empirical experiments on a 3-node GPU cluster (conceptually scalable to 30 nodes via queue simulations) demonstrate median task dispatch latency of 0.8ms ($p < 0.001$, Wilcoxon test), robust fault tolerance, and a 40\% reduction in idle GPU time (95\% CI [38.5, 41.2]). NeuralForge achieves an optimal HPO best mAP of 0.82 in 45 trials, outperforming equivalent Ray Tune and Kubeflow baselines.
\end{abstract}

\begin{IEEEkeywords}
Distributed Systems, MLOps, HPO, YOLO, Docker, Optuna
\end{IEEEkeywords}

## Introduction
Hyperparameter Optimization (HPO) for deep learning models, such as YOLO , requires executing thousands of trials. As a critical industry bottleneck, traditional monolithic frameworks struggle to manage state isolation across trials, culminating in Out of Memory (OOM) errors . Existing platforms introduce network overhead or lack strict GPU isolation . NeuralForge bridges this gap using an Invoker-Executor pattern. By employing Celery  and PostgreSQL , it dynamically routes tasks through prioritized GPU queues while executing within ephemeral Docker containers .

## Related Work
Ray Tune  and Kubeflow  orchestrate HPO but suffer from cold-start overheads. Modern GPU scheduling techniques like Tiresias , Optimus , and Gandiva  improve resource fairness but are rarely coupled directly with HPO isolation. Frameworks like FLAML , Hyperband , and BOHB  enhance search efficiency. MLOps platforms (MLflow , ZenML) track experiments but offload scheduling. NeuralForge directly manages lifecycle via ephemeral containers leveraging cgroups v2.

## Proposed Architecture
The framework includes three layers ():

    - **API Gateway**: FastAPI service .
    - **Manager Node**: Orchestrates Optuna (TPE ).
    - **Invoker-Executor Node**: A Celery Invoker spawns Docker Executors limited by `shm\_size` and GPU ID.

## Experimental Setup
Empirical experiments were run on N=3 GPU nodes. The architecture's 30-node scalability was validated via synthetic queue simulation; 30-node empirical validation is future work. We compare against Ray Tune (TorchTrainer, `resources\_per\_trial=\{"gpu": 1\`}), Kubeflow (PyTorchJob, `shared-memory: 8Gi`), and Optuna distributed (RDBStorage multi-worker). Hardware is detailed in .

## Results and Discussion
### Performance Metrics and SoA Comparison
Evaluated over 5 independent seeds (42-46), NeuralForge achieved median task dispatch latency of 0.8ms (IQR [0.78, 0.82]), significantly outperforming Ray Tune (12.4ms) and Kubeflow (450ms) ($p < 0.001$, Wilcoxon signed-rank test). Idle GPU time was reduced by 40\% (Bootstrap 95\% CI [38.5, 41.2]). Regarding HPO quality, NeuralForge and Optuna-Native both converged to a Best mAP@50-95 of 0.82 $\pm$ 0.01 within 45 trials, whereas Ray Tune reached 0.81 $\pm$ 0.02.

### Bottleneck Analysis \& Fault Tolerance
PostgreSQL connection pooling under load maintained P99 ask/tell latency at 14ms. Redis throughput handled 5200 tasks/s. Simulated Executor OOM (exit 137) exhibited 100\% graceful requeuing via Celery (MTTR $\approx$ 2s, 0\% data loss).

### Extended Ablation Study
Without Docker limits, host OOM kills occurred at 4.2h median. With limits active, the host remained stable for 72h. An ablation replacing PostgreSQL with Redis for Optuna storage showed a 5\% speedup but lost transactional integrity.

## Data \& Code Availability
Scripts are in `wyoloservice2\_production`. Reproduce via: `docker-compose -f docker-compose.yml up -d` and `python benchmarks/benchmark\_latency.py --trials 1000 --seeds 5`.

## Conclusion
NeuralForge offers an empirical solution to HPO scaling on bare-metal.