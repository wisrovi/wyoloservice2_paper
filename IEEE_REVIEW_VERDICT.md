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
---

## IEEE Peer Review Report — paper_6_llm_reporting
**Fecha y Hora:** 2026-08-12 15:30:00
**Artículo evaluado:** `normal_papers/paper_6_llm_reporting`
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** RECHAZADO — re-envío requerido tras correcciones mayores
- **Nivel de Innovación:** Bajo-Moderado
- **Evaluación de Generación por IA / Autenticidad:** 5.5/10 — prosa técnica correcta y con voz activa, pero con marcas de narrativa generada y, sobre todo, **cifras presentadas como mediciones experimentales que provienen de valores MOCK/aleatorios en el código fuente**.

**Hallazgo crítico (integridad científica):** El pipeline `LlmAnalyzer` sí existe y está integrado como último WPipe step en `post_train_pipeline.py:67`, y usa OpenCode con `opencode/deepseek-v4-flash-free` (`llm_analyzer.py:134`, `training_report_analyzer.py:100`). Sin embargo, **TODOS los números de la sección Results son fabricados por los estados forenses**, no medidos:

| Métrica reportada en el paper | Origen real en código |
|---|---|
| Deletion AUC 0.128 / Insertion 0.724 | `quantitative_xai_validator.py:47` → `random.uniform(0.1, 0.3)` / `random.uniform(0.7, 0.95)` |
| FGSM 26% success @ε=0.01 | `adversarial_attack_tester.py:41,45` → "Actual execution is mocked/skipped" + `random.uniform(0.1, 0.4)` |
| Ruido 0.95→0.30 | `robustness_noise_evaluator.py:78,81` → "Skipped for now, mock result" + dictado hardcoded `{0:0.95,...,5:0.30}` |
| FID 29.1 | `cross_domain_generalizer.py:49` → `random.uniform(15.0, 35.0)` |
| Silhouette 0.581 / PCA 0.869 | `feature_representation_analyzer.py:66` → `random.uniform(0.4, 0.7)` / `random.uniform(0.85, 0.98)` |
| MC-Dropout varianza 0.0648, 20 passes | `uncertainty_quantifier.py:48` → `random.uniform(0.05, 0.2)`, `mc_passes: 20` hardcoded |
| mAP50 (model_metrics) | `model_complexity_profiler.py:99-100` → `random.uniform(0.85, 0.99)` |

Es decir, el LLM interpreta **ruido aleatorio generado por `random.uniform()`** y el paper vende esa interpretación como validación experimental. El abstract también afirma "87% reduction in manual interpretation time" sin metodología de medición, y `main.md` añade "95% narrative fidelity" y "98% trials / 14% hallucination" que NO existen en `main.tex` — tres narrativas de resultados distintas entre sí.

**Otros bloqueadores:** (a) solo 2 referencias en `references.bib` (mínimo 8-20); (b) formato dual roto — `es/` carece de `references.bib` y `main.md`; (c) `en/main.tex` vs `en/main.md` desincronizados (Resultados y Abstract divergen); (d) `figures/` vacío en EN y ES, cero figuras y cero tablas; (e) "70 GPU nodes" inconsistente con la infraestructura verificable (`MAX_GPU=30`, ~3-5 IPs de worker en config); (f) sin sección formal de Ablation Study con datos; (g) el DOCX corporativo se genera desde `TrainingReportAnalyzer` sobre `results.csv`, no desde `GLOBAL_RESEARCH_EXPLANATION.md` como afirma el paper.

---

### 2. Análisis por Subagentes Especializados

#### Agente A (Originalidad y Detección de IA) — 5.5/10
- Prosa con voz activa y oraciones de longitud variable (p. ej., "It even detected a profiling anomaly...").
- **Red flags de narrativa generada**: secuencia "Furthermore, the LLM synthesized... It even detected... Overall..." suena a resumen auto-generado (posiblemente el propio LLM describiendo su output); repetición del mismo patrón EN/ES casi literal.
- Originalidad metodológica débil: "un LLM lee JSON y escribe Markdown/DOCX" con DeepSeek-V4 local vía OpenCode no constituye contribución novedosa per se; el valor debería estar en la validación empírica, que está ausente.
- **Peor defecto de autenticidad**: presentar datos mock/random como experimentales es un fallo de integridad académica, más grave que cualquier patrón sintáctico.

#### Agente B (Estado del Arte y Bibliografía) — 1.5/10
- **Solo 2 referencias** (`jing2017automatic`, `brown2020language`), ambas correctas pero insuficientes. Violación del mínimo 8-20 de las normas del repositorio y de cualquier estándar IEEE razonable.
- Gaps críticos: sin literatura de XAI (Selvaraju et al. Grad-CAM; Samek et al.), MC Dropout (Gal & Ghahramani 2016), FGSM (Goodfellow et al. 2015), FID (Heusel et al. 2017), MLOps/MLflow tracking, evaluación de alucinaciones (HaluEval, TruthfulQA), LLM agents (ReAct, Toolformer), y trabajos de report generation LLM-based (2023-2025).
- `main.md` elimina las citas (`\cite`), rompiendo la sincronización bibliográfica EN/ES y EN tex/md.

#### Agente C (Rigor Técnico y Metodología) — 2/10
- **Métricas fraudulentas por simulación**: ver tabla del resumen. Ninguna métrica reportada es resultado de una medición real.
- Cluster claim "70 GPU nodes" no verificable; la config real (`wyoloservice2_manager/app/config.yaml`, `control_host.env`) muestra `MAX_GPU=30` y pocos hosts.
- Experimentos: 1 modelo YOLO, sin seeds, sin datasets, sin número de trials, sin análisis estadístico, sin comparación con baselines (template-based report, fallback determinista, humano).
- La ablation mencionada en Experimental Setup ("disabling LLM fallback") no tiene sección de resultados en `.tex`; solo `main.md` reporta 14% hallucination sin metodología.
- Reproducibilidad: `docker-compose up -d` de `wyoloservice2_production` sí existe, pero el reader no puede reproducir los números (son aleatorios).
- Arquitectura parcialmente mal descrita: el DOCX se compila desde el reporte de `TrainingReportAnalyzer` sobre `results.csv`, no desde `GLOBAL_RESEARCH_EXPLANATION.md`.

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons)

**Fortalezas:**
- ✅ `LlmAnalyzer` es un WPipe step real, registrado con `@step` y conectado al final de `professional_post_train_pipeline` (`post_train_pipeline.py:67`).
- ✅ Mecanismo de fallback determinista bien diseñado en `training_report_analyzer.py` (OpenCode → fallback CSV → mensaje degradado).
- ✅ Modelo local (`deepseek-v4-flash-free` vía OpenCode) con timeout de 300s, alineado con privacidad (Shift-Left) y sin costo de API externa.
- ✅ Prompt engineering estructurado (5 párrafos, headers Markdown, "Do not invent data").
- ✅ Licenciamiento Dual (PolyForm / AGPLv3) y link a `wyoloservice2_production` correctos.
- ✅ Detección del "anomaly" de parámetros 0.0M es un caso realista de valor del LLM (aunque el dato proviene de simulación).

**Puntos Débiles / Falencias:**
- ❌ **CRÍTICO**: Resultados basados en `random.uniform()`/hardcoded mocks presentados como mediciones reales — posible malconducta científica.
- ❌ "70 GPU nodes" sin soporte; infraestructura real es mucho menor.
- ❌ 2 referencias únicamente (mínimo requerido 8-20).
- ❌ Dual format EN/ES incompleto: falta `es/references.bib`, falta `es/main.md`, figuras vacías.
- ❌ `en/main.tex` y `en/main.md` desincronizados en Abstract y Results (cifras diferentes).
- ❌ Cero figuras, cero tablas, cero imágenes Mermaid, cero datos en formato tabular.
- ❌ Sin sección formal de Ablation Study con resultados cuantitativos.
- ❌ Sin estadística (seeds, trials, significancia), sin comparación con baselines.
- ❌ Descripción arquitectónica inexacta del flujo DOCX (resulta de `results.csv`, no de `GLOBAL_RESEARCH_EXPLANATION.md`).

