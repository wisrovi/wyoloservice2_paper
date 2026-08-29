---
# Historial de Revisiones
## IEEE Peer Review Report — Revisión 3 (paper_c_domain_shift_prediction)
**Fecha y Hora:** 2026-08-29 10:04:23
**Artículo evaluado:** `paper_c_domain_shift_prediction` (rnd_papers/)
**Revisor:** IEEE Senior Member / Area Editor
**Estado del manuscrito:** Re-envío tras Revisión 2 (se verificó contra los artefactos actuales: `en/main.tex` @09:57, `en/benchmark_prediction.py`, `en/domain_pairs.npz`, `en/references.bib` @09:56, PDF/MD @09:58). El autor corrigió los tres bloqueos numéricos de la Revisión 2; la verificación reproduce ahora el núcleo del manuscrito de forma exacta.

### 1. Resumen Ejecutivo y Veredicto Final (Revisión 3)
- **Veredicto:** REVISIÓN MAYOR / RE-ENVÍO (con bloqueos acotados a 3 correcciones concretas; el manuscrito está a una iteración corta de la aceptación)
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 8/10 — redacción natural, alta burstiness, cifras no redondeadas y tono pragmático; la honestidad estadística del autor (reportar p=0.0713 y VIF=21.4 en lugar de sobrevender SC) es señal clara de redacción humana genuina. Persisten redundancia abstract↔contribuciones y frases largas mecánicas de relleno (Agente A).

**Veredicto conciso:** La Revisión 2 exigía tres correcciones numéricas y el autor las atendió: ahora se reporta β₂=2.475 como *marginalmente* significativo (t=2.438, p=0.0713, df=4, VIF=21.4) y se replantea SC como covariable de diagnóstico, no como driver primario; el SC-only LOO MAE se corrigió a 1.92 pp; y las coberturas bootstrap (FID-only 57.1%, SC-only 71.4%, FID+SC 100%) se reproducen **exactamente** con B=1000 y seed 42 (LOO). Los resultados centrales son sólidos y verificables: R²=0.988/MAE 1.05 in-sample, LOO 1.45/1.17/1.92, hold-out Day→Night 32.9 pp [31.5–34.2] vs. 30.4 reales. **Quedan 3 bloqueos para la aceptación:** (1) el párrafo del gate contiene una contradicción interna verificable — la lista nominal de pares señalados incluye "RealDay→Rain", que con el protocolo declarado NO se señala (LB=7.52), y el "CI lower bound −0.91 pp" no se reproduce (7.52 LOO / 10.21 in-sample); (2) `dollar2021rethinking` ("Rethinking the FLOPs Metric…", arXiv:2103.11181) es una referencia que **no existe** — el paper real Dollár–Singh–Girshick 2021 es "Fast and Accurate Model Scaling" (arXiv:2103.06877), por lo que hay una cita fabricada aún en la bibliografía; (3) el corpus Monte Carlo de 20 pares y la ablación "3/15 silent failures" siguen sin artefactos liberados, con lo que dos afirmaciones de robustez del abstract no son reproducibles. Recomendación: corregir el párrafo del gate, sustituir/corregir dichas referencias (además `taori2020` escribe "Ludwig, Ludwig" — el autor es Ludwig Schmidt), liberar datos del corpus ampliado y resincronizar ES.

### 2. Análisis por Subagentes Especializados (Revisión 3)

#### Agente A (Originalidad y Detección de IA)
- Sintaxis auténtica: oraciones cortas alternadas con párrafos técnicos; cifras específicas (94.2→63.8%, t=2.438, p=0.0713, VIF=21.4) que un LLM genérico no inventa; tono objetivo y sin buzzwords. Burstiness alta.
- El movimiento de honestidad estadística (fantasma: reportar `p = 0.0713` pese a querer justificar SC; y "Rather than a primary driver…") es el marcador humano más fuerte del documento.
- Puntos de riesgo: abstract y contribuciones repiten casi idénticas cifras (redundancia mecánica); el ítem 3 del abstract sigue duplicando la discusión de cobertura; frases latiguillo de transición muy uniformes ("To assess…", "This validates…"). Originalidad técnica incremental: FID+OLS+bootstrap es composición conocida; el aporte diferencial (SC como regularizador/calibrador) está honestamente presenta.
- Veredicto A: Redacción auténtica, 8/10; originalidad técnica moderada.

