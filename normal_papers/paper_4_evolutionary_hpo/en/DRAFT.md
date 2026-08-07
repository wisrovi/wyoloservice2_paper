# Decoupled Evolutionary Hyperparameter Search for YOLO Architectures in Edge-to-Core Distributed Computing Environments

## Abstract
Hyperparameter search (Random/Grid) in distributed vision is inefficient. This paper describes a fully decoupled integration of Genetic Algorithms using Optuna (TPESampler) via Celery and Redis. The evolutionary model dynamically optimizes data augmentations and training parameters across a pool of GPUs without monopolizing resources.

## 1. Introduction
We present a model where the state of the genetic trial (Manager/PostgreSQL) resides separately from the mathematical execution (Worker), allowing for horizontal auto-scaling.

## 2. Related Work
- **Hyperparameter Optimization for Object Detection Models (YOLO) using Optuna (2023-2025):** Application of TPE in Optuna to adjust augmentation magnitudes and training parameters in YOLO.
- **Evolutionary Hyperparameter Optimization for Deep Neural Networks using Genetic Algorithms (2024):** Evolutionary approaches (survival, crossover) for complex networks.
- **Automated Data Augmentation and Hyperparameter Tuning for YOLO Architectures (2024/2025):** Methodologies to reduce the "domain gap" by stabilizing vision configurations.

## 3. Distributed Genetic Manager
Analysis of the Celery orchestrator (`wyoloservice2_manager`) and the study database in PostgreSQL.

## 4. Conclusion
Decoupling the genetic algorithm reduces computational costs and dramatically accelerates training convergence.