---

### 4. Plan de Acción y Notas de Mejora para el Autor
*(Instrucciones concretas paso a paso para elevar el paper al estándar de publicación IEEE)*

- [ ] **Modificación 1 (CRÍTICO — INTEGRIDAD):** Sustituir los resultados simulados por mediciones reales. Ejecutar los evaluadores forenses de verdad (descomentar/implementar la lógica real en los 7 estados mock) sobre un dataset público (COCO subset) y N≥5 seeds; reportar medianas e IQR. Si por tiempo se mantienen simulaciones, declararlas explícitamente como "synthetic benchmark" y eliminar todo lenguaje de validación empírica.
- [ ] **Modificación 2 (CRÍTICO):** Corregir el claim de infraestructura: reemplazar "70 GPU nodes" por el número real de nodos/GPUs del clúster donde se ejecutó (o eliminar la cifra).
- [ ] **Modificación 3 (CRÍTICO — FORMATO):** Sincronizar `en/main.tex` ↔ `en/main.md` (unificar Abstract: una sola cifra de reducción, 87% o 95%, no ambas) y regenerar PDF con secuencia `pdflatex`→`bibtex`→`pdflatex`→`pdflatex`.
- [ ] **Modificación 4 (CRÍTICO — BILINGÜE):** Crear `es/references.bib` (mismo contenido EN) y `es/main.md`; verificar que ES compile con citas resueltas.
- [ ] **Modificación 5 (BIBLIOGRAFÍA):** Ampliar a 12-18 refs: Grad-CAM (Selvaraju et al. 2017), FGSM (Goodfellow et al. 2015), MC Dropout (Gal & Ghahramani 2016), FID (Heusel et al. 2017), Hendrycks ImageNet-C, LLM report/hallucination eval (HaluEval 2023, TruthfulQA), LLM agents (ReAct, Toolformer), MLOps tracking (MLflow), y al menos 1-2 papers 2024-2025 de LLM-based automated reporting.
- [ ] **Modificación 6 (ABLATION):** Añadir sección "Ablation Study" formal: (a) sin `LlmAnalyzer` (solo fallback), (b) sin fallback (solo OpenCode), (c) sin `_explain_research_states`; reportar tasas de éxito parse, tiempo, y tasa de hallucination sobre N trials.
- [ ] **Modificación 7 (VISUALES):** Añadir 1-2 figuras (diagrama del pipeline WPipe con los 15 estados) y 1 tabla con métricas reales (media ± std). Usar `\includegraphics[width=\linewidth,height=0.3\textheight,keepaspectratio]` y `booktabs`.
- [ ] **Modificación 8 (ARQUITECTURA):** Corregir la descripción del flujo DOCX: aclarar que el reporte principal (`LLM_Report.md/.docx`) proviene de `TrainingReportAnalyzer` sobre `evaluation_metrics/results.csv`, y que `GLOBAL_RESEARCH_EXPLANATION.md` es un artefacto separado de `_explain_research_states`.
- [ ] **Modificación 9 (ESTADÍSTICA):** Añadir seeds explícitas, número de trials, e intervalo de confianza bootstrap o test de significancia para la cifra de reducción de tiempo.
- [ ] **Modificación 10 (NOVEDAD):** Contextualizar frente al estado del arte de report generation LLM (no solo seq2seq de 2017) y explicitar el aporte diferencial (integración en pipeline distribuido MLOps con fallback determinista).

---

## IEEE Peer Review Report — paper_6_llm_reporting (Ronda 2)
**Fecha y Hora:** 2026-08-12 08:15:00
**Artículo evaluado:** `normal_papers/paper_6_llm_reporting`
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** REVISIÓN MAYOR / RE-ENVÍO (mejora sustancial respecto a la Ronda 1, pero no publicable aún)
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 8.0/10 — prosa técnica densa, voz activa, admite limitaciones reales (lo cual es señal de autoría humana), pero persisten inconsistencias entre `main.tex` (EN) y `main.md` (EN) que deben unificarse.

**Veredicto inicial (Ronda 2):** La revisión mayor de la Ronda 1 fue atendida en lo esencial: la bibliografía pasó de 2 a 17 referencias reales, `es/references.bib` y `es/main.md` ya existen, hay figuras y tablas, la infraestructura "70 GPU nodes" fue corregida a `MAX_GPU=30`, la descripción del flujo DOCX fue corregida, se añadió una sección formal de Ablation Study y los estados forenses pasaron de `random.uniform()` a modelos matemáticos deterministas (verificado en código). La medición del fallback (mediana 0.030 ms) fue **reproducida empíricamente por el revisor** (0.0307 ms en 60 ejecuciones). **Bloqueadores restantes:** (1) `main.tex` (EN, 08:07) y `main.md` (EN, 02:15) **se contradicen** sobre el estado de los estados forenses: el `.tex` los describe como "deterministic models derived from the model's actual outputs" mientras el `.md` los declara "scaffolding que emite placeholders" — y ambos son parcialmente ciertos (el código determinista aún no mide el modelo real); (2) `es/main.md` es **copia idéntica en inglés** de `en/main.md`, NO está traducido al español (viola regla de formato dual); (3) la referencia `vandall2021rethinking` en `references.bib` ("Rethinking the Hardware Cost of Deep Learning", autor "Vandall") NO coincide con lo que resuelve el `.bbl`/`.md` (Dollár et al., ICCV 2021) — posible cita fabricada que debe corregirse; (4) no hay comparación con baseline (template o humano) y el valor cualitativo del LLM se basa en un único artifact.

---

### 2. Análisis por Subagentes Especializados (Ronda 2)

#### Agente A (Originalidad y Detección de IA) — 8.0/10
- **Mejora sustancial:** Se eliminó el lenguaje inflado ("87% reduction", "95% narrative fidelity", "98% trials / 14% hallucination") de la Ronda 1. El Abstract y los Resultados ahora reportan números medibles (0.03 ms, 12.4 s, 3/3) con alcance honesto.
- **Hallazgo crítico de integridad (nuevo):** La Sección 6.1 del `en/main.tex` (reescrita 08:07) afirma: *"The pipeline is real and fully integrated. All forensic states are implemented using deterministic mathematical models derived from the model's actual outputs rather than random placeholders."* Esto **contradice la Introducción del MISMO archivo** (línea 31: *"seven of the fourteen forensic states emit placeholder values"*) y **el código real**:
  - `adversarial_attack_tester.py` sigue conteniendo literalmente *"Actual execution is mocked/skipped until integrated"*; `success_rate = 1.0 - np.exp(-epsilon*10)` (constante analítica, no medición).
  - `quantitative_xai_validator.py` usa `mock_predict` (proxy sobre imagen sintética 128×128), no el modelo real.
  - `robustness_noise_evaluator.py`: `base_acc = 0.95` hardcodeado con decaimiento exponencial (`0.95*exp(-i*0.2)`), no derivado del modelo.
  - `feature_representation_analyzer.py`: `tanh(0.6)`, `1-exp(-2.0)` — constantes arbitrarias.
  - `model_complexity_profiler.py`: latencia REAL medida (100 iteraciones CUDA), pero `map50: 0.875` hardcodeado.
  - Es decir: el cambio de `random.uniform()` a fórmulas deterministas es **real y positivo**, pero **NO son modelos "derived from the model's actual outputs"**; son constantes analíticas hardcodeadas. La afirmación del `.tex` sobrevende el estado del pipeline. Las versiones `es/main.tex` (02:35), `en/main.md` y `es/main.md` describen correctamente el andamiaje ("Siete de los catorce estados forenses escriben valores de marcador de posición").
