STATUS: IN_REVIEW
ROUND: 0
PAPER: paper_c_domain_shift_prediction + paper_d_autonomous_evaluation

## Reviewer status (paper_2_invoker_executor, Ronda 11)

- Veredicto Ronda 11: CAMBIOS MENORES (Ronda 10 cerrada: duplicación ES eliminada en `.tex`/`.md`/`.pdf`; `orcid.pdf` real ≠ arquitectura; `Mäntylä` correcto; `\Cref{fig:arch}` en `en/main.tex`. NUEVOS hallazgos: desincronismo CRÍTICO `.tex`↔`.md` en la Introducción EN (párrafo 2º) y ES (párrafo completo) — el `.md` conserva la variante antigua "proprietary stack"/"pila propietaria"; `\Cref` asimétrico (falta en `es/main.tex` y fuga LaTeX en `en/main.md:26`); lista Metodología `.md` como bloque de código; figura `.pdf` no renderizable en GitHub).
- STATUS: IN_REVIEW (debe permanecer hasta cerrar la lista Ronda 11).

## Current State (2026-08-15)

- Paper C (Predicting Downstream Performance Degradation Under Representation-Level Domain Shift) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/prediction.pdf`.
- Paper D (Autonomous Evaluation Framework: Robustness, Faithful Explainability & Failure-Mode Auditing) drafted and compiled: EN/ES, LaTeX + Markdown + PDF, vector figure `figures/xai_fidelity.pdf`.
- Both papers use real ecosystem data (7 domain pairs / XAI fidelity CSVs) and are registered in `ROADMAP.md` (entries 13 & 14) for local reviewer flow (`revisor.md`).
- Next step: run the local reviewer flow on both papers.
