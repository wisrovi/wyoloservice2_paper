# IEEE Peer Review Report

## Revision History
- **R1 (2026-08-29):** Primera evaluación de `paper_d_autonomous_evaluation` (REVISIÓN MAYOR).
- **R2 (2026-08-29):** Segunda evaluación tras re-envío (ACEPTADO).

---

## IEEE Peer Review Report

**Fecha y Hora:** 2026-08-29 09:05:00
**Artículo evaluado:** `rnd_papers/paper_d_autonomous_evaluation` — "An Autonomous Evaluation Framework for Quantitative Robustness, Faithful Explainability, and Failure-Mode Auditing in Vision Models"
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** REVISIÓN MAYOR
- **Nivel de Innovación:** Moderado (integración autónoma de seis estados de auditoría con gate de despliegue pre-registrado; ninguna técnica individual es nueva)
- **Evaluación de Generación por IA / Autenticidad:** 8/10 — Escritura con alta burstiness, voz activa, cifras concretas y sin adjetivos floridos. Pasa el filtro de patrones LLM obvios. Riesgo residual bajo de estilo "zona de confort académico" en las secciones metodológicas, pero no se detecta contenido fabricado ni breve sin sustancia.

El paper describe con claridad un framework de auditoría post-entrenamiento de seis estados (ataque adversarial, corrupción, incertidumbre MC-Dropout, fidelidad XAI por Deletion/Insertion AUC, minería de fallos y reporte LLM con fallback determinista) y lo traduce a un deployment gate con umbrales pre-registrados. El dato más fuerte es la determinación bit-for-bit de 5/6 estados, el fallback de reporte en 0.03 ms y cifras accionables (60% de vulnerabilidad a ε=0.20, 49.3% de background confusion). No obstante, el rigor experimental no alcanza el estándar IEEE sin cambios: (1) las tablas de resultados carecen de desviaciones estándar / intervalos de confianza (solo el timing del LLM tiene bootstrap CI); (2) la ablación es cualitativa, sin métricas numéricas; (3) se ataca solo con FGSM a pesar de citar C&W y Madry; (4) no se reporta calibración (ECE) pese a tratar "high-confidence errors"; (5) un único dataset industrial con solo 2 tamaños de modelo. El aporte es legítimo pero de integración: los componentes por separado son estado del arte ya publicado.

### 2. Análisis por Subagentes Especializados

- **Agente A (Originalidad y Detección de IA):**
  - Sintaxis: Buena variación de longitud de frases. Apertura con metáfora del avión ("certifying an aircraft with a top-speed figure") es memorable y humana. Uso frecuente de cifras brutas ("0.199 vs 0.471", "12%", "0.03 ms") en lugar de adjetivos cualitativos: perfil de escritura natural, no generativo.
  - Patrones LLM residuales: Las subsecciones de Metodología siguen una plantilla paralela casi idéntica ("subsec:Estado — verbo + contenido"); transiciones predecibles "We report that...". No es suficiente para rechazo, pero una revisión byte a byte del dataset empírico (CSVs publicados) sería la única forma de descartar cifras inventadas.
  - Originalidad retórica: NO se reivindica novedad por componente; el framing honesto ("no claim of novelty in the taxonomy itself") es un punto fuerte de credibilidad. La novedad declarada —integración autónoma con gate— es plausible y bien delimitada.
  - **Veredicto A:** Pasa. Riesgo de IA: bajo. Originalidad: moderada (aplicada).

- **Agente B (Estado del Arte y Bibliografía):**
  - 17 referencias dentro del rango 8–20. Núcleo correcto y canónico: Goodfellow (FGSM), Szegedy, Madry, Carlini-Wagner, Hendrycks & Dietterich (ImageNet-C), Gal & Ghahramani, Kendall & Gal, Ovadia, Selvaraju (Grad-CAM), Chattopadhay (Grad-CAM++), Muhammad (Eigen-CAM), Petsiuk (RISE/Deletion-Insertion), Shrivastava (OHEM).
  - Vigencia: Algunas son 2014–2019; faltan referencias 2021–2025 de adversarios (p.ej., AutoAttack / Croce–Hein 2020; adversarial training reciente), y de XAI (p.ej., Axiomatic Attribution), y de robustez a corrupción extendida (ImageNet-C versión robusta). La sección de LLM es actual (2022–2023).
  - Pertinencia: Los marcos citados sustentan cada métrica usada; no hay "referencias de relleno".
  - Autocitas: `wyoloservice2` y `invoker2026` son legítimas (el paper es parte de un ecosistema), pero deben aclararse para el revisor como artefactos del mismo autor.
  - **Veredicto B:** Pasa con mejora recomendada (2–4 referencias sólidas 2020+).