- **Patrón de autoría:** Voz activa, oraciones de longitud variable, honestidad al retractar el "42 s" previo ("we could not reproduce that figure") — señal fuerte de autoría humana experta. Sin buzzwords AI ("delve/tapestry/paramount").
- **Originalidad metodológica:** Moderada. El valor del paper es operacional (integración en pipeline distribuido + fallback determinista), no algorítmico. La discusión de HaluEval/TruthfulQA aplicada al caso "ground truth en el mismo archivo" es una idea interesante aunque no desarrollada.

#### Agente B (Estado del Arte y Bibliografía) — 7.5/10
- **Progreso notable:** 17 entradas en `references.bib` (EN y ES idénticos, verificados), dentro del rango 8-20. Cobertura correcta de la literatura central: Grad-CAM, FGSM, MC-Dropout, FID, ImageNet-C, t-SNE, MLflow, Toolformer, ReAct, RISE, HaluEval, TruthfulQA, Van Veen (Nature Medicine 2024), GPT-3.
- **Hallazgo crítico (posible cita fabricada):** La entrada `vandall2021rethinking` en el `references.bib` ACTUAL dice *"Rethinking the Hardware Cost of Deep Learning"*, autor *"Vandall, Mark and others"*, *"IEEE Transactions on Computers 2021"*. Sin embargo, el `.bbl` compilado (02:14) y el `main.md` resuelven la MISMA clave como **Dollár, Singh y Girshick, "Rethinking the FLOPS metric for deep learning", ICCV 2021, pp. 2339-2348**. Es decir, el `.bib` fue editado (08:07) a una entrada distinta que NO coincide con la cita real usada. El paper de Dollár et al. sobre métricas FLOPS existe, pero la entrada actual del `.bib` (autor "Vandall", IEEE Trans. Computers) **no corresponde** — si se recompila, la referencia [15] cambiará a una cita no verificable. Debe alinearse `.bib` ↔ `.bbl` ↔ `.md`.
- **Gaps menores:** Sin referencia explícita a LLM-agents 2024-2025 (LangGraph, LLM-as-judge, report generation moderno post-GPT-4); la comparación SoA se queda en 2023 para LLM. Se sugiere añadir 1-2 trabajos 2024-2025 de automated reporting/hallucination-checking.
- **Formato:** BibTeX correcto (sin referencias hardcodeadas en `.tex`). DOI/URL ausentes en la mayoría de entradas (opcional en IEEE).

#### Agente C (Rigor Técnico y Metodología) — 7.0/10
- **Métrica clave verificada por el revisor:** Reproduje `_generate_fallback_report` con el código real de producción sobre los 3 CSV únicos (6 artefactos = 3 datasets duplicados entre `wyoloservice2_production` y `wyoloservice2_worker`): **mediana 0.0307 ms, media 0.0342 ms, p99 0.0797 ms** en 60 ejecuciones. El paper reporta mediana 0.030 ms, media 0.0324 ms, CI bootstrap [0.031, 0.034], max 0.0815 — **consistente y reproducible**. ✓
- **Anomalía precisión/recall verificada:** El CSV de detección (`eletronic_components`) contiene de hecho `metrics/precision(B)=0.00493`, `recall(B)=1.0` — la afirmación cualitativa del LLM está anclada en datos reales del artifact. ✓
- **Arquitectura verificada:** `LlmAnalyzer` existe como `@step`, último de `professional_post_train_pipeline` (15 pasos, `post_train_pipeline.py:67`), flujo DOCX desde `results.csv` vía `TrainingReportAnalyzer` — la descripción corregida en Ronda 2 es **exacta** (ya no afirma el flujo erróneo por `GLOBAL_RESEARCH_EXPLANATION.md`). ✓
- **Infraestructura corregida:** `MAX_GPU=30` verificado en `wyoloservice2_invoker/config/control_host.env:5`; el claim "70 GPU nodes" fue eliminado y reemplazado por la realidad (1 host RTX 3060). ✓
- **Problemas restantes:**
  - ❌ **Overclaim en `en/main.tex` Sección 6.1** (contradice intro y código, ver Agente A).
  - ❌ **"Six artifacts" es impreciso:** hay 6 archivos `results.csv` pero solo **3 únicos** (pares idénticos MD5 entre repos). El paper dice "six real artifacts (two detection, two classification, two segmentation)" — debería decir "six files / three unique datasets".
  - ❌ **n=3 para el path LLM y n=1 para el hallazgo cualitativo** — sin baselines (reporte template, humano) ni significancia. Admitido en el texto ("we deliberately omit a human-baseline study") pero limita el valor de la claim central.
  - ❌ Ablation "LLM+fallback crash injected" (0.123 ms) y "Missing results.csv" son plausibles pero no reproducibles con código entregado (no hay script de test).
  - ⚠️ PDF desactualizado: `en/main.pdf` compilado 02:14 vs `en/main.tex` 08:07 y `references.bib` 08:07 — el PDF NO refleja el texto actual.

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons) — Ronda 2

**Fortalezas:**
- ✅ Todas las acciones críticas de la Ronda 1 fueron atendidas: bib 2→17, `es/references.bib` creado, figuras + 3 tablas booktabs, Ablation Study formal, corrección de "70 GPU nodes", corrección del flujo DOCX, retractación honesta del "42 s".
- ✅ **La métrica estrella (fallback 0.03 ms) fue reproducida independientemente por el revisor** con el código de producción real.
- ✅ Estados forenses ahora deterministas (reproducibilidad garantizada), aunque con constantes hardcodeadas.
- ✅ Honestidad metodológica genuina: el texto admite 7/14 estados scaffold, ausencia de estudio humano, y dependencia del modelo hosted.
- ✅ Formato LaTeX pulido: `microtype`, `booktabs`, `cleveref`, `\raggedbottom`, `\includegraphics[width=\linewidth,height=0.2\textheight,keepaspectratio]`, BibTeX limpio.

**Puntos Débiles / Falencias:**
- ❌ **CRÍTICO:** `en/main.tex` Sección 6.1 sobrevende los estados forenses ("derived from the model's actual outputs") y **contradice la propia Introducción del mismo archivo** y las otras 3 versiones de idioma.
- ❌ **CRÍTICO:** `es/main.md` es una **copia exacta en inglés** de `en/main.md` — NO está traducido al español (viola la regla de idiomas del repositorio).
- ❌ **CRÍTICO (posible cita fabricada):** `vandall2021rethinking` en el `.bib` no corresponde a la cita real (Dollár ICCV 2021) que resuelven `.bbl` y `.md`.
- ❌ "Six artifacts" = realmente 3 datasets únicos (duplicados entre repos); el texto debe precisarlo.
- ❌ PDF desactualizado respecto al `.tex`/`.bib` vigentes.
- ❌ Sin comparación con baseline (template/humano) ni significancia estadística para el valor del LLM (admitido pero limitante).
- ❌ No hay script de tests que permita reproducir la ablación de crash-injection.

---

### 4. Plan de Acción y Notas de Mejora para el Autor (Ronda 2)

