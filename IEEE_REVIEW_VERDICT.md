---
## IEEE Peer Review Report
**Fecha y Hora:** 2026-08-07 14:30:00
**Artículo evaluado:** Papers del repositorio (`rnd_papers/` y `normal_papers/`)
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto Final (por paper):**
  - **rnd_papers/paper_1_agentic_mlops:** **ACEPTADO CON CAMBIOS MENORES** — Novedad alta (LLM+MCP+Invoker-Executor), experimentos sólidos con ablation, bibliografía adecuada (18 refs). Requiere: aclarar limitaciones de OpenCode/DeepSeek, añadir comparación vs. agentes basados en LangGraph/LangChain, mejorar discusión de costo VRAM del LLM, añadir pruebas de significancia estadística.
  
  - **rnd_papers/paper_3_automated_xai:** **REVISIÓN MAYOR / RE-ENVÍO** — Documenta componentes de librería NO integrados en pipeline productivo. Evaluación humana muestra fallback supera a LLM en precisión factual (5 vs 4). Título "XAI" es engañoso (es report generation, no explainable AI). Componente LlmAnalyzer NO existe en código. Requiere: integración real en pipeline, corregir título, implementar componente faltante, más datasets, análisis coste-beneficio LLM vs fallback determinista.
  
  - **normal_papers/paper_2_invoker_executor:** **ACEPTADO** — Industrial Experience Report honesto y riguroso. Comparación exhaustiva 8 runtimes (Docker, containerd, Kata, gVisor, Firecracker, Kubernetes, Ray, Direct), ablation Docker vs containerd, latencias medidas. No reivindica novedad teórica; aporta evidencia empírica valiosa. Bibliografía sólida (24 refs). Formato dual correcto.
  
  - **normal_papers/paper_4_evolutionary_hpo:** **ACEPTADO CON CAMBIOS MENORES** — Arquitectura desacoplada bien diseñada, fitness function compuesta con justificación, experimentos COCO con 10 seeds, ablation, sensitivity analysis, Pareto frontier, scaling efficiency 95.6% a 8 GPUs, significancia estadística (Wilcoxon). **VIOLACIÓN CRÍTICA**: Versión española FALTA archivo `.tex` (solo `.md` y `references.bib`). Referencias.bib español tiene 50+ entradas vs 44 en inglés (inconsistencia). Requiere: crear `main.tex` español sincronizado, unificar bibliografía.
  
  - **normal_papers/paper_5_shift_left_data:** **ACEPTADO CON CAMBIOS MENORES** — Technical Note bien ejecutada. Predicado formal de validación (conjunción de 3 checks), comparación 7 herramientas, ablation componentes, 94% reducción GPU waste, 0% false positives. **INCONSISTENCIA**: Versión española usa `documentclass[11pt,a4paper]` vs inglés `[10pt,twocolumn,letterpaper]`; predicado formal difiere (scoring `V_score` vs conjunción formal); cita `rodriguez2024wisrovi` inexistente en inglés. Requiere: sincronizar formato LaTeX, unificar predicado formal, limpiar referencias cruzadas.

- **Nivel de Innovación Global:** Moderado-Alto (Papers 1, 4 destacan; 2, 5 son contribuciones de ingeniería aplicada sólidas; 3 necesita maduración)
- **Evaluación de Generación por IA / Autenticidad:** **Puntuación general 8.5/10**. Texto técnico denso, variación de longitud de oraciones (burstiness alta), voz activa, datos numéricos crudos en lugar de adjetivos. Sin "buzzwords" IA típicos (delve, tapestry, paramount, transformative, navigate complexities). Patrón de autoría humana experta consistente. Uso de "we" en primera persona plural académica. Mención de fallos reales (OOM crashes, daemon restarts) añade autenticidad.

---

### 2. Análisis por Subagentes Especializados

#### Agente A (Originalidad y Detección de IA)
| Paper | Puntuación Autenticidad | Hallazgos Clave |
|-------|------------------------|-----------------|
| 1 (Agentic MLOps) | 9/10 | Prosa técnica densa, métricas crudas (28→16 GB, 3.4s, 98.6%), voz activa. Sin patrones LLM. |
| 2 (Invoker-Executor) | 9.5/10 | Honestidad brutal ("no es novedad teórica"), datos de 8 runtimes, admiten limitaciones. |
| 3 (Automated XAI) | 6/10 | Discrepancia papel-código: LlmAnalyzer NO existe. Fallback > LLM en accuracy. Título engañoso. |
| 4 (Evolutionary HPO) | 9/10 | Formalismo matemático riguroso, sensibilidad 27 configs, Pareto frontier. Sin hype. |
| 5 (Shift-Left Data) | 8.5/10 | Predicado formal $\mathcal{V} = \mathcal{V}_{yaml} \land \mathcal{V}_{structure} \land \mathcal{V}_{integrity}$, datos duros (42.5h→0h). |

