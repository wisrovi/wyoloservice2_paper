# Rigor Estadístico en Evaluación de Modelos YOLO

**Autor: William Steve Rodriguez Villamizar (wisrovi rodriguez) — Líder de IA & Arquitecto de Soluciones** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Resumen

Reporting a single mAP value after YOLO training conveys no information about whether observed differences between models are real or artifacts of random seed variation. We present a statistical validation pipeline combining bootstrap resampling (1000 iterations, 95% CI), failure mode analysis via FiftyOne, and Wilcoxon signed-rank tests.

**Palabras Clave:** Bootstrap Resampling, Statistical Significance, YOLO Evaluation, Failure Mode Analysis, Wilcoxon Test, Confidence Intervals.

## 1. Introducción

Of 5 apparent mAP improvements (0.3–1.1%), only 2 survive bootstrap CI analysis and Wilcoxon testing at α=0.05. Without statistical validation, 60% of claims are overconfident.

## 2. Resultados

| Dataset | mAP Diff (%) | CI Lower | CI Upper | Significant? |
|---|---|---|---|---|
| Defect Det. | +0.8 | +0.2 | +1.4 | **Yes** |
| Satellite | +0.3 | -0.4 | +1.0 | No |
| Medical Cells | +1.1 | +0.5 | +1.7 | **Yes** |
| Driving | +0.5 | -0.3 | +1.3 | No |
| Agriculture | +0.4 | -0.5 | +1.2 | No |

## 3. Conclusión

Only 2 of 5 improvements are statistically significant. The pipeline executes in 12 seconds.

**Code:** https://github.com/wisrovi/wyoloservice2_production
**License:** PolyForm Noncommercial / AGPLv3