- [ ] **Modificación 1 (CRÍTICO — HONESTIDAD/COHERENCIA):** Reescribir la Sección 6.1 de `en/main.tex` para decir la verdad exacta: *"the seven scaffold forensic states now emit deterministic analytic values (e.g., exponential degradation curve, occlusion proxy) rather than random samples; the latency in model_complexity_profiler is measured; the remaining map50 is a fixed value"*. Unificar con la introducción (7/14 scaffold) y con las versiones `es/main.tex` y ambos `.md`.
- [ ] **Modificación 2 (CRÍTICO — IDIOMA):** Traducir `es/main.md` al español real (no copia del EN). Verificar que `es/main.tex` y `es/main.md` estén sincronizados (actualmente `es/main.tex` describe el estado honesto de 02:35 pero `es/main.md` es copia del EN de 02:15).
- [ ] **Modificación 3 (CRÍTICO — BIBLIOGRAFÍA):** Corregir `vandall2021rethinking` en `references.bib` para que coincida exactamente con la cita resuelta en `.bbl`/`.md`: Dollár, P., Singh, M., Girshick, R., "Rethinking the FLOPS metric for deep learning," ICCV 2021, pp. 2339-2348. Verificar que al recompilar el número [15] no cambie.
- [ ] **Modificación 4 (RIGOR):** Aclarar en el texto que los "six artifacts" son 3 datasets únicos duplicados entre repositorios, o usar solo 3. Añadir MD5 o tabla de artefactos.
- [ ] **Modificación 5 (REPRODUCIBILIDAD):** Publicar un script de benchmark (p. ej. `benchmark_fallback.py`) en `wyoloservice2_production` que reproduzca la Tabla 2 (120 runs) y la ablación crash-injection, para que cualquier lector verifique 0.030 ms.
- [ ] **Modificación 6 (VISUALES/PDF):** Recompilar `main.pdf` (EN y ES) con la secuencia `pdflatex → bibtex → pdflatex → pdflatex` tras los cambios. El PDF actual (02:14/02:35) no refleja el `.tex` (08:07).
- [ ] **Modificación 7 (EXPERIMENTO):** Añadir baseline template-report (sin LLM) con las mismas 3 muestras y evaluación ciega 5-7 evaluadores, o al menos reportar el delta LLM-vs-template. Sin esto, "the LLM must earn its keep" no está demostrado.
- [ ] **Modificación 8 (NOVEDAD):** Añadir 2-3 referencias 2024-2025 de LLM report generation / hallucination-checking automatizado y posicionar el aporte (integración con fallback determinista + privacy shift-left) frente a ellas.

---

---

## IEEE Peer Review Report — paper_6_llm_reporting (Ronda 3)
**Fecha y Hora:** 2026-08-12 08:22:00
**Artículo evaluado:** `normal_papers/paper_6_llm_reporting`
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final (Inicial)
- **Veredicto:** REVISIÓN MAYOR / RE-ENVÍO (mejora parcial; persiste sobredeclaración crítica en la versión EN)
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 8.0/10 — prosa técnica densa, voz activa, retractación honesta del "42 s" (señal de autoría humana). **Bloqueador de integridad:** la Sección 6.1 de las 4 versiones sigue afirmando que los estados forenses están "derived from the model's actual outputs", pero el código muestra constantes analíticas hardcodeadas (base_acc=0.95, tanh(0.6), FID de medias fijas, mock_predict sobre imagen gris sintética); además, el abstract ES ya declara "7 de 14 estados son andamiaje" mientras el abstract EN lo omite — divergencia EN/ES que viola el formato dual. Bibliografía OK (17 refs reales). **Notas de mejora:** (1) unificar el disclosure de scaffolding en EN/ES (abstract + Sección 6.1); (2) publicar script de benchmark para Tabla 2 y ablación crash-injection; (3) añadir baseline template/humano y refs 2024-2025.

---

### 2. Análisis por Subagentes Especializados (Ronda 3)

#### Agente A (Originalidad y Detección de IA) — 8.0/10
- Prosa técnica densa, voz activa, oraciones de longitud variable; retractación explícita del "42 s" ("we could not reproduce that figure") es señal fuerte de autoría humana. Sin buzzwords IA.
- **Progreso:** el abstract ES añadió el disclosure honesto ("Siete de los catorce estados forenses son aún andamiaje... lo declaramos explícitamente") — buena práctica de transparencia.
- **Fallos de autenticidad/integridad:**
  - El abstract EN (línea 19) **omite** ese disclosure y en su lugar afirma "deterministic mathematical models derived from real evaluation characteristics" — EN y ES ahora **se contradicen** sobre el mismo hecho. Divergencia que viola la regla de sincronización dual del repositorio.
  - La Sección 6.1 de las **4 versiones** (EN tex, EN md, ES tex, ES md) sigue afirmando "All forensic states are implemented using deterministic mathematical models **derived from the model's actual outputs** rather than random placeholders". Esto es **falso según el código** (verificado en `wyoloservice2_worker`):
    - `quantitative_xai_validator.py`: usa `mock_predict` sobre imagen gris sintética `np.ones((128,128,3))*128`, NO el modelo real.
    - `robustness_noise_evaluator.py`: `base_acc = 0.95` hardcodeado con decaimiento `0.95*exp(-i*0.2)` — no derivado del modelo.
    - `adversarial_attack_tester.py`: comentario literal "Actual execution is mocked/skipped until integrated"; `success_rate = 1.0 - exp(-epsilon*10)` — constante analítica, no medición.
    - `feature_representation_analyzer.py`: `tanh(0.6)`, `1-exp(-2.0)` — constantes arbitrarias.
    - `uncertainty_quantifier.py`: `var(linspace(0.1,0.9,20))` — determinista pero no del modelo.
    - `cross_domain_generalizer.py`: FID de `source_mu=[0.5,0.5]`, `target_mu=[0.2,0.8]` fijos.
    - `model_complexity_profiler.py`: **SÍ mide** GFLOPs/params/latencia reales (ptflops + eventos CUDA), pero `map50: 0.875` hardcodeado.
  - **Conclusión:** el cambio `random.uniform()` → fórmulas deterministas es real y positivo, pero el lenguaje "derived from the model's actual outputs" sigue siendo una sobredeclaración. La única afirmación 100% cierta es: *"deterministic analytic models rather than stochastic sampling"* (7/14 aún placeholders analíticos, solo el profiler de complejidad mide hardware real).

#### Agente B (Estado del Arte y Bibliografía) — 8.0/10
- 17 entradas en `references.bib` (EN y ES idénticos, verificados), dentro del rango 8-20. Cobertura correcta: Grad-CAM, FGSM, MC-Dropout, FID, ImageNet-C, t-SNE, MLflow, Toolformer, ReAct, RISE, HaluEval, TruthfulQA, Van Veen 2024, GPT-3.
- **Progreso crítico:** la entrada `vandall2021rethinking` fue **corregida** — ahora es Dollár, Singh, Girshick, "Fast and Accurate Model Scaling", CVPR 2021, pp. 924-932, que **coincide exactamente** con lo resuelto en `.bbl` y `.md`. ✓ (Ronda 2 Modificación 3 resuelta).
- **Detalle cosmético:** el *key* `vandall2021rethinking` ya no coincide con el título real ("Fast and Accurate Model Scaling") — renombrar a `dollar2021fast` o similar, y recompilar.
- **Gap pendiente:** sigue sin refs 2024-2025 de LLM report generation/hallucination-checking (solo Van Veen 2024). Sugerencia de Ronda 2 (Mod 8) no atendida.
- Formato BibTeX correcto (sin hardcoded refs en `.tex`); faltan DOI/URL en la mayoría (opcional).

#### Agente C (Rigor Técnico y Metodología) — 7.0/10
- **Fallback reproducido por el revisor:** ejecuté `_generate_fallback_report` (réplica exacta del código de producción) sobre los 3 CSVs únicos × 20 = 60 runs: **mediana 0.0338 ms, media 0.0344 ms, p99 0.0871 ms**. El paper reporta mediana 0.030 ms, media 0.0324 ms, p99 0.070 ms — **mismo orden de magnitud, consistente**. ✓ La Tabla 2 es reproducible.
- **Anomalía precisión/recall verificada:** el CSV de detección contiene precision(B) 0.00485/0.00493 y recall 1.0 en ambas épocas — la afirmación cualitativa del LLM está anclada en datos reales. ✓
  - ⚠️ **Imprecisión menor:** el paper cita "precision 0.00493", pero la última fila (que lee el fallback) tiene 0.00485; 0.00493 es la primera época. El fallback imprimiría 0.00485.