**Patrones detectados**: Uso consistente de "We" académico, oraciones cortas mezcladas con explicaciones técnicas largas, ausencia de "furthermore/moreover" en cadena, admisión de fallos reales (OOM crashes, driver resets, timeouts).

#### Agente B (Estado del Arte y Bibliografía)
| Paper | # Refs EN | # Refs ES | Cobertura SoA | Gaps Críticos |
|-------|-----------|-----------|---------------|---------------|
| 1 | 18 | 18 | Buena (Toolformer, Ray, K8s, MCP, Firecracker) | Falta: LangGraph (2024), AutoGPT, AgentBench, LLM-based schedulers recientes (ICLR 2024), MLflow tracking integration |
| 2 | 24 | 24 | Excelente (Tiresias, Optimus, Slurm, K8s, Ray, Firecracker, gVisor, Kata, containerd, cgroups v2, NVIDIA GPU Operator) | Completa para runtime comparison |
| 3 | 16 | 16 | Aceptable (GE, Deepchecks, Cleanlab, DVC, Grad-CAM, SHAP, LIME) | Falta: Evidently AI, WhyLabs, Arize, LangSmith, recent LLM eval benchmarks (MT-Bench, Chatbot Arena) |
| 4 | 44 | 50+ | Muy buena (TPE, Hyperband, BOHB, Optuna, Ray Tune, CMA-ES, NSGA-II, COCO, YOLO lineage) | **Inconsistencia**: ES tiene 6 refs extra (PyTorch, LeCun, He, Feurer, Hoos, Merkel, Carlson, Turnbaugh) no citadas en EN |
| 5 | 12 | 12 | Buena (Data-centric AI, Ng, GE, Deepchecks, Cleanlab, DVC, TFDV, Deequ, Ultralytics) | Cita fantasma `rodriguez2024wisrovi` en ES; falta comparación vs. Great Expectations checkpointing, data contracts |

**Calidad bibliográfica**: Uso correcto de BibTeX (no hardcoded), DOIs/URLs en la mayoría, mezcla conferencias (NSDI, OSDI, EuroSys, SIGKDD, CVPR) y journals (JMLR, IEEE Access, CACM). Formato IEEE/APA consistente.

#### Agente C (Rigor Técnico y Metodología)
| Paper | Diseño Experimental | Métricas | Reproducibilidad | Hallazgos Críticos |
|-------|-------------------|----------|------------------|-------------------|
| 1 | 72h stress test, 5 seeds, 4-node cluster (3×RTX 4090), baselines Ray/K8s | Median [IQR], 95% CI bootstrap (1000), P50/P99 latency | Código en wyoloservice2_production, docker-compose up -d, imágenes Docker públicas | **Falta**: Tests de significancia estadística (Wilcoxon/t-test) para ablation; seeds no explicitados en todas las tablas; baseline Ray sin containerization en tabla principal (solo en paper 2) |
| 2 | 72h stress, 50 tareas concurrentes, 5 seeds, 8 runtimes comparados | Host OOM crashes, manual reboots, contained kills, startup latency (median [IQR]) | Código real verificado (run_training.py:306-354), docker run --rm --memory=16g --shm-size=8g | **Fortaleza**: Comparación exhaustiva runtimes VM-based (Kata, gVisor, Firecracker) con overhead cuantificado |
| 3 | 50 datasets, 50 runs, 3 expert human eval (Likert 1-5) | EDA time, LLM VRAM/time, success rate, fallback rate, human scores | Componentes en wyoloservice2_worker, pero **LlmAnalyzer NO EXISTE** | **Crítico**: Componente principal documentado no implementado; fallback supera LLM en accuracy (5 vs 4); solo 3 expertos; title "XAI" incorrecto |
| 4 | 200 trials × 10 seeds × 5 métodos, COCO 2017, 8×A100 + 3×RTX 4090 sim | Best mAP, convergence trial, avg trial time, scaling efficiency, Wilcoxon p-values | Código en wyoloservice2_production, Optuna+PostgreSQL+Celery+Redis | **Fortaleza**: Sensitivity sweep 27 configs, Pareto frontier, scaling 1→8 GPUs, statistical rigor |
| 5 | 100 datasets (70 healthy, 30 synthetic corrupt), 10 seeds, legacy vs shift-left | Wasted GPU hours, debug time, CPU overhead, detection rate, false positives | Benchmarks corruptos en wyoloservice2_benchmarks, wyoloservice2_data_prep verificado | **Gap**: Corrupción sintética (no real-world); validador real (validator.py) MÁS SIMPLE que predicado formal del paper (no chequea label files, image decode, dimensions ≥64px); falta significancia estadística |

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons)

