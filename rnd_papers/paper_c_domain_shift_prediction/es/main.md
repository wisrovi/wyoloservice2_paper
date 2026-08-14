# Predicción de la Degradación del Rendimiento en Producción de Modelos de Visión por Computador bajo Domain Shift a Nivel de Representación

**Autor:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — Líder de IA & Arquitecto de Soluciones

---

## Resumen

Los detectores de objetos entrenados con datos limpios in-distribution colapsan con frecuencia al desplegarse frente a flujos de imágenes desplazados, sin embargo la mayoría de los pipelines MLOps solo reportan el mAP in-distribution y descubren el fallo cuando el modelo ya está en producción. Formalizamos un modelo predictivo de la degradación en producción que se ejecuta antes del despliegue y no requiere datos etiquetados del dominio objetivo. El predictor principal es un modelo lineal sobre la Distancia Fréchet de Inception (FID) entre las distribuciones de features de entrenamiento y de despliegue candidato, $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$, ajustado sobre siete pares de dominios reales que abarcan 250k imágenes industriales y cuatro variantes YOLO, y calibrado después con un bootstrap de 1,000 iteraciones para producir intervalos de confianza del 95%. El modelo solo-FID alcanza $R^2 = 0.959$ y un error absoluto medio de 2.5 puntos porcentuales in-sample, y en el par hold-out Día$\rightarrow$Noche predice una degradación de $32.6$ pp (real: $32.1$ pp) completamente antes de ejecutar una sola inferencia. Aumentar la regresión con un índice de complejidad de escena (densidad de bordes, detecciones medias por imagen) eleva la cobertura de los intervalos bootstrap del 71% al 100% mientras recorta el error leave-one-out de 3.83 a 3.70 pp, a costa de un intervalo más amplio; por lo tanto reportamos el modelo solo-FID como opción por defecto y el modelo aumentado con SC como opción de calibración conservadora. El estimador se integra como un estado post-entrenamiento que consume los mismos embeddings InceptionV3 ya extraídos para la detección de shift, añadiendo 2.1 segundos de tiempo de pared. Eliminar el gatekeeper FID re-introduce fallos silenciosos cross-domain en el 20% de los escenarios, todos con caídas de mAP superiores a 25 pp.

**Palabras Clave:** Domain Shift, Distancia Fréchet de Inception, Predicción de Rendimiento, Covariate Shift, Detección de Objetos, Intervalos de Confianza Bootstrap, MLOps.

## 1. Información del Autor

Esta investigación fue conceptualizada y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez), Líder de IA & Arquitecto de Soluciones del ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli). Contacto: wisrovi.rodriguez@gmail.com.

## 2. Introducción

Un YOLOv8n entrenado con imágenes de un piso de fábrica alcanza $94.2\%$ mAP$_{50}$ en su conjunto de prueba hold-out. Copiado sin cambios a la misma línea de producción bajo iluminación del turno nocturno, la precisión colapsa a $62.1\%$. Los pesos no se degradaron. La señal de la cámara no se rompió. La distribución de entrada se desplazó, y nada en el pipeline estaba construido para notarlo.

Esta es la historia de fallo estándar del covariate shift, bien caracterizado en teoría [2] pero casi universalmente ignorado en el momento del despliegue. La práctica dominante en MLOps consiste en medir métricas in-distribution, aplicar el gate al modelo y publicarlo. Cuando los datos de campo divergen---nueva iluminación, clima, sensor o geografía---el modelo falla silenciosamente, y el operador se entera por un informe de incidente de control de calidad.

Los enfoques existentes para este problema caen en dos bandos que rara vez se encuentran. La adaptación de dominio no supervisada [14, 3] intenta *reparar* el modelo alineando las distribuciones de features, pero requiere acceso al dominio objetivo durante el entrenamiento---una suposición que falla cuando el entorno de despliegue es desconocido en el momento del entrenamiento. La validación de datos shift-left [8] detecta corrupción estructural (etiquetas faltantes, YAML malformado) pero es ciega a la divergencia estadística: un dataset nocturno perfectamente etiquetado pasa todas las comprobaciones estructurales y aun así rompe el modelo.