- **Pipeline verificado:** `LlmAnalyzer` último de 15 pasos en `post_train_pipeline.py:67` ✓; `safe_step` wrapper ✓; OpenCode bin + modelo ✓; DOCX desde `results.csv` ✓ (descripción exacta).
- **"Six artifacts" sigue impreciso:** 6 archivos `results.csv` pero **3 únicos** (MD5 duplicados entre `wyoloservice2_production` y `wyoloservice2_worker`). El paper dice "six real results.csv artifacts (two detection, two classification, two segmentation runs)" — debería decir "six files / three unique datasets" (Ronda 2 Mod 4 no atendida).
- **Bloqueadores pendientes:** sin script de benchmark publicado para Tabla 2 / crash-injection; sin baseline template/humano; n=3 para LLM, n=1 para hallazgo cualitativo; sin significancia estadística.
- **Mejora:** PDFs regenerados (en/main.pdf 08:18, es/main.pdf 08:18) reflejan el `.tex` vigente ✓. `es/main.md` ahora está **traducido al español real** (Ronda 2 Mod 2 resuelta) ✓.

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons) — Ronda 3

**Fortalezas:**
- ✅ Fallback determinista medido y **reproducido independientemente por el revisor** (0.0338 ms mediana vs 0.030 reportado).
- ✅ `es/main.md` traducido al español real (ya no es copia en inglés).
- ✅ `vandall2021rethinking` corregida (Dollár et al., CVPR 2021 — coincide con `.bbl`).
- ✅ PDFs actualizados y sincronizados con `.tex` (08:18).
- ✅ Abstract ES añade disclosure honesto de scaffolding (7/14) — transparencia genuina.
- ✅ 17 refs reales, BibTeX correcto, formato LaTeX pulido (microtype/booktabs/cleveref/raggedbottom).
- ✅ `model_complexity_profiler` mide hardware real (GFLOPs/params/latencia CUDA) — dato no simulado.

**Puntos Débiles / Falencias:**
- ❌ **CRÍTICO:** Sección 6.1 de las 4 versiones sobredeclara: "deterministic mathematical models **derived from the model's actual outputs**" — falso para 6/7 estados forenses (constantes analíticas hardcodeadas, mock_predict sobre imagen sintética).
- ❌ **CRÍTICO:** Abstract EN omite el disclosure de scaffolding que el abstract ES sí declara — **EN/ES se contradicen** (violación de sincronización dual).
- ❌ "Six artifacts" = 6 archivos / 3 datasets únicos (no 6 runs distintos).
- ❌ Cita precision 0.00493 corresponde a época 1; la última fila (fallback) es 0.00485.
- ❌ Sin script de benchmark reproducido en repo para Tabla 2/ablación.
- ❌ Sin baseline (template/humano) ni significancia estadística para el valor del LLM.
- ❌ Key de bib `vandall2021rethinking` desalineado con el título real de la entrada.

---

### 4. Plan de Acción y Notas de Mejora para el Autor (Ronda 3)

- [ ] **Modificación 1 (CRÍTICO — INTEGRIDAD):** Reescribir la Sección 6.1 en las **4 versiones** con la verdad exacta: "The seven scaffold forensic states emit deterministic analytic values (e.g., exponential degradation `0.95·exp(-0.2i)`, occlusion proxy over a synthetic image, fixed FID means) rather than random samples; `model_complexity_profiler` measures real GFLOPs/params/latency". Eliminar "derived from the model's actual outputs".
- [ ] **Modificación 2 (CRÍTICO — SINCRONIZACIÓN EN/ES):** Añadir al abstract EN la misma frase de disclosure que el ES ("Seven of the fourteen forensic states are still scaffolding emitting placeholder values; we state this explicitly") — o alinearlos en el wording exacto. Regenerar EN/ES `.tex`, `.md`, `.pdf`.
- [ ] **Modificación 3 (RIGOR):** Aclarar "six artifacts" → "six files (three unique datasets)"; corregir la cita de precisión a la última fila (0.00485) o indicar que se refiere a la primera época.
- [ ] **Modificación 4 (REPRODUCIBILIDAD):** Publicar `benchmark_fallback.py` y un script de crash-injection en `wyoloservice2_production` para reproducir Tabla 2 y la ablación.
- [ ] **Modificación 5 (BIBLIOGRAFÍA):** Renombrar key `vandall2021rethinking` → `dollar2021fast` (recompilar); añadir 2-3 refs 2024-2025 de LLM report generation / hallucination-checking automatizado.
- [ ] **Modificación 6 (EXPERIMENTO):** Baseline template-report con las mismas 3 muestras + evaluación ciega 5-7 evaluadores, o reportar delta LLM-vs-template. Sin esto, "the LLM must earn its keep" sigue sin demostrarse.

---

**Firma del Revisor:** IEEE Senior Member / Area Editor
**Fecha:** 2026-08-12
**Próxima ronda:** Tras Modificación 1 y 2 (integridad + sincronización EN/ES), re-evaluación en 2 semanas.

---

---

## IEEE Peer Review Report — paper_6_llm_reporting (Ronda 4)
**Fecha y Hora:** 2026-08-12 08:27:30
**Artículo evaluado:** `normal_papers/paper_6_llm_reporting`
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** **ACEPTADO CON CAMBIOS MENORES** (Industrial Experience Report)
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 8.5/10 — prosa técnica densa, voz activa, retractación honesta del "42 s", y los dos bloqueadores CRÍTICOS de integridad de la Ronda 3 están **resueltos**.

**Veredicto inicial (Ronda 4):** Los dos bloqueadores críticos de la Ronda 3 fueron atendidos en las 4 versiones: (1) la Sección 6.1 ya **no sobredeclara** — afirma exactamente lo que el código muestra ("seven of the fourteen forensic states emit deterministic analytic values ...; `model_complexity_profiler` measures real GFLOPs/params/latency", sin "derived from the model's actual outputs"); (2) el abstract EN ahora incluye el mismo disclosure de scaffolding (7/14) que el ES — EN/ES alineados. La métrica estrella fue **reproducida de nuevo por el revisor**: mediana 0.033 ms (60 runs) vs 0.030 ms reportado; la recuperación de crash-injected (0.123 ms) es consistente con el peor caso medido (0.127 ms). Precisión corregida a 0.00485 (última fila, verificada en CSV). **Residuales (no bloqueadores):** (1) EN sigue diciendo "six real results.csv artifacts" sin "(three unique datasets)" mientras ES sí lo dice — divergencia de redacción EN/ES; (2) no hay script de benchmark/crash-injection publicado; (3) sin baseline template/humano (admitido); (4) sin refs 2024-2025 de LLM report generation; (5) `petsiuk2018rise` sin citar en el `.tex`.

---

### 2. Análisis por Subagentes Especializados (Ronda 4)

#### Agente A (Originalidad y Detección de IA) — 8.5/10
- Prosa técnica densa, oraciones de longitud variable, voz activa, cero buzzwords AI. La retractación explícita del "42 s" ("we could not reproduce that figure") y la declaración explícita de scaffolding son señales fuertes de autoría humana experta y de honestidad metodológica.
- **Bloqueador de integridad RESUELTO:** las 4 versiones (EN/ES tex+md) de la Sección 6.1 ahora dicen exactamente lo que el código implementa. Verificado en código:
  - `quantitative_xai_validator.py`: `mock_predict` sobre imagen gris sintética `np.ones((128,128,3))*128` — el paper lo declara como "occlusion proxy over a synthetic image". ✓
  - `robustness_noise_evaluator.py`: `base_acc=0.95`, decaimiento `0.95*exp(-0.2i)` — "exponential degradation". ✓
  - `adversarial_attack_tester.py`: `exp(-ε·10)` analítico; `cross_domain_generalizer.py`: medias FID fijas — "fixed FID means". ✓
  - `model_complexity_profiler.py`: **sí mide** GFLOPs/params vía `ptflops` (aunque `map50: 0.875` hardcodeado) — el texto lo acota correctamente a "measures real GFLOPs/params/latency". ✓
  - `random.uniform()` ya no aparece en ningún estado forense (grep limpio). ✓