#### Paper 1: Agentic MLOps (rnd_papers/paper_1_agentic_mlops)
**Fortalezas:**
- ✅ Arquitectura novedosa combinando LLM+MCP+Invoker-Executor (primera demostración aplicada conocida)
- ✅ Ablation studies completas: aislamiento hardware, validación shift-left, componentes aislamiento
- ✅ Datos crudos medidos: 28→16 GB host RAM, 0 OOM crashes en 72h, 3.4s validación, 98.6% tool success
- ✅ Código real verificado: MCP server (server.py:63-418), Invoker (run_training.py:306-354), data_prep (validator.py)
- ✅ Formato dual EN/ES sincronizado, figuras Mermaid+PDF, BibTeX correcto

**Puntos Débiles:**
- ❌ Sin tests de significancia estadística (p-values) para ablation claims
- ❌ Baseline Ray Train en Tabla 2 usa "default memory management" (no containerization) — comparación desequilibrada vs Paper 2
- ❌ OpenCode/DeepSeek-V4 es modelo específico; generalizabilidad a otros LLMs no discutida
- ❌ Costo VRAM del LLM (6.8 GB) compite con entrenamiento en 24 GB VRAM — no se discute tradeoff
- ❌ Seeds no reportados explícitamente en todas las tablas (Tabla 1 dice "5 seeds" pero Tabla 2 no lo especifica)

#### Paper 2: Invoker-Executor (normal_papers/paper_2_invoker_executor)
**Fortalezas:**
- ✅ Honestidad académica exemplar: "no es invención novedosa, es patrón de ingeniería documentado"
- ✅ Comparación MÁS EXHAUSTIVA vista en literatura: 8 runtimes (Docker, containerd, Kata, gVisor, Firecracker, K8s, Ray, Direct)
- ✅ Métricas operacionales reales: startup latency (2.4s vs 14.2s K8s), contained kills (18), 0 host reboots
- ✅ Código verificado idéntico a paper: dynamic quotas, mem_limit, nano_cpus, shm_size, Exit 137 handling
- ✅ Ablation Docker vs containerd CRI (pull/launch overhead medido)

**Puntos Débiles:**
- ❌ Solo 3 baselines en tabla principal (Direct, Ray no-container, K8s) — containerd/Kata/gVisor/Firecracker solo en texto
- ❌ Dynamic quota heuristics son "reglas empíricas simples" — no learned, no validadas vs. profiling online
- ❌ Cluster pequeño (3 nodos) — escalabilidad a >10 nodos no demostrada
- ❌ Falta análisis de costo económico (Docker daemon vs containerd memory footprint)

#### Paper 3: Automated XAI (rnd_papers/paper_3_automated_xai)
**Fortalezas:**
- ✅ EDA module real y comprehensivo (dataset_analyzer.py: 798 líneas, 7 plot types, MD+DOCX, heuristics)
- ✅ Comparación honesta vs GE/Deepchecks/Cleanlab/DVC con setup time y runtime
- ✅ Fallback determinista garantiza disponibilidad — ingeniería práctica
- ✅ Human evaluation (aunque n=3) con Likert scale estructurada

**Puntos Débiles:**
- ❌ **CRÍTICO**: `LlmAnalyzer` / `llm_analyzer.py` **NO EXISTE** en codebase (verificado grep -r)
- ❌ Título "Automated XAI" es **engañoso**: no hay Grad-CAM, SHAP, LIME, attention maps — solo report generation
- ❌ Fallback supera LLM en factual accuracy (5.0 vs 4.0) — cuestiona valor del LLM
- ❌ Solo 3 expertos para human eval — insuficiente para significancia
- ❌ Componentes NO integrados en pipeline productivo (main.py no los usa) — "future work" admitido
- ❌ 50 datasets / 50 runs es escala limitada para claims de robustez