#### Agente B (Estado del Arte y Bibliografía)
- Confirmado: se mantiene el SOTA real incorporado en la Revisión 2 (Taori 2020, Recht 2019, Hendrycks 2019, Garg 2022/ATC, Deng 2023, Ben-David 2010, Heusel 2017), autoría de `sun2017revisiting` correcta.
- **HALLAZGO CRÍTICO — referencia fabricada en esta revisión:** `dollar2021rethinking` ("Rethinking the FLOPs Metric for Deep Learning Inference", arXiv:2103.11181) **no existe**. Verificación por búsqueda web: el único título Dollár–Singh–Girshick de 2021 con esa temática es "Fast and Accurate Model Scaling" (arXiv:2103.06877). El preprint citado ni su arXiv ID aparecen en ningún índice. Es exactamente la clase de defecto de integridad que ya se eliminó en la Revisión 1 (`zhang2024robust`). Debe sustituirse por la referencia real o eliminarse.
- Errores adicionales: `taori2020measuring` consigna autor final "Ludwig, Ludwig" (debe ser **Schmidt, Ludwig**); `xu2020domain` (IEEE TIP 2021) sigue tipado como `@inproceedings` (debe ser `@article`); título de `garg2022leveraging` alterado ("…Predict Out-of-Distribution Accuracy" vs. título real "…Out-of-Distribution Performance"); `deng2023unsupervised` y `chen2022domain` sin DOI/páginas verificables.
- Autocitas (wyoloservice2 + invoker2026 ≈ 2/18) en rango aceptable; `invoker2026` (ICSE 2026, futuro) sin confirmación de publicación.
- Veredicto B: marco teórico adecuado y vigente, pero la presencia de una cita fabricada es bloqueante de integridad académica hasta corregirse.

#### Agente C (Rigor Técnico y Metodología)
Verificación numérica reproducida desde `domain_pairs.npz` (B=1000, seed 42, protocolo LOO):
- **Reproducidos exactamente (mejora mayor sobre Revisión 2):** FID-only R²=0.988, MAE in-sample 1.05, β₁=0.250, intercepto 0.457; FID+SC R²=0.995, MAE 0.62, β₂=2.475, t=2.438, p=0.0713 (df=4), VIF=21.4 (ρ(FID,SC)=0.976); LOO MAE: 1.45 (FID-only), 1.17 (FID+SC), 1.92 (SC-only); cobertura LOO: 57.1% (4/7), 71.4% (5/7 SC-only), 100% (7/7 FID+SC); hold-out Day→Night pred 32.9 pp, CI [31.4–34.2] (el paper indica [31.5–34.2], ✓ por redondeo), FID+SC 32.6 [30.0–33.7] vs. paper [30.0–33.5] (dif. 0.2 pp).
- **Contradicción remanente (gate):** con LB>10 en LOO bootstrap, los pares señalados son fid={72.3, 90.7, 127.6, 142.9, 149.9} → 5/7 (conteo ✓). Pero el texto nombre "Synthetic→Night, RealDay→Rain, Day↔Night, Clear↔Rainy e Indoor↔Outdoor" incluye **RealDay→Rain** (fid=43.8, d=11.03), que NO se señala (LB=7.52); el par fid=149.9 (d=40.0) que sí se señala no aparece en la lista. Además "…whose actual degradation exceeds 10 pp" es falso: **6 de 7 pares** superan 10 pp reales. El "conservative CI lower bound of −0.91 pp" para el par de 11.03 pp no es reproducible por ningún protocolo probado (LOO=7.52; in-sample=10.21).
- **Límite estadístico N=7:** cobertura 57.1% vs. 100% con N=7 no es distinguible estadísticamente (Wilson 95% para 4/7 ≈ [0.25, 0.84]; para 7/7 ≈ [0.59, 1.00] — intervalos solapados). El manuscrito ya no sobrevende la ganancia de cobertura (bien), pero debería cuantificar la incertidumbre de la cobertura (Clopper-Pearson/Wilson) o ampliar el corpus.
- **No reproducibles (sin artefactos):** Monte Carlo "M=20 synthetic pairs" (R²=0.968±0.004, MAE 1.15±0.08 pp; SC 0.992±0.002, 0.68±0.04) — sin datos ni script; ablación "3/15 silent failures" (5 seeds × 3 pares severos) — sin definición de pares/seeds; overhead "2.1 s" — sin protocolo ni mediciones; "YOLO26n" — sin referencia.
- Menor: el `.npz` expone solo fid/sc/d sin nombres de pares (el mapeo fid↔par no es trazable); el ES des-sincronizado omite la cláusula final del párrafo del gate; solo 1 figura (no hay diagrama de arquitectura del pipeline pese a la regla de figuras del repo); ausencia de desglose por variante YOLO/seeds con barras de error.
- Veredicto C: el diseño experimental y la integridad numérica mejoraron sustancialmente y el núcleo es reproducible; bloquean aún la contradicción del gate, la cita fabricada y la falta de artefactos de robustez.