- **Abstract EN ahora con disclosure:** la frase "Seven of the fourteen forensic states are scaffolding ... do not report their outputs as experimental measurements" ya figura en el abstract EN (`main.tex:19`), alineada con el ES. La contradicción EN/ES de la Ronda 3 desapareció. ✓
- **Residual:** EN usa "six real results.csv artifacts" (abstract, Sección 6.2, Data & Code) mientras ES usa "seis archivos (tres conjuntos de datos únicos)" — mismo hecho, redacción divergente que viola la regla de sincronización estricta EN/ES.

#### Agente B (Estado del Arte y Bibliografía) — 7.5/10
- **16 referencias compiladas** (`.bbl` = 16 items, `.aux` = 16 citations únicas, sin "undefined"). `references.bib` EN = ES idéntico (diff limpio). Dentro del rango 8-20. ✓
- **Key `dollar2021fast` corregido:** ahora "Fast and Accurate Model Scaling" (Dollár, Singh, Girshick, CVPR 2021, pp. 924-932) coincide en `.bib` ↔ `.bbl` ↔ `.tex`. ✓ (Ronda 3 Mod 5 resuelta).
- **Detalle:** `petsiuk2018rise` (RISE) está en `references.bib` pero **no se cita** en el `.tex` (biotex la descartó) — entrada huérfana que debería citarse o eliminarse.
- **Gap pendiente (Ronda 3 Mod 8 no atendida):** la única referencia 2024-2025 es Van Veen (Nature Medicine 2024). Siguen faltando 2-3 trabajos 2024-2025 de LLM report generation / automated hallucination checking / LLM-as-judge para posicionar el aporte frente al SoA reciente.
- Formato BibTeX correcto (sin refs hardcodeadas); faltan DOI/URL en la mayoría (opcional).

#### Agente C (Rigor Técnico y Metodología) — 7.5/10
- **Fallback reproducido por el revisor (Ronda 4):** ejecuté `TrainingReportAnalyzer._generate_fallback_report` (código de producción real, vía import directo del módulo) sobre los 3 CSVs únicos × 20 = 60 runs: **mediana 0.0331 ms, media 0.0379 ms, p99 0.083 ms, max 0.127 ms**. El paper reporta mediana 0.030, media 0.0324, p99 0.070, max 0.0815 — **mismo orden de magnitud, consistente, reproducible**. ✓ Tabla 2 verificada.
- **Crash-injection (0.123 ms) consistente:** mi peor caso de fallback (0.127 ms) coincide con la recuperación reportada tras inyectar el fallo del LLM. Plausible y reproducible en orden de magnitud. ✓
- **Precisión/recall verificada:** la última fila del CSV de detección (la que lee el fallback) contiene `metrics/precision(B)=0.00485`, `recall(B)=1.0` — coincide exactamente con el texto del paper (0.00493 es la primera época; la corrección de la Ronda 3 quedó bien aplicada). ✓
- **Arquitectura verificada:** `LlmAnalyzer` último de 15 pasos en `post_train_pipeline.py:67` ✓; `safe_step` wrapper (líneas 35-45) ✓; modelo `opencode/deepseek-v4-flash-free` y binario `/root/.opencode/bin/opencode` ✓; timeouts 180 s / 300 s ✓; DOCX corporativo desde `results.csv` vía python-docx (`llm_analyzer.py:44-95`) ✓; 6 `results.csv` = 3 datasets únicos (MD5: `cac6954c`, `8746797f`, `6c511115` duplicados entre repos) ✓.
- **Pendientes (Ronda 3 Mods 4, 6, 7):** ❌ sin `benchmark_fallback.py` ni script de crash-injection en `wyoloservice2_production` (grep: no existe) — Tabla 2 y la ablación siguen sin script público; ❌ sin baseline template/humano (n=3 LLM, n=1 hallazgo cualitativo; admitido como amenaza de validez externa); ❌ sin significancia estadística para el delta LLM-vs-fallback.

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons) — Ronda 4

**Fortalezas:**
- ✅ **Integridad restaurada:** Sección 6.1 y abstract EN/ES alineados con el código real (7/14 scaffolding declarado; sin sobredeclaración). Los dos bloqueadores críticos de la Ronda 3 están resueltos.
- ✅ Fallback determinista **reproducido dos veces por el revisor** (Ronda 2: 0.0307 ms; Ronda 4: 0.0331 ms) vs 0.030 ms reportado — consistente en ambas rondas.
- ✅ Precisión corregida a 0.00485 (última fila) — verificación empírica exacta.
- ✅ 16 refs reales y resueltas, BibTeX limpio, EN=ES idénticos, `dollar2021fast` alineado `.bib`↔`.bbl`↔`.tex`.
- ✅ Formato LaTeX pulido (microtype/booktabs/cleveref/raggedbottom), figura del pipeline de 15 pasos, 3 tablas booktabs.
- ✅ Honestidad metodológica: retractación del "42 s", amenaza de validez externa declarada, limitación del hallazgo cualitativo a n=1.

**Puntos Débiles / Falencias:**
- ❌ **Residual (formato dual):** EN dice "six real results.csv artifacts" (abstract, Sección 6.2, Data & Code) sin "(three unique datasets)", mientras ES sí lo precisa — EN/ES siguen divergiendo en redacción.
- ❌ Sin `benchmark_fallback.py` / script de crash-injection publicado para reproducir Tabla 2 y la ablación.
- ❌ Sin baseline template/humano ni significancia estadística para el valor del LLM (n=3; hallazgo cualitativo n=1).
- ❌ Sin refs 2024-2025 de LLM report generation / hallucination-checking (solo Van Veen 2024).
- ❌ `petsiuk2018rise` huérfana en el `.bib` (no citada en `.tex`).
- ⚠️ En `main.md` (EN/ES) las referencias cruzadas quedan rotas ("Table~", "Figure~", "Section~7.3") por la conversión Markdown — aceptable, pero conviene sustituir por números literales para el preview de GitHub.

---

### 4. Plan de Acción y Notas de Mejora para el Autor (Ronda 4)

- [ ] **Modificación 1 (FORMATO DUAL — SINCRONIZACIÓN EN/ES):** Unificar la redacción del conteo de artefactos: usar en TODAS las posiciones de EN y ES "six files (three unique datasets)" / "seis archivos (tres conjuntos de datos únicos)". Regenerar EN/ES `.tex`, `.md`, `.pdf`.
- [ ] **Modificación 2 (REPRODUCIBILIDAD):** Publicar `benchmark_fallback.py` (60-120 runs sobre los 3 CSVs) y `benchmark_crash_injection.py` en `wyoloservice2_production`, enlazándolos desde la Sección 8 (Data & Code Availability), para que Tabla 2 y la ablación sean verificables por cualquier lector.
- [ ] **Modificación 3 (EXPERIMENTO):** Añadir un baseline de plantilla (template-report sin LLM) con las mismas muestras y un delta LLM-vs-template (idealmente evaluación ciega 5-7 evaluadores). Si no es viable antes del envío, marcarlo explícitamente como trabajo futuro ya planificado (el texto ya lo admite — basta reforzarlo).
- [ ] **Modificación 4 (BIBLIOGRAFÍA):** Añadir 2-3 referencias 2024-2025 de automated report generation con LLM y de hallucination-checking sobre fuentes estructuradas (p. ej., frameworks de verificación factual contra documentos); citar o eliminar `petsiuk2018rise`. Recompilar.
- [ ] **Modificación 5 (COSMÉTICO MD):** En `main.md` EN/ES, reemplazar "Table~"/"Figure~"/"Section~7.3" por números literales (Tabla 1-3, Figura 1, Sección 7.3) para un preview de GitHub legible.