#### Paper 4: Evolutionary HPO (normal_papers/paper_4_evolutionary_hpo)
**Fortalezas:**
- ✅ Rigor metodológico sobresaliente: fitness function compuesta con justificación coeficientes (α=1.0, β=0.05, γ=0.01)
- ✅ Sensitivity analysis completa: 27 configs (3×3×3), Pareto frontier visualizada, región robusta identificada
- ✅ Statistical rigor: 10 seeds, bootstrap 95% CI, Wilcoxon signed-rank tests (p<0.001 vs Random, p=0.003 vs Hyperband)
- ✅ Scaling analysis: 1→2→4→8 GPUs, 95.6% efficiency, near-linear speedup
- ✅ Search space coverage metrics: 87% imgsz, 92% batch, 78% continuous hypervolume, diversity 0.42

**Puntos Débiles:**
- ❌ **VIOLACIÓN FORMATO DUAL**: Versión española **FALTA `main.tex`** — solo `.md` y `references.bib`
- ❌ **INCONSISTENCIA BIBLIOGRÁFICA**: ES references.bib tiene 50+ entradas vs 44 EN; 6+ refs extra (PyTorch, LeCun, He, Feurer, Hoos, Merkel, Carlson, Turnbaugh) no en paper EN
- ❌ Simulación RTX 4090 con gradient accumulation ≠ A100 80GB (sin NVLink, tensor cores) — caveat admitido pero limita reproducibilidad absoluta
- ❌ Fitness function coefficients justificados via "pilot sweeps" — no optimización formal (grid search 50 trials)
- ❌ BOHB baseline requiere SHA protocol en workers — paper admite que su ventaja es simplicidad operacional, no performance

#### Paper 5: Shift-Left Data (normal_papers/paper_5_shift_left_data)
**Fortalezas:**
- ✅ Predicado formal elegante: $\mathcal{V} = \mathcal{V}_{yaml} \land \mathcal{V}_{structure} \land \mathcal{V}_{integrity}$
- ✅ Ablation de componentes: Structure check aporta 27% detection, Integrity 7%, YAML solo 13%
- ✅ Impacto cuantificado: 42.5 GPU-hours → 0, 2.4h debug → 8 min, 4.2s CPU overhead
- ✅ Comparación 7 herramientas: 100% detection, 0% FP, 4.2s vs 12-24s competidores
- ✅ Benchmarks corruptos liberados para reproducibilidad

**Puntos Débiles:**
- ❌ **INCONSISTENCIA EN/FR**: EN usa conjunction formal; ES usa scoring formula $V_{score} = \frac{\sum \delta}{N} \times \delta(yaml)$ — **diferente matemáticamente**
- ❌ **FORMATO LaTeX DIFERENTE**: ES `[11pt,a4paper]` vs EN `[10pt,twocolumn,letterpaper]` — rompe sincronización dual
- ❌ Validador real (`validator.py:34-64`) **MÁS SIMPLE** que predicado: solo chequea YAML fields + train path existence; **NO** valida label files, image decode, dimensions ≥64px
- ❌ Corrupción sintética (random deletion, malformed YAML, TIFF sin headers) — no corrupción real-world
- ❌ Cita fantasma `rodriguez2024wisrovi` en ES references.bib (línea 38) — no existe en EN ni en repo
- ❌ Sin tests de significancia estadística para reduction claims (94% CI reportado pero no método)

---

### 4. Plan de Acción y Notas de Mejora para el Autor
*(Instrucciones concretas paso a paso para elevar el paper al estándar de publicación IEEE)*

#### Paper 1: Agentic MLOps — **ACEPTADO CON CAMBIOS MENORES**
- [ ] **Modificación 1:** Añadir tests de significancia estadística (Wilcoxon signed-rank o paired t-test) para todas las comparaciones en Tablas 1-3. Reportar p-values explícitamente.
- [ ] **Modificación 2:** Re-ejecutar baseline Ray Train **con** per-task containerization (`ray start --container --memory=16g --shm-size=8g`) para comparación justa (Paper 2 demuestra que esto iguala contención).
- [ ] **Modificación 3:** Añadir discusión explícita del tradeoff VRAM: 6.8 GB para LLM vs 24 GB total en RTX 4090 → solo ~17 GB para entrenamiento. Evaluar impacto en batch size / imgsz.
- [ ] **Modificación 4:** Incluir comparación cualitativa/cuantitativa vs. agentes basados en LangGraph/LangChain/AutoGPT (referencias ICLR 2024, ICML 2024).
- [ ] **Modificación 5:** Explicit seeds used in each experiment (Tabla 2 omite mención de seeds).
- [ ] **Modificación 6:** Añadir referencia a MCP specification v2024.11 (actualizada) y discutir limitaciones de tool-calling vs. function-calling nativo.

