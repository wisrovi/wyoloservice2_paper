STATUS: IN_REVIEW
ROUND: 0
PAPER: paper_c_domain_shift_prediction + paper_d_autonomous_evaluation

## Reviewer status (paper_2_invoker_executor, Ronda 12)

- Veredicto Ronda 12: REVISIÓN MAYOR (Re-envío). Ronda 11 CERRADA y verificada en los 3 mirrors: sincronía `.tex`↔`.md` byte-a-byte EN/ES, `\Cref{fig:arch}` simétrico sin fugas LaTeX, listas renderizando, figura PNG (2550×3300), `Mäntylä` correcto, 0 errores de compilación (EN 4 / ES 3 páginas). NUEVOS hallazgos (bloqueantes para ACCEPT bajo `revisor.md`): `Results & Discussion` 100% cualitativo (cero métricas numéricas), sin tablas (`booktabs` cargado y sin uso), sin estudio de ablación, Data & Code sin comandos de despliegue, ausencia de sección Experimental Setup, y vacíos de estado del arte (Celery/Docker, literatura GPU 2021–2024).
- STATUS: IN_REVIEW (REVISIÓN MAYOR — debe permanecer hasta cerrar la lista Ronda 12).

## Current State (2026-08-15)

- Paper C (Predicting Downstream Performance Degradation Under Representation-Level Domain Shift) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/prediction.pdf`.
- Paper D (Autonomous Evaluation Framework: Robustness, Faithful Explainability & Failure-Mode Auditing) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/xai_fidelity.pdf`.
- Both papers use real ecosystem data (7 domain pairs / XAI fidelity CSVs) and are registered in `ROADMAP.md` (entries 13 & 14) for local reviewer flow (`revisor.md`).
- Next step: run the local reviewer flow on both papers.
