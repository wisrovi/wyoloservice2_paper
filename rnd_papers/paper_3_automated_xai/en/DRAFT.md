# Automated XAI Pipelines in Computer Vision: Integrating Pre-train EDA and On-Device LLM Diagnostics into the MLOps Lifecycle

## Abstract
The disconnect between model training and metric interpretation requires hours of human analysis. We propose an "Onion-Layer" architecture where the training pipeline automatically executes a statistical Exploratory Data Analysis (EDA) and, post-training, a local LLM (OpenCode) generates narrative reports and diagnostics to explain model behavior.

## 1. Introduction
We address Explainability and Automated Diagnostics in MLOps, automatically transforming raw CSV files and confusion matrices into human-readable information (MD/DOCX) using Generative AI.

## 2. Related Work
- **Are Large Language Models Post Hoc Explainers? (2024/2025):** Research on how LLMs interpret visual features and generate readable summaries.
- **PASTA: Perceptual Assessment System for explanaTion of Artificial Intelligence (2024/2025):** A benchmark integrating explanatory analysis and automated metrics.
- **Automatic Configuration of LLM Post-Training Pipelines (AutoPipe) (2025/2026):** Agent-oriented automation for post-training stages.

## 3. Automated XAI Pipeline
Internal pipeline description of the *worker*: EDA Extraction -> YOLO Training -> Post-training Analysis with local LLM.

## 4. Conclusion
Automating model diagnostics (XAI) within the MLOps cycle democratizes data-driven decision-making without intensive manual intervention.