### 3. Fortalezas y Puntos Débiles (Pros & Cons)
- **Fortalezas:**
  - Núcleo experimental reproducible exactamente (coeficientes, R², MAE, LOO, coberturas, hold-out): 8 de 9 cifras centrales verificadas contra `domain_pairs.npz`.
  - Honestidad estadística: reportar t=2.438/p=0.0713/VIF=21.4 y reformular SC como regularizador es el estándar que pide el revisor; mejora notable frente a la Revisión 2.
  - SOTA de predicción de rendimiento correctamente incorporado (Taori/Recht/Hendrycks/Garg/Deng) y gap de investigación defendible.
  - Problema real y crítico en MLOps industrial; bajo costo marginal (+2.1 s, embeddings ya existentes); gate conservador por cota inferior; ablaciones completas (FID-only / FID+SC / SC-only / sin gatekeeper).
  - Estructura IEEE completa, EN/ES/PDF/MD sincronizados en el momento de compilación (09:58).
- **Puntos Débiles / Falencias:**
  - Contradicción interna en el párrafo del gate (nombres de pares señalados ≠ cómputo; "6 de 7 superan 10 pp"; "CI −0.91" irreproducible).
  - Referencia fabricada `dollar2021rethinking` + errores en `taori2020` (Ludwig/Ludwig), `xu2020domain` (tipo) y título de `garg2022leveraging`.
  - Robustez (20 pares Monte Carlo, 3/15 silent failures, 2.1 s) sin artefactos liberados.
  - N=7: coberturas no distinguibles estadísticamente; VIF=21.4.
  - ES fuera de sincronía en el párrafo del gate; sin diagrama de arquitectura; "YOLO26n" sin referenciar; sin ORCID.

