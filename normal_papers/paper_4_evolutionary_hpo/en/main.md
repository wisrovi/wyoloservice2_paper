# Decoupled Evolutionary Hyperparameter Search for YOLO Architectures in Edge-to-Core Distributed Computing Environments

## Abstract
Hyperparameter Optimization (HPO) is an essential component in developing robust Computer Vision (CV) models. However, traditional HPO methodologies, such as Grid Search or Random Search, are inherently inefficient and resource-intensive when deployed on distributed object detection workloads. This paper presents a fully decoupled, fault-tolerant integration of Evolutionary Hyperparameter Optimization leveraging the Tree-structured Parzen Estimator (TPE) algorithm. Our architecture orchestrates the search dynamically via a Celery and Redis message broker, completely decoupling the genetic algorithm's state (managed in PostgreSQL) from the intense mathematical execution (performed on distributed GPU worker nodes). We propose and detail a composite mathematical fitness function designed to optimize data augmentations and training hyperparameters by balancing mean Average Precision (mAP) against computational efficiency. Extensive empirical evaluations on the MS COCO 2017 dataset demonstrate that this decoupled approach drastically accelerates convergence, scales near-linearly across multi-GPU architectures, and outperforms baseline Random Search techniques by a significant margin.

## 1. Introduction
The advent of deep learning has revolutionized computer vision, particularly in real-time object detection where YOLO (You Only Look Once) architectures \cite{redmon2016you, redmon2017yolo9000, redmon2018yolov3, bochkovskiy2020yolov4, wang2023yolov7, jocher2023ultralytics} dominate. Achieving state-of-the-art performance with these models heavily depends on selecting optimal hyperparameters, ranging from learning rates and weight decay to complex geometric and photometric data augmentations. 

Hyperparameter Optimization (HPO) \cite{feurer2019hyperparameter} in deep neural networks \cite{lecun2015deep, he2016deep} is a non-convex optimization problem over a high-dimensional search space. In modern MLOps \cite{symeonidis2022mlops} and Data-centric AI \cite{zha2023data} environments, executing HPO efficiently requires orchestrating vast computational resources. Traditional tightly-coupled training scripts often result in resource monopolization, node failures corrupting the search state, and inefficient utilization of distributed clusters. 

To address these challenges, we propose a fully decoupled architectural paradigm for HPO. By separating the genetic trial management from the physical training execution using tools like Optuna \cite{akiba2019optuna}, Celery \cite{turnbaugh2007human}, Redis \cite{carlson2013redis}, and Docker \cite{merkel2014docker}, we achieve a robust, horizontally auto-scaling system. This paper details our methodology, including a rigorous definition of a composite fitness function that incorporates training latency penalties, and provides a comprehensive empirical comparison against established baselines.

## 2. Related Work
The field of HPO has progressed significantly beyond naive exhaustive search methods.

### 2.1 Traditional and Bayesian Optimization
Grid search and Random Search \cite{bergstra2012random} have been historically prevalent. While Random Search is surprisingly effective in lower dimensions, it struggles in complex CV pipelines. Bayesian Optimization (BO) \cite{snoek2012practical, hoos2014efficient} builds a surrogate model to map the hyperparameter space. The Tree-structured Parzen Estimator (TPE) \cite{bergstra2011algorithms} is a powerful BO approach that models the density of good and bad hyperparameters separately, proving highly effective for neural networks.

### 2.2 Multi-fidelity and Evolutionary Methods
Advanced frameworks like Hyperband \cite{li2017hyperband} utilize successive halving to allocate resources efficiently, discarding poor performers early. BOHB \cite{falkner2018bohb} integrates BO with Hyperband to achieve strong any-time performance. Furthermore, regularized evolutionary algorithms \cite{real2019regularized} have shown extreme robustness in complex architectural search spaces, avoiding local minima by applying mutation and crossover across populations of configurations.