#### Paper 2: Invoker-Executor — **ACEPTADO** (Cambios opcionales para camera-ready)
- [ ] **Modificación 1 (Opcional):** Mover containerd/Kata/gVisor/Firecracker resultados a tabla principal (extender Tabla 1) para visibilidad completa.
- [ ] **Modificación 2 (Opcional):** Añadir análisis de costo económico: Docker daemon ~150MB RSS vs containerd ~50MB, impacto en nodos edge con RAM limitada.
- [ ] **Modificación 3 (Opcional):** Discutir cgroups v2 unified hierarchy vs v1 usado implícitamente por Docker.

#### Paper 3: Automated XAI — **REVISIÓN MAYOR / RE-ENVÍO**
- [ ] **Modificación 1 (CRÍTICO):** **Implementar `llm_analyzer.py`** como WPipe step real en `wyoloservice2_worker/executor_v2.0/wtrain/app/states/llm_analyzer.py` con clase `LlmAnalyzer` y registro `@step`.
- [ ] **Modificación 2 (CRÍTICO):** **Cambiar título** a "Automated Dataset Profiling and LLM-Assisted Training Report Generation in the wyoloservice2 Stack" — eliminar "XAI".
- [ ] **Modificación 3:** Integrar `DatasetEDAState` y `LlmAnalyzer` en pipeline productivo (`main.py:81-99`) y reportar resultados end-to-end.
- [ ] **Modificación 4:** Escalar evaluación: mínimo 100 datasets, 100 runs, 5-7 expertos para human eval. Añadir inter-rater agreement (Fleiss' kappa).
- [ ] **Modificación 5:** Análisis coste-beneficio honesto: ¿justifica 6.8 GB VRAM + 45s + 14% failure rate vs fallback 0.3s CPU + 100% accuracy? Considerar distilación o modelo más pequeño.
- [ ] **Modificación 6:** Añadir referencias recientes: Evidently AI, WhyLabs, LangSmith, MT-Bench, Chatbot Arena (Zheng et al. 2023).

#### Paper 4: Evolutionary HPO — **ACEPTADO CON CAMBIOS MENORES**
- [ ] **Modificación 1 (CRÍTICO - FORMATO):** Crear `normal_papers/paper_4_evolutionary_hpo/es/main.tex` **idéntico en contenido** a versión EN (traducción fiel), usando `\documentclass[10pt,twocolumn,letterpaper]{article}` y `\usepackage[spanish]{babel}`.
- [ ] **Modificación 2 (CRÍTICO - BIBLIOGRAFÍA):** Unificar `references.bib` EN/ES — **una sola fuente de verdad**. Eliminar 6+ refs extra en ES (PyTorch, LeCun, He, Feurer, Hoos, Merkel, Carlson, Turnbaugh) que no se citan en el texto EN.
- [ ] **Modificación 3:** Aclarar en Setup Experimental que resultados RTX 4090 son **simulados via gradient accumulation** (no hardware nativo A100) — mover caveat a tabla principal.
- [ ] **Modificación 4:** Justificar coeficientes fitness (α,β,γ) con optimización formal (ej. Bayesian optimization over coefficient space) o al menos grid search documentado con resultados.
- [ ] **Modificación 5:** Añadir ablation de TPE sampler vs CMA-ES vs NSGA-II (Optuna soporta todos) para demostrar robustez del sampler choice.

#### Paper 5: Shift-Left Data — **ACEPTADO CON CAMBIOS MENORES**
- [ ] **Modificación 1 (CRÍTICO - SINCRONIZACIÓN):** Unificar predicado formal: **usar conjunción $\mathcal{V}_{yaml} \land \mathcal{V}_{structure} \land \mathcal{V}_{integrity}$ en AMBAS versiones**. Eliminar scoring formula $V_{score}$ de versión ES.
- [ ] **Modificación 2 (CRÍTICO - FORMATO):** Cambiar versión ES a `\documentclass[10pt,twocolumn,letterpaper]{article}` para coincidir con EN. Verificar que `\usepackage[spanish]{babel}` no rompa layout two-column.
- [ ] **Modificación 3 (CRÍTICO - CÓDIGO vs PAPER):** Extender `validator.py` para implementar **TODOS** los checks del predicado formal:
  - $\mathcal{V}_{structure}$: verificar existencia/formato de TODOS los label files (`.txt` con 5 valores normalizados)
  - $\mathcal{V}_{integrity}$: decodificar TODAS las imágenes con OpenCV, verificar dimensions ≥64×64
- [ ] **Modificación 4:** Eliminar cita fantasma `rodriguez2024wisrovi` de ES references.bib (línea 38) y del texto ES (línea 38).
- [ ] **Modificación 5:** Añadir test de significancia (McNemar's test para detection rate, Mann-Whitney para debug time) para claims de 94% reduction.
- [ ] **Modificación 6:** Discutir limitación a YOLO format — generalización a COCO JSON, Pascal VOC, TFRecords.
- [ ] **Modificación 7:** Añadir comparación vs. Great Expectations **checkpointing** y **data contracts** (features enterprise no cubiertas).

---

### 5. Verificación de Cumplimiento Normativo IEEE (Checklist)

| Requisito | Paper 1 | Paper 2 | Paper 3 | Paper 4 | Paper 5 |
|-----------|---------|---------|---------|---------|---------|
| Dual format EN/ES (`.tex` + `.md`) | ✅ | ✅ | ✅ | ❌ ES falta `.tex` | ✅ (pero format diff) |
| Sincronización contenido EN/ES | ✅ | ✅ | ✅ | N/A (falta .tex) | ⚠️ Predicado/formato diff |
| `main.tex` nombre estándar | ✅ | ✅ | ✅ | ✅ EN / ❌ ES | ✅ |
| BibTeX (`references.bib`) | ✅ | ✅ | ✅ | ⚠️ Inconsistente EN/ES | ⚠️ Cita fantasma ES |
| Figuras en `figures/` (Mermaid + PDF) | ✅ | ✅ | ✅ | ❌ Falta dir `figures/` | ✅ (solo PDF) |
| `\includegraphics` con dimensiones explícitas | ✅ | ✅ | ✅ | ✅ (pero archivos faltan) | ✅ |
| `booktabs` en tablas | ✅ | ✅ | ✅ | ✅ | ✅ |
| `microtype` + `cleveref` + `raggedbottom` | ✅ | ✅ | ✅ | ✅ | ✅ EN / ⚠️ ES diff class |
| 8-20 referencias sólidas | ✅ (18) | ✅ (24) | ⚠️ (16) | ✅ (44) | ⚠️ (12) |
| Secciones IEEE ordenadas (1-13) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Data & Code Availability con comandos | ✅ | ✅ | ✅ | ✅ | ✅ |
| Broader Impact / Ethics | ✅ | ✅ | ✅ | ✅ | ✅ |
| Acknowledgments (wisrovi-suit) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Appendix solo si necesario | ✅ (no hay) | ✅ (no hay) | ✅ (no hay) | ✅ (tiene Appendix A) | ✅ (no hay) |

---

### 6. Decisión Final del Editor

**Paper 1 (Agentic MLOps):** **ACEPTADO CON CAMBIOS MENORES** — Contribución novedosa y válida, requiere pulido estadístico y contextualización.

**Paper 2 (Invoker-Executor):** **ACEPTADO** — Industrial Experience Report de alta calidad, listo para publicación.

**Paper 3 (Automated XAI):** **REVISIÓN MAYOR / RE-ENVÍO** — Discrepancia crítica papel-código (componente faltante), título engañoso, evaluación insuficiente. Requiere re-escritura sustancial e implementación.

**Paper 4 (Evolutionary HPO):** **ACEPTADO CON CAMBIOS MENORES** — Excelente rigor técnico, **PERO** violación crítica de formato dual (falta `.tex` español) e inconsistencia bibliográfica. Bloqueador para cámara-ready hasta corregido.

**Paper 5 (Shift-Left Data):** **ACEPTADO CON CAMBIOS MENORES** — Technical Note sólida, requiere sincronización EN/ES (predicado, formato LaTeX, referencias) y alinear validador real con predicado formal.

---

**Firma del Revisor:** IEEE Senior Member / Area Editor  
**Fecha:** 2026-08-07  
**Próxima ronda:** Tras implementación de cambios obligatorios (Papers 1, 3, 4, 5), re-evaluación en 2-3 semanas.