### 4. Plan de Acción y Notas de Mejora para el Autor
*(Instrucciones concretas paso a paso para elevar el paper al estándar de publicación IEEE)*
- [ ] **Modificación 1 (bloqueante — integridad):** Sustituir `dollar2021rethinking` por la referencia real "Fast and Accurate Model Scaling" (Dollár, Singh, Girshick; arXiv:2103.06877) o eliminarla; ajustar la frase "danger of relying on singular proxy metrics" para que refleje el paper real (o usar una fuente realmente sobre métricas proxy). Corregir `taori2020` (autor final: Schmidt, Ludwig), tipar `xu2020domain` como `@article` y restaurar el título exacto de `garg2022leveraging`.
- [ ] **Modificación 2 (bloqueante — coherencia):** Reescribir el párrafo del gate con los datos verificados: 6/7 pares superan 10 pp reales; el gate (LB>10, LOO) señala exactamente 5 (indique fid/pares correctos: fid=72.3, 90.7, 127.6, 142.9, 149.9) y no señala los 2 de bajo riesgo (fid=18.3, 43.8); reportar el LB real del par de 11.03 pp (7.52, no −0.91) o eliminar la cifra. Liberar en `domain_pairs.npz` el mapeo fid↔nombres de pares.
- [ ] **Modificación 3 (bloqueante — reproducibilidad):** Liberar artefactos del corpus ampliado (script/simulación M=20 del Monte Carlo; selección de los 3 pares severos y las 5 seeds de la ablación "3/15") para que R²=0.968±0.004 y "20% silent failures" sean verificables; o degradarlas a claim de ingeniería etiquetado como no publicado.
- [ ] **Modificación 4:** Cuantificar la incertidumbre de la cobertura: reportar intervalos Wilson/Clopper-Pearson para 57.1% (4/7) y 100% (7/7) y explicitar que las diferencias no son significativas con N=7, o ampliar el número de pares para dar poder a la comparación SC vs. FID-only.
- [ ] **Modificación 5:** Añadir el diagrama de arquitectura del pipeline (extracción → FID → SC → OLS/bootstrap → gate JSON) como figura renderizada de una columna con `\includegraphics[width=\linewidth,…]`.
- [ ] **Modificación 6:** Desglosar resultados por variante YOLO (n/s/m/YOLO26n) y por seed (media±std) con barras de error en la Figura 1; documentar el protocolo del profiling de 2.1 s (hardware, N imágenes, mediana vs. media).
- [ ] **Modificación 7:** Referenciar formalmente "YOLO26n" (o renombrarla como variante no publicada y eliminarla de la lista de modelos evaluados); añadir ORCID del autor.
- [ ] **Modificación 8:** Resincronizar el ES (`es/main.tex`) para que incluya la cláusula final del párrafo del gate, y regenerar PDF/MD/ES tras aplicar los cambios con la secuencia pdflatex→bibtex→pdflatex→pdflatex.

---
## IEEE Peer Review Report — Revisión 2 (paper_c_domain_shift_prediction)
**Fecha y Hora:** 2026-08-29 09:55:37
**Artículo evaluado:** `paper_c_domain_shift_prediction` (rnd_papers/)
**Revisor:** IEEE Senior Member / Area Editor
**Estado del manuscrito:** Re-envío tras Revisión 1 (los hallazgos de la revisión previa fueron mayormente atendidos por el autor; se verificó contra los artefactos actuales: `en/main.tex`, `en/benchmark_prediction.py`, `en/domain_pairs.npz`, `en/references.bib`).

### 3. Resumen Ejecutivo y Veredicto Final (Revisión 2)
- **Veredicto:** REVISIÓN MAYOR / RE-ENVÍO
- **Nivel de Innovación:** Moderado (predictor calibrado FID→ΔmAP con CI bootstrap aplicado a detección de objetos industrial; aporte de ingeniería sólido y honesto, novedad algorítmica incremental)
- **Evaluación de Generación por IA / Autenticidad:** 7.5/10 — redacción natural, alta "burstiness", datos concretos y tono pragmático. Ya no se detectan refuerzos placeholder en la bibliografía; la escritura es creíblemente humana. Aún hay redundancia mecánica en la enumeración de contribuciones vs. el abstract.

**Veredicto conciso:** El autor atendió la mayoría de los bloqueos de la Revisión 1: la bibliografía se rehizo (se eliminó la cita fabricada `zhang2024robust` / arXiv:2403.12345, se corrigió la autoría de `sun2017revisiting`, y se incorporó el SOTA real: Taori 2020, Recht 2019, Hendrycks 2019, Garg 2022/ATC, Deng 2023), y el `benchmark_prediction.py` ahora lee el `.npz` (R²=0.988/MAE 1.05 reproducibles). **Sin embargo, la verificación numérica contra los artefactos liberados revela tres contradicciones internas que impiden la aceptación:** (1) el paper afirma β₂=2.475 significativo con t=3.12 y p<0.05, pero el `.npz` arroja t=2.44/p=0.071 (NO significativo; además VIF=21.4 = colinealidad severa FID–SC); (2) el ablation reporta SC-only LOO MAE=2.85 pp, pero los datos dan 1.92 pp; (3) el gate "flags exactly the 5 pairs" contradice el propio `.npz`, donde 6 de 7 pares superan los 10 pp y el gate se activa en 6/7. Las coberturas 71.4%/95.0% tampoco se reproducen (57.1%/100% en mi cómputo LOO-bootstrap). Notas críticas: (1) reportar β₂ con su p-valor real y descartar o redefinir la ganancia de cobertura de SC dado el riesgo de colinealidad, (2) corregir el conteo del gate y el SC-only LOO MAE según `.npz`, (3) liberar los artefactos del corpus ampliado de 20 pares, hoy no reproducibles.

