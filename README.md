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

### 🚀 Research and Development (R&D) Papers
*Experimental research, generative AI integration, and the AgentOps frontier.*

| Paper ID | Title | Research Focus | Links |
|:---:|:---|:---|:---|
| **1** | **Agentic MLOps: LLM-Driven Autonomous Orchestration** | Proposes using LLMs equipped with MCP to autonomously manage, validate, and launch massive YOLO training sessions. | [EN](./rnd_papers/paper_1_agentic_mlops/en/main.md) - [ES](./rnd_papers/paper_1_agentic_mlops/es/main.md) |
| **3** | **Automated XAI Pipelines in Computer Vision** | Introduces an "Onion-Layer" pipeline where statistical EDA and local LLMs (OpenCode) auto-generate post-training diagnostics. | [EN](./rnd_papers/paper_3_automated_xai/en/main.md) - [ES](./rnd_papers/paper_3_automated_xai/es/main.md) |

### ⚙️ Standard Papers (MLOps Engineering and Architecture)
*Systems architecture, High-Performance Computing (HPC), and industrial applied solutions.*

| Paper ID | Title | Research Focus | Links |
|:---:|:---|:---|:---|
| **2** | **The Invoker-Executor Pattern** | Mitigates memory leaks and hardware degradation in GPU clusters using Celery daemons and isolated ephemeral containers. | [EN](./normal_papers/paper_2_invoker_executor/en/main.md) - [ES](./normal_papers/paper_2_invoker_executor/es/main.md) |
| **4** | **Decoupled Evolutionary Hyperparameter Search** | Details a distributed Genetic Algorithm approach (Optuna) over Celery that prevents edge-to-core bottlenecks. | [EN](./normal_papers/paper_4_evolutionary_hpo/en/main.md) - [ES](./normal_papers/paper_4_evolutionary_hpo/es/main.md) |
| **5** | **Shift-Left Data Gatekeeping** | Validates the economic and operational impact of remote static validation on network-mounted datasets (CIFS/Samba). | [EN](./normal_papers/paper_5_shift_left_data/en/main.md) - [ES](./normal_papers/paper_5_shift_left_data/es/main.md) |

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

- **v1.0.2 (2026-08-07)**: Added new timestamped IEEE expert panel review verdicts for all 5 papers.
- **v1.0.1 (2026-08-07)**: Added official IEEE expert panel review verdicts for all papers.

---
*Developed with ❤️ in Badajoz, Extremadura, Spain.*