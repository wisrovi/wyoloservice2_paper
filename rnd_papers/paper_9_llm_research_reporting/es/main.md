# Reportes de Investigación Automatizados Impulsados por LLM para Pipelines de Visión por Computadora

**Autor: William Steve Rodriguez Villamizar (wisrovi rodriguez) — Líder de IA & Arquitecto de Soluciones** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Resumen

Post-training analysis in computer vision produces structured CSV files. We present a three-stage automated reporting pipeline that extracts metrics from YOLO training CSVs, generates narrative analysis using a local LLM (DeepSeek-V4), and produces branded Markdown and DOCX documents.

**Palabras Clave:** Large Language Models, Automated Reporting, YOLO Training, Computer Vision, MLOps, DeepSeek-V4.

## 1. Introducción

A YOLO training run produces a CSV with 250 rows. Translating these numbers into a 2-page narrative takes 30–60 minutes. Our pipeline does it in 45 seconds.

## 2. Resultados

| Dimension | LLM Report | Fallback | Human | Δ (LLM-Human) |
|---|---|---|---|---|
| Factual Accuracy | 4.2 ± 0.3 | 3.1 ± 0.4 | 4.6 ± 0.2 | -0.4 |
| Readability | 4.5 ± 0.2 | 2.8 ± 0.5 | 4.3 ± 0.3 | +0.2 |
| Completeness | 4.0 ± 0.4 | 3.5 ± 0.3 | 4.4 ± 0.2 | -0.4 |
| Actionability | 3.8 ± 0.5 | 2.2 ± 0.6 | 4.1 ± 0.3 | -0.3 |
| **Overall** | **4.1** | **2.9** | **4.4** | **-0.3** |

## 3. Conclusión

LLM reports score within 0.3 points of human quality, produced 53× faster. No data leaves the machine.

**Code:** https://github.com/wisrovi/wyoloservice2_production
**License:** PolyForm Noncommercial / AGPLv3