### 4. Análisis por Subagentes Especializados (Revisión 2)

#### Agente A (Originalidad y Detección de IA)
- Sintaxis: se conserva la mezcla de frases cortas de impacto y párrafos técnicos densos; sin cadenas cliché. Burstiness alta; el cuerpo es auténtico.
- Puntos de riesgo: el abstract y las cuatro contribuciones repiten casi las mismas cifras (redundancia tipo LLM); el ítem 3 (cobertura 71.4%→95.0%) se duplica casi literalmente en el resumen. Originalidad técnica limitada: FID + OLS + bootstrap es una composición conocida; el ángulo de complejidad de escena (SC) como calibrador es el aporte genuino, pero su evidencia en esta revisión es estadísticamente débil (ver Agente C).
- Veredicto A: Redacción auténtica (7.5/10); originalidad técnica incremental.

#### Agente B (Estado del Arte y Bibliografía)
- Mejoras confirmadas frente a la Revisión 1:
  1. Se eliminó la referencia placeholder/fabricada `zhang2024robust` (arXiv:2403.12345).
  2. `sun2017revisiting` ahora lista correctamente a Sun, Shrivastava, Singh y Gupta.
  3. Se incorporó el SOTA de predicción de rendimiento bajo shift: Taori et al. 2020, Recht et al. 2019, Hendrycks & Dietterich 2019, Garg et al. 2022 (ATC) y Deng et al. 2023. La afirmación de gap ahora es más defendible.
- Pendientes menores: `xu2020domain` (IEEE TIP, vol.30, 2021) está tipado como `@inproceedings` (debería ser `@article`); `dollar2021rethinking` es un preprint arXiv sin DOI/verificación de páginas; la autocita `invoker2026` (ICSE) fechada en 2026 no está confirmada como publicada. Autocitas en torno al 15-20% (wyoloservice2, invoker2026) dentro del margen aceptable pero a vigilar.
- Veredicto B: Bibliografía adecuada y vigente tras la revisión; defectos cosméticos de tipeo; ningún vacío crítico de SOTA pendiente.

#### Agente C (Rigor Técnico y Metodología)
Verificación numérica reproducida desde `domain_pairs.npz` (única fuente, ya unificada):
- FID-only: R²=0.988, MAE in-sample=1.05 ✓; LOO MAE=1.45 ✓; beta1=0.250 ✓; predicción hold-out Day→Night 32.9 vs 30.4 ✓ (error 2.5 pp).
- FID+SC: R²=0.995, MAE=0.62 ✓; LOO MAE=1.17 ✓; β₂=2.475 ✓.
- **CONTRADICCIÓN CRÍTICA 1 — Significancia de β₂:** El paper afirma "β₂=2.475 significativo (p<0.05, t=3.12)". Reproducción: t=2.438, p=0.0713 (df=4) → **NO significativo**. Además corr(FID,SC)=0.976 y **VIF=21.4** (colinealidad severa). La afirmación de que SC "aporta la varianza explicativa restante" y "eleva la cobertura a nominal" no está respaldada por los datos en N=7.
- **CONTRADICCIÓN CRÍTICA 2 — SC-only LOO MAE:** El paper reporta 2.85 pp en el ablation; el `.npz` arroja LOO MAE=1.92 pp (R²=0.977). Dato no reproducible.
- **CONTRADICCIÓN CRÍTICA 3 — Conteo del gate:** El paper afirma "flags exactly the 5 pairs whose actual degradation exceeds 10 pp and never flags a low-risk pair". En el `.npz`, d=[5.34,11.03,19.84,22.22,30.37,35.81,40.00] → **6 de 7 pares superan 10 pp**; con bootstrap in-sample (LB>10) el gate se activa en **6/7**. La lista nombrada (5 pares, omitiendo el par realday°rain) no coincide con el set alto-riesgo real.
- **Cobertura no reproducible:** El paper cita cobertura LOO 71.4% (FID-only) y 95.0% (FID+SC); mi cómputo LOO-bootstrap da 57.1% y 100%. Dependiente de seed/método, pero no coincide con lo reportado.
- **Corpus ampliado de 20 pares** (R²=0.968±0.004, MAE 1.15±0.08): sin artefacto liberado (no hay datos de BDD100k/COCO/ImageNet-C en el repo) → no reproducible. Resultado presentado como robustez sin evidencia liberada.
- **Ablación "3/15 silent failures"** (5 seeds × 3 pares severos): el denominador y la selección de "3 pares severos" no se derivan de los artefactos liberados; inconsistente con los 6 pares >10 pp del `.npz`.
- **N=7 y fragilidad estadística:** sigue siendo el cuello de botella; 7 pares no sostienen inferencias de cobertura ni la separación FID/SC.
- Menor: SC usa `mean detections` de un YOLOv8n "decoupled, fixed baseline" (el paper declara mitigar el leak; mejoró respecto a la Revisión 1); falta diagrama de arquitectura del pipeline y desglose por variante YOLO/seeds; "YOLO26n" sin referencia.
- Veredicto C: el diseño experimental y la integridad de artefactos mejoraron (datos unificados, números centrales reproducibles), pero tres contradicciones verificables en el texto contra el `.npz` y la fragilidad por N=7 impiden la aceptación en este estado.