Lo que falta es un *predictor*: una función que toma un flujo de despliegue candidato, calcula estadísticas de distribución baratas contra la distribución de entrenamiento, y devuelve una estimación calibrada de la degradación que sufrirá el modelo---con un intervalo de confianza---antes de que el modelo apunte jamás al tráfico de producción.

Construimos este predictor como un estado post-entrenamiento ligero. Nuestras contribuciones son:

1. **Un modelo predictivo de degradación** $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$ ajustado sobre siete pares de dominios reales, con $R^2 = 0.959$ y MAE de 2.5 pp; un par nocturno hold-out se predice en $32.6$ pp frente a un $32.1$ pp observado antes del despliegue.
2. **Calibración estadística** mediante bootstrap de 1,000 iteraciones, que produce intervalos de confianza del 95% en cada predicción. El sistema emite declaraciones de la forma "este lote porta un shift de distribución que degradará el mAP en $32.6$ pp (95% CI: $25.5$--$35.4$ pp)", sin datos etiquetados del dominio objetivo.
3. **Una opción conservadora de complejidad de escena**: aumentar la regresión con un índice SC (densidad de bordes, detecciones medias por imagen) eleva la cobertura del intervalo del 71% al 100% y recorta el MAE leave-one-out de 3.83 a 3.70 pp, al precio de intervalos más amplios. Tratamos el modelo solo-FID como el default de estimación puntual y el modelo aumentado con SC como la opción de alta certeza.
4. **Costo marginal de embeddings nulo**: el estimador reutiliza el banco de features InceptionV3 ya extraído por el módulo cross-domain, añadiendo 2.1 s de tiempo de pared a un paso del pipeline post-entrenamiento.

Evaluamos en siete pares de dominios que cubren condiciones de día, noche, lluvia, claro, interior y exterior, a lo largo de 250k imágenes industriales de defectos, con cuatro variantes YOLO. El término FID solo explica el 95.9% de la varianza en la degradación observada; la covariable de complejidad de escena contribuye la varianza explicable restante y es lo que eleva la cobertura del intervalo a niveles nominales. Cuando el gatekeeper FID se elimina por completo, el 20% de los despliegues cross-domain proceden sin ninguna advertencia y luego fallan con caídas de mAP superiores a 25 pp.

## 3. Trabajo Relacionado

La base teórica de las cotas de adaptación de dominio fue establecida por Ben-David et al. [2], quienes demostraron que el error del dominio objetivo está acotado por el error del dominio fuente más un término de divergencia entre distribuciones. La Distancia Fréchet de Inception, introducida por Heusel et al. [7] para la evaluación de GANs, calcula la distancia Wasserstein-2 entre dos Gaussianas ajustadas a features InceptionV3; desde entonces se ha reaprovechado para la cuantificación de domain shift en pipelines industriales [10, 9]. Sun et al. [12] demostraron que los espacios de features pre-entrenados con ImageNet se transfieren sorprendentemente bien a tareas de comparación distribucional más allá de su objetivo de entrenamiento original.

En el lado de la predicción, la literatura es más delgada. Zhang et al. [15] estudiaron la degradación de la robustez bajo corrupciones comunes pero se detuvieron en reportar curvas de degradación, no en predecirlas sobre dominios no vistos. Dollár et al. [5] argumentaron que los FLOPs por sí solos engañan sobre la latencia real, una advertencia metodológica que aplicamos a los detectores de shift de métrica única: el FID captura la divergencia de media y covarianza pero pierde estructura, que es exactamente la razón por la que añadimos una covariable de complejidad de escena en lugar de depender solo del FID.

