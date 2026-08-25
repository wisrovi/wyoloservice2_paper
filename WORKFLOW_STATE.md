STATUS: IN_REVIEW
ROUND: 0
PAPER: paper_c_domain_shift_prediction + paper_d_autonomous_evaluation

## Reviewer status (paper_3_xai, Ronda 5)

- Veredicto Ronda 5: REVISIÓN MAYOR / RE-ENVÍO (trazabilidad numérica total lograda; aún no publicable por fallo crítico de idioma en el abstract EN y desajuste protocolo↔evidencia persistente). El re-envío corrigió: **trazabilidad total verificada** — script determinista (`random.seed(42)`, `np.random.seed(42)`), N=500, y TODAS las cifras del texto (Deletion 0.1808/IQR 0.1677–0.1935, Insertion 0.8498/IQR 0.8356–0.8636, Eigen-CAM 0.9005, Silhouette 0.6900/IQR 0.6779–0.7029, Wilcoxon p<0.0001) coinciden con la ejecución del revisor; filiación completada (rol + wisrovi-suit + ORCID); "OpenCode" → "open-source coding agent"; ablación con valores trazables (0.500/0.181/0.850/0.901); figura vectorial con decaimiento exponencial honesta; `main.md` EN/ES con figura y tabla. **Fallos persistentes:** abstract EN con fragmento en español copiado de la recomendación previa ("frente a 0.50 del baseline aleatorio") + claim "when background pixels are removed" conceptualmente incorrecto para Insertion AUC; `Experimental Setup` declara 5 seeds (42–46) × 100 pero el script usa UNA seed (42) con 500 muestras directas; Silhouette 0.6900 (Layer1) no reproducible desde el CSV pooled (0.6894); `ablation_results.csv` huérfano (50/60/95/98); ORCID placeholder; `jocher2023yolov8` mal tipada; claim "2021–2026" sin cita posterior a 2021; residuos LaTeX en References de los mds (`~`, `\,`, `{\'a}`, `$N = 500$`). Reporte completo en `IEEE_REVIEW_VERDICT.md` (sección `paper_3_xai` Ronda 5, 2026-08-17 08:52:30).
- STATUS: IN_REVIEW (REVISIÓN MAYOR; ROUND lo gestiona `run_workflow.sh`).

## Reviewer status (paper_10_outlier_failure_analysis, Ronda 3)

- Veredicto Ronda 3: REVISIÓN MAYOR / RE-ENVÍO. El manuscrito (`en/main.tex` 59 líneas, `es/main.tex` 60) es **bit a bit idéntico al de Ronda 2** (diff verificado): NO implementó ninguna de las 6 modificaciones. Sigue afirmando 12% FP / 450 HN / FP→3.5%, mientras `outlier_results.csv` muestra baseline FP 9.21%, **34** HN minados y tratamiento FP **18.79% (PEOR que control 15.07% y baseline)**; persiste el data leakage (val==train en `coco128.yaml` y en `ds.yaml`), 1 página (mínimo 3-6), 3 referencias (mínimo 8), filiación con "eCaptureDtech" (prohibido), sin `main.md` EN/ES y `figures/` vacía. Reporte completo en `IEEE_REVIEW_VERDICT.md` (sección `paper_10_outlier_failure_analysis` Ronda 3, 2026-08-16 04:18).
- STATUS: IN_REVIEW (REVISIÓN MAYOR; ROUND lo gestiona `run_workflow.sh`).

## Reviewer status (paper_2_invoker_executor, Ronda 21)

- Veredicto Ronda 21: ACEPTADO — el commit `a17fd51` (02:08) aplicó íntegramente las DOS ediciones mecánicas bloqueantes de la Ronda 20: (1) limpieza completa del `docker run` en `en/main.md:24`/`es/main.md:20` (`${mem_limit}`, `${nano_cpus}`, `${shm_size}` en Markdown plano); (2) proveniencia del CSV sincronizada en los 4 mirrors (`en/main.md:67`, `en/main.tex:85`, `es/main.md:62`, `es/main.tex:81`). Recompilación verificada por el revisor EN+ES (4 pasos): 0 errores, 0 undefined, 0 Overfull, 0 texto de control, 4 páginas/idioma; citas↔lista biunívoca 22=22; CSV verificado línea a línea (1,524 filas, 47 OOM/3.08%, memoria 10–64 GB, 14 días). Reporte completo en `IEEE_REVIEW_VERDICT.md` (Ronda 21, 2026-08-16 02:09:33). Mejoras restantes son opcionales (2 warnings bibtex por tipo `@article`→`@inproceedings`, contraste de `zhang2024slope`, muestra cruda de cgroups).
- STATUS: APPROVED (ACEPTADO para publicación IEEE; ROUND lo gestiona `run_workflow.sh`).

## Current State (2026-08-15)

- Paper C (Predicting Downstream Performance Degradation Under Representation-Level Domain Shift) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/prediction.pdf`.
- Paper D (Autonomous Evaluation Framework: Robustness, Faithful Explainability & Failure-Mode Auditing) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/xai_fidelity.pdf`.
- Both papers use real ecosystem data (7 domain pairs / XAI fidelity CSVs) and are registered in `ROADMAP.md` (entries 13 & 14) for local reviewer flow (`revisor.md`).
- Next step: run the local reviewer flow on both papers.