### 5. Fortalezas y Puntos Débiles (Pros & Cons)
- **Fortalezas:**
  - Problema real y crítico en MLOps industrial; motivación concreta (94.2%→63.8%) y sin tono comercial.
  - Datos centrales unificados en `domain_pairs.npz`; R²/MAE/beta1/hold-out reproducibles en la práctica.
  - Bajo costo (reusa embeddings InceptionV3; +2.1 s).
  - Ablations presentes (FID-only / FID+SC / SC-only / sin gatekeeper); gate por cota inferior = conservadurismo correcto en espíritu.
  - Bibliografía reinvertida con SOTA real de predicción bajo shift; estructura IEEE completa y bilateral EN/ES sincronizada.
- **Puntos Débiles / Falencias:**
  - β₂ NO significativo (p=0.071 vs. p<0.05 afirmado) y VIF=21.4: la justificación central del modelo SC-augmented no se sostiene.
  - SC-only LOO MAE 2.85 vs. 1.92 real; gate "5 pares" vs. 6/7 reales; coberturas 71.4%/95.0% no reproducibles.
  - Corpus "20 pares" y ablación "3/15" sin artefactos liberados.
  - N=7; colinealidad FID–SC casi perfecta en los 7 pares.
  - Falta figura de arquitectura, desglose por modelo/seed y barras de error.