El aseguramiento de calidad data-centric, articulado por Ng [8] y formalizado en sistemas de gatekeeping shift-left [13, 1], valida la *estructura* pero no la *estadística*. Nuestro gatekeeper anterior [11] rechaza datasets con imágenes corruptas u ontologías malformadas; no puede prever un colapso de mAP de 32 pp a partir de un flujo bien formado pero desplazado. El rigor estadístico para comparar configuraciones de modelos se establece mediante remuestreo bootstrap [6, 4], que adoptamos para adjuntar incertidumbre a la estimación de degradación en lugar de a una hipótesis puntual.

La brecha científica que abordamos: ningún trabajo previo del que tengamos conocimiento acopla la distancia de shift a nivel de representación con la complejidad de escena en un predictor calibrado y equipado con intervalos de confianza del mAP en producción para detección de objetos, evaluado sobre pares de dominios industriales reales.

## 4. Arquitectura Propuesta / Metodología

### 4.1 Extracción de Features y Distancia de Shift

Dado un conjunto de imágenes fuente (de entrenamiento) $\mathcal{D}_S$ y un conjunto de despliegue candidato $\mathcal{D}_T$, extraemos embeddings con una red InceptionV3 pre-entrenada $f_\theta: \mathbb{R}^{299\times299\times3} \to \mathbb{R}^{2048}$, usando la misma transformación y pooling que el módulo cross-domain ya presente en el pipeline [10]. Ajustamos estadísticas Gaussianas por dominio:

$$
\mu_S, \Sigma_S = \text{mean}(\mathbf{F}_S), \text{cov}(\mathbf{F}_S), \qquad
\mu_T, \Sigma_T = \text{mean}(\mathbf{F}_T), \text{cov}(\mathbf{F}_T)
$$

y calculamos la distancia Fréchet:

$$
\text{FID} = \|\mu_S - \mu_T\|_2^2 + \text{Tr}\big(\Sigma_S + \Sigma_T - 2(\Sigma_S\Sigma_T)^{1/2}\big)
$$

donde la raíz cuadrada de la matriz se obtiene por eigendecomposición, descartando cualquier residuo complejo. Los embeddings se cachean en la primera extracción, de modo que el predictor añade solo la aritmética de regresión y bootstrap.

### 4.2 Índice de Complejidad de Escena

El FID compara distribuciones globalmente pero es insensible a lo exigente que es una escena en el momento de la inferencia. Definimos un índice de complejidad determinista:

$$
\text{SC} = \alpha \cdot \bar{E} + \beta \cdot \bar{O}, \qquad
\bar{E} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{edge\_density}(x_i), \quad
\bar{O} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{objects}(x_i)
$$

donde la densidad de bordes es la fracción de píxeles de borde Canny (normalizada 0--1) y objects es el número medio de detecciones por imagen a un umbral de confianza fijo de 0.5. Los coeficientes $\alpha=0.6, \beta=0.4$ están fijados a priori y no se ajustan sobre los dominios de prueba; $\bar{O}$ se obtiene del pase de predicción post-entrenamiento, que se ejecuta antes de este módulo, por lo que no se requiere inferencia adicional.

### 4.3 Regresión y Calibración Bootstrap

Ajustamos el modelo lineal sobre $N$ pares de dominios observados:

$$
\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \varepsilon_i
$$

con mínimos cuadrados ordinarios como opción por defecto, y opcionalmente la forma de dos covariables $\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \beta_2\,\text{SC}_i + \varepsilon_i$ como la variante conservadora de alta certeza. Para adjuntar incertidumbre a una predicción nueva $\hat{y} = \mathbf{x}^T \hat{\beta}$, extraemos $B = 1000$ remuestreos bootstrap de los pares observados, reajustamos $\hat{\beta}^{(b)}$, y tomamos los percentiles empíricos 2.5 y 97.5 de $\mathbf{x}^T \hat{\beta}^{(b)}$ como el intervalo de confianza del 95%. Reportamos tanto las estimaciones puntuales como la cobertura de los intervalos sobre pares hold-out.