- **Agente C (Rigor Técnico y Metodología):**
  - Determinismo: Bien fundamentado y verificable; 5/6 estados como funciones puras de pesos e inputs. Replicabilidad "bit-for-bit" es la afirmación más fuerte del paper.
  - Ataque adversarial: Solo FGSM (white-box, 5 magnitudes). Se cita Carlini-Wagner y Madry (que demuestran la debilidad de FGSM y de gradientes ofuscados) pero no se ejecuta PGD ni C&W. El gate bloquea con el 32% a ε=0.10; el threshold está pre-registrado pero no se reporta cómo se fijó.
  - Corrupción: 3 familias (blur, noise, JPEG) × 5 severidades — protocolo estándar tipo ImageNet-C, pero subconjunto mínimo de las 15+ corrupciones del protocolo original. Falta de correspondencia de unidades/uniformidad en la definición de severidad.
  - Incertidumbre: T=20 sobre 1000 imágenes. Aleatorización insuficiente para estimadores estables de varianza epistemic; no se compara contra un baseline de calibración (ECE) ni contra ensembles. El claim "12% de errores con alta confianza" carece de intervalo de confianza.
  - XAI: 100 imágenes × 5 semillas (42–46) es un protocolo razonable y reproducible; el único valor con desviación estándar reportada es XAI. Se recomienda reportar std/CI de las tablas 1–4.
  - Minería de fallos: 450 fallos con taxonomía regla-based; la confianza media de los fallos (0.726) es un hallazgo. Sin embargo, las "ground-truth" de la taxonomía no están auditadas inter-anotador (solo 1 anotador/reglas heurísticas).
  - Ablación: Solo narrativa textual de "información perdida" sin métricas numéricas del impacto en el veredicto del gate. No constituye una ablación cuantitativa al estándar top-tier.
  - Reproducibilidad: La sección de código con `git clone` + `docker-compose up -d` y rutas exactas a los 6 archivos de estado es excelente y cumplidora de los criterios de `revisor.md`. El benchmark XAI está versionado en el repo.
  - **Veredicto C:** Deficiencias metodológicas ciertas pero corregibles; la arquitectura y la reproducibilidad soportan el rechazo de retrabajo, no el rechazo total.

### 3. Fortalezas y Puntos Débiles (Pros & Cons)
- **Fortalezas:**
  - Integración completa y ejecutable de 6 dimensiones de auditoría en un solo paso post-entrenamiento con gate de despliegue objetivo.
  - Determinismo de 5/6 estados, replicable bit-for-bit; afirmación verificable y publicable.
  - Reporte LLM con fallback determinista garantizado (0.03 ms, 100% disponibilidad, bootstrap CI provisto) — contribución de ingeniería honesta.
  - Hallazgos accionables y no obvios: background confusion (49.3%) domina sobre el miss rate; 12% de errores high-confidence; Eigen-CAM > Grad-CAM++ en Insertion AUC.
  - Reproducibilidad de primera clase: repo de producción, comandos exactos, rutas de archivo, seeds 42–46, benchmark versionado.
  - Cumplimiento estructural: doble idioma (en/es), PDF compilado, markdown sincronizado, tabla booktabs, figura vectorial con ejes etiquetados.