### 2.3 Distributed MLOps Frameworks
Modern deep learning frameworks like PyTorch \cite{paszke2019pytorch} provide backend distributed training capabilities. However, for HPO, the orchestration of multiple distinct training runs (trials) requires a higher-level abstraction. Frameworks like Optuna \cite{akiba2019optuna} provide relational database backends to store study states, yet they lack native queue-based execution decoupling, which our architecture specifically addresses.

## 3. Methodology and Decoupled Architecture

Our primary contribution is a robust, decoupled architecture where the Hyperparameter Search Manager is isolated from the Compute Workers. 

### 3.1 Architectural Design

The system is designed around a producer-consumer paradigm using an Invoker-Executor pattern:

```mermaid
graph TD
    subgraph Manager Node
        O[Optuna TPE Sampler] -->|Generate Trial| DB[(PostgreSQL: Study State)]
        O -->|Enqueue Task| C[Celery Message Broker]
    end

    subgraph Messaging Layer
        C <-->|AMQP / Redis| R[(Redis Queue)]
    end

    subgraph GPU Worker Pool
        R -->|Dequeue Task| W1[Celery Worker 1]
        R -->|Dequeue Task| W2[Celery Worker 2]
        R -->|Dequeue Task| WN[Celery Worker N]
        
        W1 -->|Launch| D1[Docker Executor: YOLO Training]
        W2 -->|Launch| D2[Docker Executor: YOLO Training]
        WN -->|Launch| DN[Docker Executor: YOLO Training]
    end
    
    D1 -.->|Report Fitness| DB
    D2 -.->|Report Fitness| DB
    DN -.->|Report Fitness| DB
```

1. **Manager Node**: Runs the Optuna sampler. It evaluates the current study state from PostgreSQL and generates the next promising set of hyperparameters using the TPE algorithm.
2. **Message Broker**: The generated configuration is serialized and pushed to a Redis-backed Celery queue.
3. **Worker Nodes**: Distributed nodes listen to the queue. When a GPU becomes available, a Celery worker dequeues the configuration and launches an ephemeral Docker container to execute the training.
4. **State Reporting**: Upon completion (or early pruning), the container reports the objective fitness directly back to PostgreSQL, informing the next TPE sampling generation.

This decoupling guarantees that if a GPU node experiences a hardware failure (Out-Of-Memory, thermal throttling), the overall genetic study is neither corrupted nor halted. The failed task is simply re-queued or marked as pruned.

## 4. Mathematical Fitness Function and Coefficient Selection

In industrial computer vision, accuracy (e.g., mAP) is not the sole objective; computational efficiency and inference latency are equally critical. Our evolutionary search seeks to maximize a composite fitness function $F$ that balances predictive performance against training cost.

Let $mAP_{0.5:0.95}$ be the mean Average Precision evaluated on the validation set, and $T_{train}$ be the total training duration in hours for $E$ epochs. The fitness function is formulated as:

$$ F(x) = lpha \cdot mAP_{0.5:0.95}(x) - eta \cdot \log_{10}(T_{train}(x) + 1) - \gamma \cdot \Omega(x) $$

Where $x$ is the hyperparameter vector (e.g., learning rate, mosaic augmentation probability, mixup scale).

### 4.1 Coefficient Justification

- **$lpha$ (Accuracy Coefficient):** Set to $1.0$. We baseline the fitness on the absolute percentage of mAP.
- **$eta$ (Temporal Penalty):** Determines the penalty for slow convergence. A typical value is $0.05$. Because training times can vary exponentially based on batch size and input resolution, the logarithmic scale $\log_{10}(T_{train} + 1)$ ensures that excessively long training runs are gently penalized without dominating the mAP score. For instance, an increase from 10 to 100 hours of training only reduces the fitness by $0.05$.
- **$\gamma$ (Complexity Regularization):** A penalty term $\Omega(x)$ applied to computationally expensive augmentations (like high-degree Copy-Paste or MixUp). $\gamma$ is typically set to $0.01$ to discourage the TPE from exploiting data augmentations that marginally increase mAP but drastically increase epoch time.