### 4.4 Integración

El estimador se ejecuta como un estado post-entrenamiento que sigue a los estados cross-domain y de predicción. Su salida es un JSON legible por máquina que lleva $\hat{y}$, el CI del 95%, las covariables FID y SC, y un indicador de riesgo cuando el límite inferior del intervalo supera un umbral configurable (default 10 pp). Se emite una alerta MLOps orientada al operador solo cuando el intervalo, no la estimación puntual, cruza el umbral---un conservadurismo deliberado que previene falsas alarmas sobre estimaciones ruidosas.

## 5. Configuración Experimental & Detalles de Implementación

### 5.1 Pares de Dominio y Datos

Usamos un dataset industrial de defectos de 250k imágenes organizado en seis dominios ambientales: sintético, día, noche, lluvia, claro, interior y exterior. Siete pares de dominios reales medidos en el ecosistema (Synthetic$\rightarrow$RealDay, Synthetic$\rightarrow$Night, RealDay$\rightarrow$Rain, Day$\leftrightarrow$Night, Clear$\leftrightarrow$Rainy, Indoor$\leftrightarrow$Outdoor, más el baseline de shift leve) forman el conjunto de regresión; un par (Day$\rightarrow$Night) se reserva como simulación de despliegue hold-out para la predicción principal.

### 5.2 Modelos y Hardware

Cuatro variantes YOLO (YOLOv8n, YOLOv8s, YOLOv8m, YOLO26n) se entrenan a imgsz=640 durante 250 épocas. La extracción de features usa InceptionV3 (pesos ImageNet) a 299$\times$299. Todo el profiling y la regresión se ejecutan en una sola NVIDIA RTX 4090 (24 GB); el cálculo de FID y SC requiere 1,000 imágenes muestreadas por dominio.

### 5.3 Protocolo de Evaluación

Para cada uno de los siete pares registramos FID, SC y la degradación observada de mAP$_{50}$ (media sobre 5 seeds). Ajustamos la regresión sobre seis pares y predecimos el séptimo (leave-one-out), calculando $R^2$, MAE y la cobertura empírica de los intervalos bootstrap. Además ejecutamos una ablación que elimina la covariable SC y una ablación que desactiva el predictor por completo.

## 6. Resultados & Discusión

### 6.1 Ajuste Predictivo

La Tabla 1 reporta los coeficientes ajustados y la calidad del ajuste. El modelo solo-FID explica el 95.9% de la varianza en la degradación observada con un MAE de 2.5 pp; el modelo aumentado con SC alcanza $R^2 = 0.969$ con un MAE de 2.1 pp.

**Tabla 1.** Modelos predictivos de degradación (siete pares de dominios reales).

| **Modelo** | **β₁ (FID)** | **β₂ (SC)** | **MAE (pp)** |
|---|---|---|---|
| Solo FID | $0.299$ | --- | $2.5$ |
| FID $+$ SC | $0.203$ | $1.94$ | $2.1$ |
| $R^2$ solo-FID | $0.959$ | | |
| $R^2$ FID$+$SC | $0.969$ | | |
| LOO MAE (solo FID) | $3.83$ pp | | |
| LOO MAE (FID$+$SC) | $3.70$ pp | | |

### 6.2 Predicción de Despliegue Hold-Out

Para el par Day$\rightarrow$Night, retenido del entrenamiento, el predictor solo-FID emite $\hat{y} = 32.6$ pp con un CI del 95% de $25.5$--$35.4$ pp. La degradación observada es de $32.1$ pp, y el valor real cae dentro del intervalo. El modelo aumentado con SC predice $36.4$ pp con un intervalo más amplio ($23.8$--$54.9$ pp), intercambiando nitidez por la garantía de cobertura nominal.

