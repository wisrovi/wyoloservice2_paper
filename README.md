# 🔬 NeuralForgeAI - Scientific Research & Publications

Welcome to the official research and academic repository for the **NeuralForgeAI (train_service2)** ecosystem. 

This repository serves as the central hub for our scientific publications, technical whitepapers, and state-of-the-art architectural research in the field of Distributed Machine Learning, Agentic MLOps, and Computer Vision orchestration.

## 📖 About Our Research

The NeuralForgeAI ecosystem resolves critical industry bottlenecks in distributed Deep Learning—such as hardware monopolization, memory leaks in GPU clusters, and manual diagnostic inefficiencies. Our research focuses on taking these applied engineering solutions and formalizing them into high-impact academic papers for the broader AI community (e.g., IEEE, ACM, NeurIPS, CVPR).

Our primary research vectors include:
1. **Agentic MLOps**: Integrating Large Language Models (LLMs) and Model Context Protocol (MCP) to autonomously orchestrate computer vision clusters.
2. **Hardware Isolation**: Decentralizing compute using the Invoker-Executor pattern with ephemeral Docker containers to prevent catastrophic cluster failures.
3. **Automated Explainability (XAI)**: Merging Exploratory Data Analysis (EDA) with local generative models to provide human-readable post-training diagnostics.
4. **Decoupled Hyperparameter Optimization**: Scaling Genetic Algorithms and Optuna TPESamplers across distributed nodes.
5. **Data-Centric AI (Shift-Left)**: Proving that early-stage network dataset validation saves thousands of GPU compute hours.

---

## ⚖️ IEEE Expert Panel Review (2026)

All papers in this repository have been subjected to a rigorous peer review by an IEEE expert panel to assess their scientific contribution, novelty, and integrity. The final verdicts, including detection of AI-generated content and detailed improvement notes, can be found in the [IEEE_REVIEW_VERDICT.md](./IEEE_REVIEW_VERDICT.md) document.

---

## 📚 Publications Directory

We categorize our papers into two main branches: **Research & Development (R&D)** for experimental frontier technologies, and **Standard Papers** for MLOps engineering and architecture.

*(Note: Currently, only papers that have passed the strict IEEE Peer Review process and achieved APPROVED status are listed here. Other papers are currently undergoing revision).*

### ⚙️ Standard Papers (MLOps Engineering and Architecture)
*Systems architecture, High-Performance Computing (HPC), and industrial applied solutions.*

| Paper ID | Title | Research Focus | Links |
|:---:|:---|:---|:---|
| **1** | **NeuralForge: A Distributed MLOps Framework** | Invoker-Executor pattern with ephemeral Docker isolated tasks that prevents catastrophic cluster failures via dynamic task orchestration. | [EN](./normal_papers/paper_1_mlops/en/main.md) - [ES](./normal_papers/paper_1_mlops/es/main.md) |
| **2** | **Automated Explainable AI Pipeline for YOLO Models** | Methodological framework for quantitative fidelity validation of visual explanations using Deletion/Insertion AUC and t-SNE latent space mappings. | [EN](./normal_papers/paper_2_xai/en/main.md) - [ES](./normal_papers/paper_2_xai/es/main.md) |
| **3** | **Quantifying YOLO Model Robustness** | Automated robustness auditing pipeline evaluating adversarial vulnerability (FGSM), noise resilience, and uncertainty decomposition (MC Dropout). | [EN](./normal_papers/paper_3_robustness/en/main.md) - [ES](./normal_papers/paper_3_robustness/es/main.md) |
| **4** | **Cross-Domain Generalization Assessment** | Automated post-training pipeline using Fréchet Inception Distance (FID) to predict domain shift mAP degradation, paired with hardware complexity profiling. | [EN](./normal_papers/paper_4_crossdomain/en/main.md) - [ES](./normal_papers/paper_4_crossdomain/es/main.md) |
| **6** | **LLM-Powered Automated Research Reporting** | Local LLMs (OpenCode) generate verifiable, deterministic post-training scientific narratives, avoiding hallucinations via strict fallback mechanisms. | [EN](./normal_papers/paper_6_llm_reporting/en/main.md) - [ES](./normal_papers/paper_6_llm_reporting/es/main.md) |
| **7** | **WPipe: A Declarative Pipeline Framework with Forensic Tracking** | SQLite-based forensic tracking, strict Pydantic type validation, and checkpointing for rapid failure recovery in ML workflows. | [EN](./normal_papers/paper_7_wpipe/en/main.md) - [ES](./normal_papers/paper_7_wpipe/es/main.md) |

---

## 📜 Repository Rules & Standards

To maintain camera-ready quality for all our publications, this repository enforces strict authorship protocols via our `AGENTS.md` system:

1. **Camera-Ready Structure**: Every paper must strictly adhere to a 13-section IEEE-style format, including Abstract, Related Work, Methodology, Broader Impact, and Data Availability statements.
2. **Dual-Language Sync**: Papers must exist simultaneously in English (`en/`) and Spanish (`es/`). Synchronization between the two is mandatory.
3. **Format Triangulation**: Inside every language folder, the paper must be maintained identically across three formats: `Markdown (.md)` for quick reading, `LaTeX (.tex)` for academic submission, and compiled `.pdf`.
4. **Git Identity**: All commits must trace back to the primary author identity: **William Steve Rodriguez Villamizar (wisrovi rodriguez)**.

---

## 🤝 Citation & Licensing

### Citation
If you utilize our architectural patterns or reference these papers in your own work, please cite the primary author:
> **William Steve Rodriguez Villamizar (wisrovi rodriguez)**, *AI Leader & Solutions Architect at eCaptureDtech*.

*A formal `CITATION.cff` is available at the root of the ecosystem.*

### License
These papers document an ecosystem that operates under a **Dual Licensing Model** (PolyForm Noncommercial / AGPLv3). 
- For academic and open-source research, the concepts and code are free to use.
- For commercial applications, please consult the `COMMERCIAL.md` file in our core repositories and contact the author for revenue-share/licensing agreements.

## 🔄 Changelog

- **v1.6.0 (2026-08-12)**: Paper 4 (Cross-Domain Generalization Assessment for Object Detection Models) has been officially ACCEPTED by the IEEE.
- **v1.5.0 (2026-08-12)**: Paper 3 (Quantifying YOLO Model Robustness) has been officially ACCEPTED by the IEEE.
- **v1.4.0 (2026-08-12)**: Paper 7 (WPipe: A Declarative Pipeline Framework with Forensic Tracking for ML Workflows) has been officially ACCEPTED by the IEEE.
- **v1.3.0 (2026-08-12)**: Paper 2 (Automated Explainable AI Pipeline for YOLO Models) has been officially ACCEPTED by the IEEE.
- **v1.2.0 (2026-08-12)**: Paper 1 (NeuralForge: A Distributed MLOps Framework) has been officially ACCEPTED by the IEEE.
- **v1.1.0 (2026-08-12)**: Paper 6 (LLM-Powered Automated Research Reporting) has been officially ACCEPTED by the IEEE.
- **v1.0.3 (2026-08-12)**: Updated directory to only list strictly approved papers.
- **v1.0.2 (2026-08-07)**: Added new timestamped IEEE expert panel review verdicts for all 5 papers.
- **v1.0.1 (2026-08-07)**: Added official IEEE expert panel review verdicts for all papers.

---
*Developed with ❤️ in Badajoz, Extremadura, Spain.*