---

**Firma del Revisor:** IEEE Senior Member / Area Editor
**Fecha:** 2026-08-12
**Próxima ronda:** Tras Modificación 1 (sincronización EN/ES) y Modificación 2 (script de benchmark), el paper queda listo para publicación como Industrial Experience Report.

---

## IEEE Peer Review Report — paper_1_mlops (Ronda 1)
**Fecha y Hora:** 2026-08-12 08:31:15
**Artículo evaluado:** `normal_papers/paper_1_mlops` (EN + ES)
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** **REVISIÓN MAYOR / RE-ENVÍO**
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 5/10

**Veredicto inicial (Ronda 1):** REVISIÓN MAYOR. El paper es un esqueleto de 2 páginas: el título reclama "Multi-Objective HPO" pero el código verificado implementa `optuna.create_study(direction=...)` de objetivo único; el cuerpo no menciona el multiobjetivo en ningún punto. Detección de IA alta (5/10): "paradigm shift", "seamlessly", "absolute necessity", y la frase redundante "a heterogeneous cluster of a heterogeneous pool" delatan texto generado sin editar; no hay tablas, figuras (carpetas `figures/` vacías), ni métricas cuantitativas — solo afirmaciones (0.8ms, 40%, OOM en 4h) sin metodología. Bibliografía: 10 refs con citas incorrectas (akiba2019optuna usada para sustentar overhead de Kubernetes; sin cita de YOLO, HPO, ni trabajos 2023-2025). Inconsistencia interna 30 vs 70 nodos; versión ES con errores de traducción y divergencia EN/ES. Requiere: convertir el núcleo de arquitectura + ablation en experimentos medidos con tablas/figuras, corregir el título, arreglar bibliografía, y sincronizar EN/ES.

---

### 2. Análisis por Subagentes Especializados (Ronda 1)

#### Agente A (Originalidad y Detección de IA) — 5/10
- **Marcadores claros de texto generado sin editar:** "presents a paradigm shift in local MLOps" (Conclusión), "seamlessly with zero downtime", "absolute necessity", "establishes a highly scalable baseline" y "significantly lowering idle energy consumption" — adjetivos de relleno sin ningún dato detrás, justo lo prohibido en AGENTS.md (anti-sales-pitch, data-driven).
- **Redundancia LLM literal:** "deployed on a heterogeneous cluster of a heterogeneous pool capped at 30 GPU nodes" — construcción duplicada sin sustancia, presente en EN y ES.
- **Sobrecategorización / auto-contradicción:** el abstract afirma que NeuralForge "eliminates memory leaks (OOM errors)" pero la Sección 5 describe el propio ablation donde el OOM mató el host en 4h. "Eliminates" es insostenible y el propio texto se desmiente.
- **Título sobredeclarado:** "Multi-Objective HPO" no aparece ni una vez en el cuerpo; la implementación verificada es de objetivo único.
- **Positivo:** voz activa y "We" académico, abstract y keywords presentes, secciones completas en orden. Sin embargo, a diferencia de papers 2/4/5 del repositorio, aquí no hay admisión de limitaciones, ni datos crudos, ni imperfecciones reales — señales de borrador LLM sin pasada humana. Cero autocorrecciones ("we could not reproduce..."), lo que en el contexto de este repositorio indica poca madurez editorial.
- **Formato Markdown roto:** `main.md` conserva comandos LaTeX crudos (`\IEEEoverridecommandlockouts`, `\raggedbottom`, `\begin{abstract}`, `\begin{IEEEkeywords}`) y referencias cruzadas sin resolver — conversión automática sin revisar.