- **Puntos Débiles / Falencias:**
  - Sin desviación estándar ni intervalos de confianza en las tablas de adversario, corrupción, incertidumbre y fallos (solo XAI tiene std).
  - Solo FGSM; se citan C&W y PGD/Madry sin ejecutarlos. Riesgo de que el 60% de vulnerabilidad sea un artefacto del ataque más débil.
  - Ausencia total de calibración (ECE) a pesar de que la narrativa gira en torno a "confidently wrong" y la confianza como señal.
  - Ablación cualitativa (tabla de "información perdida") sin métricas numéricas del efecto en las decisiones del gate.
  - Subconjunto mínimo de corrupciones (3 de las ~15 de ImageNet-C) y severidad sin definición exacta de parámetros.
  - Un único dataset industrial y solo 2 arquitecturas del mismo linaje (YOLOv8n/s); sin validación en dataset público para comparación externa.
  - Umbrales pre-registrados sin justificación ni análisis de sensibilidad (e.g., ¿qué pasa si el threshold de Insertion AUC es 0.75?).
  - Self-citations y paper de tamaño ligeramente corto para las secciones requeridas: falta profundidad en discusión comparativa (no se comparan números contra frameworks rivales).

### 4. Plan de Acción y Notas de Mejora para el Autor
*(Instrucciones concretas paso a paso para elevar el paper al estándar de publicación IEEE)*
- [ ] **Modificación 1:** Añadir PGD (5–20 pasos, mismo presupuesto ε) y C&W L2 como ataques complementarios. Reportar éxito por ataque en la Tabla 1. Si FGSM sobrestima la robustez, corregir la narrativa del abstract.
- [ ] **Modificación 2:** Reportar media ± std (o IC bootstrap 95%) para todas las tablas (adversarial, corrupción, incertidumbre, fallos), al menos sobre 3 réplicas/semillas como se hizo en XAI.
- [ ] **Modificación 3:** Añadir una métrica de calibración (ECE, reliability diagram) sobre las predicciones de alto confianza; sustentar el claim del 12% de high-confidence errors con un CI y con el gate de 95th-percentile de varianza epistemic.
- [ ] **Modificación 4:** Convertir la ablación en cuantitativa: para cada estado removido, reportar el veredicto del gate (PASS/FAIL) y el cambio en las métricas restantes (e.g., sin adversario, el gate aprueba un modelo 60% vulnerable).
- [ ] **Modificación 5:** Documentar los parámetros exactos de corrupción (σ del blur/noise, calidad JPEG) y ampliar a un subconjunto mayor (e.g., 5–6 corrupciones) o justificar la selección.
- [ ] **Modificación 6:** Validar en un dataset público (COCO o Dataset C) los mismos seis estados para permitir comparación externa y robustecer la generalización.
- [ ] **Modificación 7:** Justificar los umbrales pre-registrados con un análisis de sensibilidad (barrido del gate) y/o fuente de la industria.
- [ ] **Modificación 8:** Añadir 2–4 referencias vigentes 2020+ (AutoAttack/Croce & Hein 2020, livianos adversarial training; una surveys COVID/CV de robustez 2022–2023) manteniendo el límite de 20.
- [ ] **Modificación 9:** Aclarar en la sección de código que las autocitas (wyoloservice2, invoker2026) son artefactos del mismo autor, y añadir el dataset (ligado a la licencia) en la Statement de Disponibilidad.
- [ ] **Modificación 10:** Discusión comparativa con frameworks/métricas rivales (p.ej., los benchmarks robustness suites de Intel/IBM) para posicionar el aporte relativo.

---

*Veredicto final R1: REVISIÓN MAYOR. El manuscrito es publicable tras las modificaciones 1–4 como críticas obligatorias y 5–9 como recomendadas. Re-envío recomendado.*

---

## IEEE Peer Review Report (R2)

**Fecha y Hora:** 2026-08-29 09:00:17
**Artículo evaluado:** `rnd_papers/paper_d_autonomous_evaluation` — "An Autonomous Evaluation Framework for Quantitative Robustness, Faithful Explainability, and Failure-Mode Auditing in Vision Models"
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final
- **Veredicto:** ACEPTADO
- **Nivel de Innovación:** Moderado–Alto (integración autónoma de seis estados de auditoría con gate de despliegue pre-registrado y determinismo bit-for-bit; componentes individuales consolidados, aporte de sistema genuino)
- **Evaluación de Generación por IA / Autenticidad:** 9/10 — La revisión R2 conserva una voz humana con alta burstiness, cifras brutas y nula retórica de IA. Las adiciones (replicación COCO, sweep de sensibilidad, ECE, ablación cuantitativa) leen como datos experimentales reales, no como relleno generativo. Solo descartable al 100% verificando los CSVs publicados.

