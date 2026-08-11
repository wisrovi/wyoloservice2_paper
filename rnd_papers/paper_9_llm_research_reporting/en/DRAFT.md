# Paper 9: LLM-Powered Automated Research Reporting for Computer Vision Pipelines

**Category:** Research & Development (R&D)  
**Status:** DRAFT  
**Target Venue:** EMNLP / ACL / NeurIPS Workshop on AI for Science

---

## 🎯 Core Idea

This paper presents an **automated research reporting system** that uses local LLMs (OpenCode with DeepSeek-V4) to generate human-readable analysis reports from YOLO training metrics — turning raw CSV data into scientific narratives.

### Key Contribution
A **three-stage reporting pipeline**:
1. **Metrics Extraction** — Parse YOLO training CSV (loss, mAP, precision, recall)
2. **LLM Analysis** — Generate narrative explanation using local LLM
3. **Document Generation** — Output Markdown + DOCX with corporate branding

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TRAINING OUTPUT                       │
│  evaluation_metrics/results.csv                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STAGE 1: METRICS EXTRACTION                │
│  TrainingReportAnalyzer.analyze(csv_path)               │
│  - Parse columns: train/box_loss, val/mAP50, etc.      │
│  - Extract final epoch metrics                          │
│  - Compute deltas (improvement over epochs)             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STAGE 2: LLM ANALYSIS                      │
│  OpenCode CLI: opencode run --model deepseek-v4         │
│  - Input: CSV metrics + prompt template                 │
│  - Output: Markdown narrative analysis                  │
│  - Fallback: Deterministic CSV analysis if LLM fails    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STAGE 3: DOCUMENT GENERATION               │
│  LlmAnalyzer.__call__()                                │
│  - Save llm.md (Markdown)                              │
│  - Generate LLM_Report.docx (python-docx)              │
│  - Include branding: wtrain.jpg, wpipe.jpg, logo.jpg   │
│  - Upload to MLflow as artifacts                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔬 Experimental Setup

- **Datasets:** 50 YOLO training runs (detection + classification)
- **LLM:** OpenCode with DeepSeek-V4-Flash (free tier)
- **Evaluation:** 3 expert human evaluators (Likert 1-5 scale)
- **Metrics:** Factual accuracy, readability, completeness, time-to-generate
- **Fallback:** Deterministic CSV parser (baseline comparison)

---

## 📊 Expected Figures

1. **LLM vs. Fallback Accuracy** — Bar chart comparing factual accuracy
2. **Generation Time** — LLM (45s) vs. Fallback (0.3s) comparison
3. **Expert Evaluation Scores** — Likert scale distribution
4. **Report Example** — Side-by-side LLM vs. fallback output

---

## 📚 Key References

- OpenCode (2024) — Local LLM inference framework
- DeepSeek-V4 (2024) — Open-source LLM for code and analysis
- python-docx (2024) — DOCX generation library
- Ultralytics YOLO (2024) — Training metrics format

---

## 🛠️ Implementation Status

| Module | File | Status |
|--------|------|--------|
| LlmAnalyzer | `llm_analyzer.py` | ✅ **FUNCIONAL** |
| TrainingReportAnalyzer | `training_report_analyzer.py` | ✅ **FUNCIONAL** |
| DOCX Generator | (inline in llm_analyzer.py) | ✅ **FUNCIONAL** |

**Status:** This paper's core components are **fully implemented and functional**.

---

## 📝 Notes

- OpenCode is installed in the Docker image via `curl -fsSL https://opencode.ai/install | bash`
- The LLM generates both English and Spanish reports
- Branding images (wtrain.jpg, wpipe.jpg, logo.jpg) are included in the DOCX
- Fallback parser handles real YOLO column names (train/box_loss, val/box_loss, etc.)
- The report is automatically uploaded to MLflow as artifacts