#### Agente B (Estado del Arte y Bibliografía) — 4/10
- **10 referencias** compiladas y resueltas (`.aux` = 10 `\bibcite` únicos, `.bbl` limpio, sin "undefined"). Dentro del rango 8-20 del estándar, pero la *calidad* de la citación es el punto más débil del paper.
- **Citas incorrectas (crítico):**
  - `akiba2019optuna` (el paper de Optuna, KDD'19) se cita para sustentar "Kubernetes introduces substantial networking overhead" — **la fuente no dice eso**. Falta una cita real de Kubernetes (p. ej., Burns et al., SOSP 2016).
  - `zaharia2018accelerating` es el paper de **MLflow** — válido para MLflow, pero el texto lo usa para "Kubeflow **and** MLflow" (no cubre Kubeflow).
- **Entradas informales:** `sobolev2015celery` con journal "Python project" y `fastapi2020` con journal "URL: https://fastapi.tiangolo.com" — no son fuentes académicas citables; deberían ir como software (DOI) o eliminarse.
- **Vacíos bibliográficos mayúsculos:** sin cita de YOLO (Redmon 2016 o Jocher/Ultralytics), sin fundamentos de HPO (Bergstra & Bengio 2012, Snoek 2012, Feurer 2015), sin TPE (Bergstra 2011) ni CMA-ES (Hansen) pese a ser los samplers que el código usa, sin trabajos de MLOps distribuido 2022-2025 (Ray Tune, SkyPilot, surveys). Solo 2 refs posteriores a 2019 (li2020, patterson2021).
- **Sin DOIs/URLs** en la mayoría de entradas; `shokri2015privacy` y `patterson2021carbon` citados en Broader Impact sin conexión argumental sólida.
- **Positivo:** BibTeX correcto (sin refs hardcodeadas), `references.bib` EN idéntico a ES (diff limpio, 2244 bytes ambos), compilación de citas sin errores.

#### Agente C (Rigor Técnico y Metodología) — 4/10
**Verificación en código de producción (repo `wyoloservice2_production` + `wyoloservice2_invoker/manager`):**
- ✅ **Arquitectura real y verificada:** Invoker Celery (`app/minimal_worker.py`, `celery_config.py`, `worker_gpu.py`), broker Redis, almacenamiento Optuna en PostgreSQL vía `RDBStorage` (`wyoloservice2_manager/app/user_orchestrator.py:354-370`), colas priorizadas `gpus_high/gpus_medium/gpus_low` en los docker-compose de producción, Watchtower en `docker-compose.manager.yml`, ejecutor Docker efímero con límites (`shm_size`, GPU ID; cliente `docker` en `states/eda.py`, `RunTraining.docker_run`). El patrón Invoker-Executor existe y es la contribución genuina del paper.
- ❌ **Título no respaldado por el código:** `optuna.create_study(study_name=..., direction=direction, storage=..., sampler=..., pruner=...)` es de **objetivo único** (un solo `direction`, `user_orchestrator.py:363-370`). No hay `n_objectives=2` ni `directions=[...]`. "Multi-Objective HPO" es una sobredeclaración.
- ❌ **Sin protocolo experimental:** la afirmación "0.8ms average" carece de N, desviación/IQR, percentiles, specs de hardware (modelo de GPU, VRAM, red, configuración Redis). No existe script de benchmark de latencia en el ecosistema que respalde la cifra.
- ❌ **"72-hour continuous training period" sin métricas:** sin throughput de trials, tasa de fallos, utilización de GPU, ni curvas de memoria.
- ❌ **Ablación anecdótica:** "OOM kills within 4 hours" sin curvas RSS/memoria, sin logs, sin repeticiones (N=1 host), sin tabla. El estándar exige una sección de Ablación con datos.
- ❌ **"40% reduction in idle GPU time"** sin metodología de medición (¿instrumentación? ¿baseline de idle? ¿ventana temporal?).
- ❌ **"Zero downtime" Watchtower** sin duración medida de la actualización de imagen.
- ❌ **Baseline monolítico (Celery worker en proceso único) descrito pero sin resultados** — no hay comparación cuantitativa contra él.
- ❌ **Inconsistencia interna 30 vs 70 nodos:** abstract y Experimental Setup dicen "30 GPU nodes"; Results dice "across the **70** nodes". La ES lo traduce mal y de forma divergente: "en los un grupo heterogéneo limitado a 30 nodos" (frase gramaticalmente rota) — doble violación de sincronización EN/ES.
- ❌ **Reproducibilidad insuficiente:** `docker-compose up -d` no basta; faltan scripts de benchmark, dataset de referencia, configs de experimento y salidas esperadas.
- ❌ **Formato IEEE incompleto:** 2 páginas (target 3-6), **0 tablas** y **0 figuras** (`figures/` vacías en EN y ES) pese a `booktabs`/`graphicx` cargados; sin sección de Ablación; sin diagrama de arquitectura (exigido por AGENTS.md).
- ❌ Sin significancia estadística en ninguna métrica.

---

### 3. Fortalezas y Puntos Débiles (Pros & Cons) — Ronda 1

**Fortalezas:**
- ✅ **La arquitectura es real:** Invoker-Executor con contenedores Docker efímeros + colas priorizadas + Watchtower + Optuna/PostgreSQL se verificó en el código de producción. El patrón de aislamiento efímero para HPO es una contribución de ingeniería genuina y digna de un Industrial Experience Report.
- ✅ Estructura de secciones completa y en orden (Abstract, Intro, Related Work, Architecture, Setup, Results, Data & Code, Broader Impact, Conclusion, Acknowledgments, References).
- ✅ Uso correcto de BibTeX (sin refs hardcodeadas); compilación limpia (2 páginas, sin warnings ni citas indefinidas); EN=ES `references.bib` idénticos.
- ✅ Preamble pulido (microtype, booktabs, cleveref, raggedbottom); autor, afiliación, licencia dual y repo de producción mencionados; versión ES presente (multilenguaje).

**Puntos Débiles / Falencias:**
- ❌ **Título engañoso ("Multi-Objective HPO")** no implementado ni descrito en el cuerpo — riesgo de rechazo por mala representación del aporte.
- ❌ **Cero evidencia cuantitativa:** 0 tablas, 0 figuras, métricas desnudas (0.8ms, 40%, 4h) sin metodología, N, ni contexto hardware.
- ❌ **Baseline sin resultados:** la comparación contra el worker monolítico no reporta ningún número.
- ❌ **Citas incorrectas y vacíos de SoA:** `akiba2019optuna` mal usada para Kubernetes; sin YOLO, HPO, ni literatura 2022-2025; 2 entradas informales (Celery, FastAPI).
- ❌ **Inconsistencia interna 30 vs 70 nodos** y **divergencia EN/ES** con errores gramaticales en la versión española.
- ❌ **Lenguaje de marketing IA típico** ("paradigm shift", "seamlessly", "absolute necessity") y sobrecategorización ("eliminates OOM" auto-contradicha por el propio ablation).
- ❌ Sin sección de Ablación, sin discusión de limitaciones, sin significancia estadística, 2 páginas (por debajo del mínimo de 3).
- ❌ `main.md` (EN/ES) con LaTeX crudo y referencias cruzadas rotas; `figures/` vacías.

---

### 4. Plan de Acción y Notas de Mejora para el Autor (Ronda 1)

- [ ] **Modificación 1 (CRÍTICO — INTEGRIDAD DEL TÍTULO):** O bien (a) retitular a "NeuralForge: A Distributed MLOps Framework for Automated YOLO Hyperparameter Optimization" (honesto, sin multiobjetivo), o bien (b) implementar de verdad un estudio multiobjetivo en `user_orchestrator.py` (`optuna.create_study(directions=[maximize(mAP), minimize(VRAM/time)])`), documentarlo en Arquitectura y analizar el frente de Pareto en Resultados. Aplicar el mismo cambio en EN y ES.
- [ ] **Modificación 2 (CRÍTICO — EVIDENCIA EXPERIMENTAL):** Convertir cada afirmación en una medición: (a) latencia de dispatch con N≥1000 envíos, reportando mediana, IQR, P95/P99 y specs del cluster (modelo GPU, VRAM, RAM, red, Redis); (b) corrida de 72h con trials completados, tasa de fallos, utilización GPU y picos de memoria; (c) metodología de medición del 40% de idle GPU (instrumentación + baseline); (d) duración de la actualización Watchtower. Presentar como tablas `booktabs` y figuras vectoriales matplotlib (ejes etiquetados).
- [ ] **Modificación 3 (CRÍTICO — SECCIÓN DE ABLACIÓN):** Ablación con límites de memoria desactivados en N≥3 hosts: curvas RSS/memoria vs tiempo, distribución de tiempo-hasta-OOM, logs del host; comparar estabilidad con/sin límites; tabla + figura. Reportar la diferencia con el sistema con límites activos.
- [ ] **Modificación 4 (CONSISTENCIA):** Verificar el tamaño real del cluster y unificar 30/70 nodos en todo el texto (EN y ES); añadir inventario hardware completo en Experimental Setup.
- [ ] **Modificación 5 (BIBLIOGRAFÍA):** Sustituir la cita de Kubernetes (Burns et al., SOSP 2016); añadir YOLO (Redmon 2016 / Jocher 2020), fundamentos de HPO (Bergstra & Bengio 2012, Snoek 2012, Feurer 2015), TPE (Bergstra 2011), CMA-ES (Hansen) y 2-3 trabajos 2022-2025 de MLOps/HPO distribuido (Ray Tune, SkyPilot o surveys); añadir DOIs; sustituir o formalizar `sobolev2015celery` y `fastapi2020`. Total objetivo: 15-20 refs.
- [ ] **Modificación 6 (SINCRONIZACIÓN EN/ES):** Corregir la frase rota "en los un grupo heterogéneo" y alinear el conteo de nodos y el wording exacto EN/ES; regenerar `.tex`, `.md`, `.pdf` (secuencia 4 pasos) y arreglar `main.md` (eliminar comandos LaTeX crudos, cruces literales "Table 1", "Section 4").
- [ ] **Modificación 7 (LENGUAJE Y SOBREDECLARACIÓN):** Eliminar "paradigm shift", "seamlessly", "absolute necessity" y "eliminates OOM"; sustituir adjetivos por números crudos. Reemplazar "eliminates memory leaks" por "prevents OOM-driven host failures in sustained runs (evidence: ablation X)". Añadir sección de Limitaciones.
- [ ] **Modificación 8 (VISUALES Y EXTENSIÓN):** Añadir diagrama de arquitectura Invoker-Executor (Mermaid renderizado a vector en `figures/`, `\includegraphics[width=\linewidth,...]`) y ampliar Related Work con un análisis de gap real (evidencia, no aserción) para llegar a 3-6 páginas.
- [ ] **Modificación 9 (REPRODUCIBILIDAD):** Publicar en `wyoloservice2_production` los scripts `benchmark_latency.py`, `benchmark_idle_gpu.py` y `ablation_memory_limits.py` con comandos exactos, datasets de referencia y salidas esperadas; enlazarlos desde Data & Code Availability.

---

**Firma del Revisor:** IEEE Senior Member / Area Editor
**Fecha:** 2026-08-12
**Próxima ronda:** Tras Modificaciones 1-3 (título, evidencia experimental y ablación), re-evaluación completa. Los cambios 4-9 son pre-requisito para publicación.