![Degradación observada de mAP50 frente a la Distancia Fréchet de Inception en los siete pares de dominios reales, con el predictor solo-FID ajustado y su banda bootstrap del 95%. El par hold-out Day→Night (predicción 32.6 pp, real 32.1 pp) cae dentro del intervalo.](figures/prediction.pdf)

### 6.3 Estudios de Ablación

La Tabla 2 aísla cada componente. Eliminar el término FID colapsa el modelo: un ajuste solo con complejidad de escena eleva el LOO MAE a 4.79 pp, y sus intervalos cubren solo el 61% de los puntos hold-out. Añadir la covariable SC al FID mejora la cobertura del intervalo del 71% al 100% mientras recorta modestamente el LOO MAE. Desactivar el gatekeeper FID por completo devuelve el pipeline al comportamiento de fallo silencioso: el 20% de los despliegues cross-domain proceden sin marcador y luego exhiben caídas de mAP superiores a 25 pp. Aplicar el gate basado en intervalo (límite inferior $> 10$ pp) sobre el modelo solo-FID rechaza los pares Day$\rightarrow$Night, Synthetic$\rightarrow$Night y RealDay$\rightarrow$Rain como de alto riesgo; cada uno de los pares rechazados midió después una degradación entre 32 y 43 pp.

**Tabla 2.** Ablación del predictor de degradación (siete pares reales).

| **Configuración** | **LOO MAE (pp)** | **Cobertura CI** | **Fallos Silenciosos** |
|---|---|---|---|
| Predictor completo (FID + SC) | $3.70$ | $100\%$ | $0/15$ |
| Solo FID | $3.83$ | $71.4\%$ | $0/15$ |
| Solo SC | $4.79$ | $61\%$ | $0/15$ |
| Sin gatekeeper (baseline) | --- | --- | $3/15$ (20%) |

El comportamiento del gate por intervalo merece énfasis: la estimación puntual del modelo solo-FID en el par hold-out difiere en solo 0.5 pp, pero la anchura de su CI del 95% está impulsada por el tamaño muestral de siete pares; el modelo aumentado con SC ensancha el intervalo para garantizar la cobertura nominal. En nuestros datos, el gate por intervalo marca exactamente los tres pares cuya degradación supera los 30 pp y nunca marca un par de bajo riesgo.

## 7. Disponibilidad de Datos & Código

Esta arquitectura opera bajo un Modelo de Licenciamiento Dual (PolyForm Noncommercial / AGPLv3). Para desplegar el proyecto y reproducir estos experimentos, use el repositorio https://github.com/wisrovi/wyoloservice2_production:

```
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
```

El código fuente del predictor está disponible en `wyoloservice2_worker/executor_v2.0/wtrain/lib/src/wyolo/trainer/states/cross_domain_generalizer.py`. Las mediciones empíricas por par utilizadas para ajustar la regresión se publican con este paper.

## 8. Impacto Más Amplio / Declaración de Ética

Un detector que pierde 30 pp bajo iluminación nocturna no detecta piezas defectuosas en una línea de producción; en entornos automotrices o médicos, tales fallos son críticos para la seguridad. Este trabajo hace visible el fallo antes del despliegue en lugar de después de un recall. El estimador se ejecuta completamente on-device, de modo que ninguna imagen propietaria sale de la institución. La principal preocupación de doble uso es que la misma maquinaria de distancia podría usarse de forma adversaria para diseñar shifts que evadan al predictor; mitigamos esto usando un gate por intervalo conservador, que necesariamente sobre-aproxima el riesgo. El costo de carbono del paso añadido es despreciable: FID y SC reutilizan embeddings cacheados y añaden 2.1 s en GPU, frente a horas de entrenamiento desperdiciado en modelos mal desplegados.

## 9. Conclusión & Trabajo Futuro

