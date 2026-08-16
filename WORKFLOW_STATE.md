STATUS: IN_REVIEW
ROUND: 0
PAPER: paper_c_domain_shift_prediction + paper_d_autonomous_evaluation

## Reviewer status (paper_10_outlier_failure_analysis, Ronda 2)

- Veredicto Ronda 2: REVISIÓN MAYOR / RE-ENVÍO. La evidencia aportada (`benchmark_outlier_analysis.py`, `evidencias/*.csv`, seed=42) **contradice directamente el texto**: el paper afirma 12% FP / 450 hard-negatives / FP→3.5%, pero el CSV muestra baseline FP 9.21%, **34** HN minados y tratamiento FP **18.79% (PEOR que control 15.07% y baseline)**; además hay data leakage (val==train en COCO128 y en `ds.yaml`), sigue siendo 1 página (mínimo 3-6), 3 referencias (mínimo 8), filiación con "eCaptureDtech" (prohibido), sin `main.md` EN/ES ni figuras. Reporte completo en `IEEE_REVIEW_VERDICT.md` (sección `paper_10_outlier_failure_analysis` Ronda 2, 2026-08-16 04:13).
- STATUS: IN_REVIEW (REVISIÓN MAYOR; ROUND lo gestiona `run_workflow.sh`).

## Reviewer status (paper_2_invoker_executor, Ronda 21)

- Veredicto Ronda 21: ACEPTADO — el commit `a17fd51` (02:08) aplicó íntegramente las DOS ediciones mecánicas bloqueantes de la Ronda 20: (1) limpieza completa del `docker run` en `en/main.md:24`/`es/main.md:20` (`${mem_limit}`, `${nano_cpus}`, `${shm_size}` en Markdown plano); (2) proveniencia del CSV sincronizada en los 4 mirrors (`en/main.md:67`, `en/main.tex:85`, `es/main.md:62`, `es/main.tex:81`). Recompilación verificada por el revisor EN+ES (4 pasos): 0 errores, 0 undefined, 0 Overfull, 0 texto de control, 4 páginas/idioma; citas↔lista biunívoca 22=22; CSV verificado línea a línea (1,524 filas, 47 OOM/3.08%, memoria 10–64 GB, 14 días). Reporte completo en `IEEE_REVIEW_VERDICT.md` (Ronda 21, 2026-08-16 02:09:33). Mejoras restantes son opcionales (2 warnings bibtex por tipo `@article`→`@inproceedings`, contraste de `zhang2024slope`, muestra cruda de cgroups).
- STATUS: APPROVED (ACEPTADO para publicación IEEE; ROUND lo gestiona `run_workflow.sh`).

## Current State (2026-08-15)

- Paper C (Predicting Downstream Performance Degradation Under Representation-Level Domain Shift) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/prediction.pdf`.
- Paper D (Autonomous Evaluation Framework: Robustness, Faithful Explainability & Failure-Mode Auditing) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/xai_fidelity.pdf`.
- Both papers use real ecosystem data (7 domain pairs / XAI fidelity CSVs) and are registered in `ROADMAP.md` (entries 13 & 14) for local reviewer flow (`revisor.md`).
- Next step: run the local reviewer flow on both papers.