### 6. Plan de Acción y Notas de Mejora para el Autor
*(Instrucciones concretas paso a paso para elevar el paper al estándar de publicación IEEE)*
- [ ] **Modificación 1 (bloqueante):** Corregir la significancia estadística de β₂. Calcular y reportar el p-valor/valor t REAL desde `domain_pairs.npz` (t≈2.44, p≈0.071). O bien (recomendado) replantear el aporte de SC: dado VIF=21.4, presentar SC como covariable de diagnóstico de colinealidad y NO como factor de mejora de cobertura, o recolectar pares de dominio con SC ortogonal a FID.
- [ ] **Modificación 2 (bloqueante):** Alinear el texto del ablation con los datos: corregir SC-only LOO MAE a ~1.9 pp, y el conteo del gate a su valor real (6/7 pares >10 pp; gate 6/7 in-sample, o recalcular el protocolo de gating reportado) y actualizar la lista de pares.
- [ ] **Modificación 3:** Fijar el pipeline de cobertura: documentar seed, número de resamples (B=1000/2000) y método (LOO vs in-sample) para que las coberturas 71.4%/95.0% sean reproducibles exactamente; si no lo son, reportar el valor empírico real.
- [ ] **Modificación 4 (bloqueante +):** Liberar los artefactos del corpus ampliado (20 pares, BDD100k/COCO/ImageNet-C) y de la ablación "3/15" (definir los 3 pares severos y las 5 seeds); hoy esas cifras (R²=0.968, 20% silent failures) no son verificables.
- [ ] **Modificación 5:** Reportar desglose por variante YOLO (n/s/m/YOLO26n) y por seed (media±std) del ΔmAP y del FID; añadir barras de error en la figura 1.
- [ ] **Modificación 6:** Añadir diagrama de arquitectura del pipeline (extracción → FID → SC → OLS/bootstrap → gate JSON) acotado a una columna.
- [ ] **Modificación 7:** Suavizar el claim de cobertura ("incremento 71.4%→95%") a "la cobertura nominal cae dentro del error de estimación para N=7" o presentar el resultado con intervalo de Wilson ya citado.
- [ ] **Modificación 8:** Pulir la bibliografía: tipar `xu2020domain` como `@article`; verificar/DOI de `dollar2021rethinking`; confirmar publicación de `invoker2026`; referenciar formalmente "YOLO26n".
- [ ] **Modificación 9:** Cuantificar el protocolo de profiling de los 2.1 s (hardware, N de imágenes, mediana vs media).

---
## IEEE Peer Review Report — Revisión 1 (histórico)
**Fecha y Hora:** 2026-08-29 09:41:45 (refinado 09:50)
**Artículo evaluado:** `paper_c_domain_shift_prediction` (rnd_papers/)
**Revisor:** IEEE Senior Member / Area Editor

### 1. Resumen Ejecutivo y Veredicto Final (Revisión 1)
- **Veredicto:** REVISIÓN MAYOR / RE-ENVÍO
- **Nivel de Innovación:** Moderado
- **Evaluación de Generación por IA / Autenticidad:** 7.5/10

**Veredicto conciso:** El paper modela la degradación pre-despliegue de mAP bajo covariate shift como regresión lineal sobre FID con intervalos bootstrap. La idea es útil y bien contada, pero adolecía de tres defectos de fondo: (1) potencia estadística insuficiente (N=7), (2) datos reproducibles inconsistentes y (3) bibliografía con referencias placeholder/fabricadas y vacuos de SOTA. (Ver análisis detallado en el estado original del manuscrito; la mayoría de estos bloqueos fueron atendidos en el re-envío evaluado en la Revisión 2.)

### 2. Análisis por Subagentes Especializados (Revisión 1 — resumen)
- **Agente A:** Redacción auténtica (7.5/10); originalidad técnica incremental.
- **Agente B:** Referencia fabricada `zhang2024robust` (arXiv:2403.12345), error de autoría en `sun2017revisiting`, etiquetas bibliográficas erróneas, autocitas al 20% y ausencia del SOTA de predicción de rendimiento (Taori/Recht/Hendrycks/Garg/Deng).
- **Agente C:** Dos series de datos rivales (`npz` vs script), N=7 frágil, gate incoherente, coberturas sin significancia, definición de SC con leak parcial.
- **Fortalezas:** problema real, propuesta de bajo costo, ablations, gate conservador, estructura IEEE.
- **Puntos débiles:** reproducibilidad quebrada, N=7, claims de gate contradichos, bibliografía deficiente, "no prior work" indefendible.

### Plan de Acción (Revisión 1 — para trazabilidad)
- [x] Unificar la serie de datos (`npz` como fuente única).
- [x] Corregir la sección de gating y aclarar cota inferior in-sample vs LOO.
- [*] Ampliar el corpus experimental (parcial: solo se declara; falta liberar artefactos).
- [ ] Añadir inferencia estadística real para β₂ (pendiente — ver Revisión 2, Modificación 1).
- [x] Rehacer la bibliografía (eliminar refs fabricadas, corregir autorías, incorporar SOTA).
- [x] Suavizar la afirmación de gap.
- [ ] Añadir diagrama de arquitectura y desglosar denominador 15 (pendiente).
- [ ] Referenciar "YOLO26n" y cuantificar profiling (pendiente).