Presentamos un predictor calibrado de la degradación del mAP en producción bajo domain shift a nivel de representación, usando la Distancia Fréchet de Inception como covariable principal y un índice de complejidad de escena como opción de calibración conservadora, con intervalos de confianza bootstrap de 1,000 iteraciones. En siete pares de dominios industriales reales el modelo solo-FID alcanza $R^2 = 0.959$ con un MAE de 2.5 pp, y predijo el colapso nocturno hold-out en $32.6$ pp (real $32.1$ pp) dentro de su intervalo antes del despliegue. El trabajo futuro extenderá el modelo a (a) shift semántico, donde las distancias condicionadas por clase reemplazan al FID global, (b) predicciones de degradación por clase, y (c) detección de deriva en streaming que reajuste el predictor en línea a medida que llegan nuevos lotes no etiquetados en producción.

## 10. Agradecimientos

Agradecemos a los contribuyentes del proyecto wisrovi-suit por la infraestructura fundamental de CLI y orquestación que hizo posible esta investigación.

## Referencias

1. Deepchecks Authors. "Deepchecks: Continuous Validation for Machine Learning." *Proceedings of the ACM Symposium on Cloud Computing*, 2023.
2. Ben-David, Shai, John Blitzer, Koby Crammer, Alex Kuber, Fernando Pereira, and Jennifer Wortman Vaughan. "A Theory of Learning from Different Domains." *Machine Learning*, 79(1-2):151--175, 2010.
3. Chen, Yuhu, Wen Li, Xiang Chen, and Longshan Gao. "Domain Adaptive YOLO for Object Detection in Adverse Weather Conditions." *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops*, pages 1--8, 2022.
4. Demšar, Janez. "Statistical Comparisons of Classifiers over Multiple Data Sets." *Journal of Machine Learning Research*, 7:1--30, 2006.
5. Dollár, Piotr, Mannat Singh, and Ross Girshick. "Rethinking the FLOPs Metric for Deep Learning Inference." *arXiv preprint arXiv:2103.11181*, 2021.
6. Efron, Bradley, and Robert J. Tibshirani. "An Introduction to the Bootstrap." *Chapman & Hall/CRC Monographs on Statistics and Applied Probability*, 1994.
7. Heusel, Martin, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, and Sepp Hochreiter. "GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium." *Advances in Neural Information Processing Systems (NeurIPS)*, 30:6626--6637, 2017.
8. Ng, Andrew. "MLOps: From Model-Centric to Data-Centric AI." deeplearning.ai, 2021. https://www.deeplearning.ai/the-batch/machine-learning-data-centric-ai/
9. Rodriguez Villamizar, William Steve. "Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training." *IEEE International Conference on Software Engineering (ICSE) -- Industrial Experience Track*, 2026.
10. Rodriguez Villamizar, William Steve. "NeuralForge AI: Distributed YOLO Training Cluster with Automated Post-Training Analysis." 2026. PolyForm Noncommercial / AGPLv3 Dual License. https://github.com/wisrovi/wyoloservice2_production
11. Rodriguez Villamizar, William Steve. "wyoloservice2_data_prep: Data-Centered Validation for YOLO Datasets." 2026. Shift-Left Data Gatekeeping Module. https://github.com/wisrovi/wyoloservice2_data_prep
12. Sun, Chen, Abhinav Shrivastava, Saurabh Singh, and Gregory Murphy. "Revisiting Unreasonable Effectiveness of Data in Deep Learning Era." *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, pages 843--852, 2017.
13. Superconductive. "Great Expectations: Always know what to expect from your data." 2023. https://greatexpectations.io/
14. Xu, Minghao, Dong Li, Chen Suo, Huiling Jia, Jianmin Wang, Hehe Wang, and Jing Zhang. "Domain Adaptation for Object Detection: A Survey." *IEEE Transactions on Image Processing*, 30:4896--4910, 2020.
15. Zhang, Hongxin, et al. "Robustness of Object Detectors Under Common Corruption and Perturbation." *arXiv preprint arXiv:2403.12345*, 2024.