This function effectively forces the TPE algorithm to search for hyperparameters that achieve high accuracy rapidly, filtering out configurations that yield negligible mAP gains at exorbitant computational costs.

## 5. Experimental Setup and Quantitative Results

To validate the framework, we executed HPO trials on the standard MS COCO 2017 dataset \cite{lin2014microsoft}, comparing our Decoupled TPE Evolutionary approach against a baseline Random Search \cite{bergstra2012random}.

### 5.1 Experimental Configuration
- **Model:** YOLOv8-s (Small) \cite{jocher2023ultralytics}
- **Dataset:** COCO 2017 (118k training images, 5k validation images)
- **Hardware:** A distributed cluster of 8x NVIDIA A100 (80GB) GPUs.
- **Search Space:** 
  - Initial Learning Rate: Log-uniform $[10^{-4}, 10^{-2}]$
  - Momentum: Uniform $[0.8, 0.99]$
  - Mosaic Augmentation Probability: Uniform $[0.0, 1.0]$
  - Mixup Probability: Uniform $[0.0, 0.5]$

### 5.2 Performance Comparison: TPE vs Random Search

We ran a 200-trial budget for both TPE and Random Search across the 8-GPU cluster.

| Algorithm | Best mAP (0.5:0.95) | Search Budget | Convergence Trial | Avg Trial Time (hrs) |
|---|---|---|---|---|
| Random Search \cite{bergstra2012random} | 46.1 | 200 | 184 | 2.1 |
| **Decoupled TPE (Ours)** | **48.5** | 200 | **62** | **1.8** |

*Table 1: Comparison of HPO strategies on the COCO dataset.*

The TPE algorithm not only found a superior hyperparameter configuration yielding a +2.4 mAP improvement, but it also converged on the best configuration significantly faster (at trial 62 versus 184). Furthermore, due to the temporal penalty $eta$ in our fitness function, the TPE actively avoided configurations with excessively heavy augmentations, resulting in a lower average trial time (1.8 hrs vs 2.1 hrs).

### 5.3 Multi-GPU Scaling and Efficiency

A critical evaluation of a decoupled architecture is its ability to scale horizontally without encountering communication bottlenecks.

| GPUs | Total Search Time (hrs) | Speedup Factor | Efficiency |
|---|---|---|---|
| 1 | 360.5 | 1.00x | 100% |
| 2 | 182.0 | 1.98x | 99% |
| 4 | 92.4 | 3.90x | 97.5% |
| 8 | 47.1 | 7.65x | 95.6% |

*Table 2: Scaling efficiency of the decoupled HPO architecture.*

As illustrated in Table 2, our architecture achieves near-linear scaling up to 8 GPUs. The overhead introduced by Celery task delegation and Redis messaging is negligible (less than 4.4% degradation at 8 nodes). This confirms that decoupling the manager state from the worker execution completely mitigates the traditional orchestration bottlenecks seen in tightly coupled MPI-based frameworks.

## 6. Conclusion and Future Work

In this paper, we introduced a fully decoupled architectural framework for Evolutionary Hyperparameter Search tailored for YOLO object detection models in distributed computing environments. By separating state management from mathematical execution via an Invoker-Executor pattern with Celery and Redis, we enabled robust, fault-tolerant horizontal scaling. Our customized composite fitness function successfully directed the Optuna TPE sampler toward configurations that maximized mAP while minimizing computational training costs. Empirical results on the MS COCO dataset proved that our method significantly outperforms traditional Random Search, converging faster and achieving higher accuracy.

Future work will investigate integrating multi-fidelity scheduling paradigms, such as BOHB, into our decoupled architecture to permit dynamic, mid-epoch pruning of sub-optimal trials across the distributed cluster.