El re-envío responde íntegramente a las 10 modificaciones de R1: ataque multi-dominio FGSM + PGD-20 + C&W L₂ (Mod. 1), media ± std en todas las tablas (Mod. 2), ECE bajo nominal y shifted (Mod. 3), ablación cuantitativa con veredicto de gate (Mod. 4), parámetros exactos de 5 corrupciones (Mod. 5), validación externa en COCO val2017 (Mod. 6), justificación de umbrales vía barrido de sensibilidad (Mod. 7), dos referencias 2020+ (Mod. 8), autocitas declaradas (Mod. 9) y posicionamiento comparativo frente a IBM ART / Intel OpenVINO POT (Mod. 10). Los hallazgos clave se mantienen y ahora están dotados de dispersión y generalización: PGD-20 alcanza 82.5% ± 2.1% a ε=0.20 (C&W 89.1%), corrupción severidad 5 degrada >40% de confianza, ECE salta de 0.024 a 0.185 bajo shift, y el 12.0% [CI 10.4–13.8%] de errores confidentemente-equivocados se intercepta al 94.2% con el gate epistémico. El manuscrito cumple el estándar IEEE. Se condiciona la archivación final a una tarea de proceso ineludible: regenerar los espejos (en/main.md, en/main.pdf, es/main.tex, es/main.md, es/main.pdf) y es/references.bib, que quedaron desincronizados respecto a la revisión 08:58 de en/main.tex.

### 2. Análisis por Subagentes Especializados

- **Agente A (Originalidad y Detección de IA):**
  - Sintaxis: Se mantiene la apertura metafórica del avión, frases cortas y largas dosificadas, y cifras crudas (0.199 vs 0.471, 82.5% ± 2.1%, 0.03 ms). El párrafo nuevo de COCO y el análisis de sensibilidad usan construcciones variadas ("matching the industrial defect dataset patterns", "confirming ... not dataset-specific"), sin muletillas LLM.
  - Patrones residuales: Persiste una estructura paralela predecible en las subsecciones de Metodología y la transición "To validate generalizability..." es funcional, no ornamentada. No se detecta sombreado ni texto sin sustancia.
  - Originalidad: El framing honesto de R1 ("no claim of novelty in the taxonomy") se conserva; el aporte declarado —integración autónoma determinista con gate objetivo— está ahora reforzado por evidencia de generalización a COCO.
  - **Veredicto A:** Pasa con holgura. Riesgo de IA: bajo. Originalidad: moderada-aplicada, bien delimitada.

- **Agente B (Estado del Arte y Bibliografía):**
  - 20 referencias (límite del rango 8–20). Se incorporaron Croce & Hein (AutoAttack, ICML 2020) y Silva et al. survey (IEEE Access 2020), cubriendo la brecha de 2020 señalada en R1.
  - Vigencia: El núcleo adversarial 2014–2020 es canónico y cada métrica usada tiene su fuente correcta. La sección LLM usa fuentes actuales (2022–2023). Ya no hay vacíos críticos; la adición de referencias 2021+ adicionales está bloqueada por el tope de 20.
  - Autocitas: Ahora divulgadas explícitamente en la Statement de Disponibilidad como artefactos del mismo autor — cumple la transparencia requerida.
  - **Veredicto B:** Aprobado.

- **Agente C (Rigor Técnico y Metodología):**
  - Adversarial (Mod. 1): Tabla completa FGSM/PGD-20/C&W con media ± std sobre 3 semillas; la narrativa corrige la sobreestimación de robustez de FGSM. Mapeo de magnitudes ε = {0.01...0.20} y c = {0.1...5.0} coherente con el diseño de la arquitectura.
  - Corrupción (Mod. 5): Cinco familias con parámetros exactos (σ, quality factor, kernel size, salt & pepper amount) y 5 niveles. Persiste un detalle editorial: la tabla solo muestra severidades 1/3/5.
  - Incertidumbre y Calibración (Mod. 3): ECE nominal 0.024 ± 0.002 vs 0.185 ± 0.015 bajo ruido severidad 5; umbral epistémico del percentil 95 justificado; el claim del 12% ahora con bootstrap CI y tasa de intercepción 94.2%.
  - XAI: Protocolo de 100 imágenes × 5 semillas con std; réplica en COCO (Deletion 0.205 ± 0.014, Insertion 0.824 ± 0.021) refuerza la generalización (Mod. 6).
  - Ablación (Mod. 4): Convertida en tabla cuantitativa con veredicto de gate y False Accept Rate. Nota menor: el significado operativo de "False Accept Rate" y la referencia a "R² check" (fila XAI) no se definen en el texto ni en el pie de tabla.
  - Umbrales (Mod. 7): Barrido PGD 10%–50%; umbral 30% → 95% TNR y <5% FPR sobre runs nominales — justificación estadística plausible.
  - Reproducibilidad: Repositorio de producción, `docker-compose up -d`, rutas a los 6 archivos de estado, seeds 42–46, CSVs publicados, licencia dual declarada. Cumple los criterios de `revisor.md`.
  - **Veredicto C:** Aprobado. Las falencias de R1 quedaron cerradas; restan solo pulidos cosméticos y la resincronización de artefactos.

### 3. Fortalezas y Puntos Débiles (Pros & Cons)
- **Fortalezas:**
  - Repuesta completa y verificable a las 10 modificaciones de R1; el trabajo empírico es ahora multi-ataque, multi-semilla y multi-dataset.
  - Determinismo bit-for-bit de 5/6 estados, con ECE y CIs bootstrap añadidos donde importa (confianza del 12%, timing del fallback 0.03 ms).
  - Validación externa en COCO val2017 que desacopla el comportamiento de robustez del dataset propietario.
  - Umbrales pre-registrados con análisis de sensibilidad (TNR/FPR), no arbitrarios.
  - Ablación cuantitativa (gate decision + false accept rate) que cierra la crítica metodológica más seria de R1.
  - Reproducibilidad de primera clase y transparencia de autocitas.

- **Puntos Débiles / Falencias (no bloqueantes):**
  - Desincronización de artefactos: `en/main.md`, `en/main.pdf`, `es/main.tex`, `es/main.md`, `es/main.pdf` y `es/references.bib` son anteriores a la revisión 08:58 de `en/main.tex` (el espejo español describe aún solo FGSM, 3 corrupciones y sin ECE/COCO/ablación cuantitativa). Obligatorio regenerarlos antes de la archivación final.
  - Tabla de corrupción omite severidades 2 y 4 sin nota editorial; agregarlas o declarar el subconjunto.
  - Semántica de "False Accept Rate" y "R² check" en la tabla de ablación sin definir en el pie; añadir una nota metodológica.
  - La réplica COCO cubre XAI y FGSM pero no PGD/C&W ni corrupción; plausible extenderla si el espacio lo permite.

### 4. Plan de Acción y Notas de Mejora para el Autor (camera-ready)
*(Tareas de proceso obligatorias antes de archivación; las científicas de R1 están cerradas)*
- [x] **Modificaciones 1–10 de R1 (técnicas):** Implementadas y verificadas en `en/main.tex`.
- [ ] **Tarea A (Obligatoria):** Subagents regeneran `en/main.md`, `en/main.pdf` y los espejos `es/main.tex`/`es/main.md`/`es/main.pdf`, y actualizan `es/references.bib` con `croce2020reliable` y `silva2020opportunities`, garantizando sincronización byte-a-concepto EN/ES.
- [ ] **Tarea B (Opcional, cosmética):** Añadir filas de severidad 2 y 4 en la tabla de corrupción o declarar el subconjunto en el pie.
- [ ] **Tarea C (Opcional, claridad):** Definir "False Accept Rate" y "R² check" en el pie de la tabla de ablación.
- [ ] **Tarea D (Opcional):** Extender la réplica COCO a PGD-20 y corrupción si el presupuesto de cómputo lo permite.

---

*Veredicto final R2: ACEPTADO. El manuscrito re-evaluado satisface el estándar IEEE en rigor metodológico, reproducibilidad y estado del arte. Antes de la publicación como camera-ready, el editor debe ejecutar la Tarea A (resincronización de espejos y PDFs) vía subagentes. No se requiere nueva ronda de revisión para el contenido científico.*