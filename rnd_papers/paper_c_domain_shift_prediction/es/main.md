# Predicción de la Degradación del Rendimiento en Producción de Modelos de Visión por Computador bajo Desplazamiento de Dominio a Nivel de Representación

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — Líder de IA & Arquitecto de Soluciones

---

## Resumen & Palabras Clave
**Resumen:** Los detectores de objetos entrenados con datos limpios dentro de la distribución (in-distribution) frecuentemente colapsan cuando se despliegan frente a flujos de imágenes desplazados; sin embargo, la mayoría de los pipelines de MLOps solo reportan el mAP in-distribution y descubren el fallo una vez que el modelo ya está en producción. Formalizamos un modelo predictivo de la degradación downstream que se ejecuta antes del despliegue y no requiere datos etiquetados del dominio objetivo. El predictor principal es un modelo lineal sobre la Distancia Fr\'echet de Inception (FID) entre las distribuciones de características de entrenamiento y del despliegue candidato, $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$, ajustado sobre siete pares de dominios reales que abarcan 250k imágenes industriales y cuatro variantes de YOLO, y luego calibrado con un bootstrap de 1,000 iteraciones para producir intervalos de confianza del 95%. El modelo que solo utiliza FID alcanza $R^2 = 0.988$ y un error absoluto medio de 1.05 puntos porcentuales (pp) in-sample, y en el par reservado (held-out) Día$\rightarrow$Noche predice una degradación de $32.9$ pp (real: $30.4$ pp) completamente antes de ejecutar una sola inferencia. Aumentar la regresión con un índice de complejidad de escena (SC) (densidad de bordes, promedio de detecciones por imagen) eleva la cobertura de los intervalos bootstrap del 57.1% al 100% mientras reduce el error de validación cruzada dejando uno fuera (leave-one-out, LOO) de 1.45 a 1.17 pp; por lo tanto, reportamos el modelo solo-FID como el predeterminado y el modelo aumentado con SC como la opción de calibración conservadora. El estimador se integra como un estado post-entrenamiento que consume los mismos embeddings de InceptionV3 ya extraídos para la detección de desplazamiento, agregando 2.1 segundos de tiempo de ejecución real (wall-clock time). Eliminar el gatekeeper de FID reintroduce fallos silenciosos entre dominios (cross-domain) en los 15 escenarios (100% de tasa de fallos silenciosos), todos con caídas de mAP superiores a 25 pp.

**Palabras Clave:** Desplazamiento de Dominio, Distancia Fr\'echet de Inception, Predicción del Rendimiento, Covariate Shift, Detección de Objetos, Intervalos de Confianza Bootstrap, MLOps.

## 1. Información del Autor
Esta investigación fue conceptualizada y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez), Líder de IA & Arquitecto de Soluciones para el ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli). Contacto: wisrovi.rodriguez@gmail.com.

## 2. Introducción
Un YOLOv8n entrenado con imágenes de la planta de producción alcanza un $94.2%$ de mAP$_{50}$ en su conjunto de prueba reservado. Copiado sin cambios en la misma línea de producción bajo la iluminación del turno de noche, la precisión colapsa al $63.8%$. Los pesos no se degradaron. El flujo de la cámara no falló. La distribución de entrada se desplazó, y nada en el pipeline estaba diseñado para detectarlo.

Este es el caso clásico de fallo por covariate shift, bien caracterizado en teoría~[1] pero ignorado casi universalmente en el momento del despliegue. La práctica dominante en MLOps consiste en medir métricas dentro de la distribución (in-distribution), validar el modelo y desplegarlo. Cuando los datos de campo divergen (nueva iluminación, clima, sensor o ubicación geográfica), el modelo falla silenciosamente y el operador se entera a través de un informe de incidentes de control de calidad.

Los enfoques existentes para este problema se dividen en dos grupos que rara vez coinciden. La adaptación de dominio no supervisada~[18, 2] intenta \emph{reparar} el modelo alineando las distribuciones de características, pero requiere acceso al dominio objetivo durante el entrenamiento, una suposición que no se cumple cuando el entorno de despliegue se desconoce durante la fase de entrenamiento. La validación de datos shift-left~[11] detecta la corrupción estructural (etiquetas faltantes, YAML malformados) pero no detecta la divergencia estadística: un conjunto de datos de noche perfectamente etiquetado supera todas las comprobaciones estructurales y, aun así, rompe el modelo.

Lo que falta es un \emph{predictor}: una función que reciba una secuencia de despliegue candidato, calcule estadísticas de distribución de bajo costo computacional en relación con la distribución de entrenamiento y devuelva una estimación calibrada de la degradación que sufrirá el modelo, junto con un intervalo de confianza, antes de que este se exponga al tráfico de producción.

Construimos este predictor como un estado ligero posterior al entrenamiento. Nuestras contribuciones son:

    1. **Un modelo predictivo de degradación** $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$ ajustado sobre siete pares de dominios reales, con $R^2 = 0.988$ y un MAE de 1.05 pp; un par nocturno reservado se predice con una degradación de $32.9$ pp en comparación con la observada de $30.4$ pp antes del despliegue.
    1. **Calibración estadística** mediante un bootstrap de 1,000 iteraciones, lo que genera intervalos de confianza del 95% para cada predicción. El sistema emite declaraciones del tipo ``este lote presenta un desplazamiento de distribución que degradará el mAP en $32.9$ pp (IC del 95%: $31.5$--$34.2$ pp)'', sin necesidad de datos etiquetados del dominio objetivo.
    1. **Una opción de complejidad de escena conservadora**: aumentar la regresión con un índice de complejidad de escena (SC) (densidad de bordes, detecciones promedio por imagen) eleva la cobertura de los intervalos del 57.1% al 100% y reduce el MAE de validación cruzada dejando uno fuera (LOO) de 1.45 a 1.17 pp. Consideramos el modelo solo-FID como el valor predeterminado para estimación puntual y el modelo aumentado con SC como la opción de alta certeza.
    1. **Costo marginal de extracción nulo**: el estimador reutiliza el banco de características de InceptionV3 ya extraído por el módulo cross-domain, agregando solo 2.1 s de tiempo de ejecución real a un paso del pipeline posterior al entrenamiento.

Evaluamos sobre siete pares de dominios que abarcan condiciones de día, noche, lluvia, despejado, interiores y exteriores en 250k imágenes de defectos industriales con cuatro variantes de YOLO. El término FID por sí solo explica el 98.8% de la varianza en la degradación observada; la covariable de complejidad de la escena aporta la varianza explicable restante y es la que eleva la cobertura de los intervalos a los niveles nominales. Cuando el gatekeeper de FID se elimina por completo, los 15 escenarios (100% de tasa de fallos silenciosos) continúan sin advertencia alguna y fallan posteriormente con caídas de mAP superiores a 25 pp.

## 3. Trabajo Relacionado
La base teórica de los límites de adaptación de dominio fue establecida por Ben-David et al.~[1], quienes demostraron que el error en el dominio objetivo está acotado por el error en el dominio de origen más un término de divergencia entre las distribuciones. La Distancia Fr\'echet de Inception, introducida por Heusel et al.~[9] para la evaluación de GANs, calcula la distancia Wasserstein-2 entre dos Gaussianas ajustadas a las características de InceptionV3; desde entonces, se ha adaptado para la cuantificación del desplazamiento de dominio en pipelines industriales~[14, 13]. Sun et al.~[15] (con listados de autores corregidos: Sun, Shrivastava, Singh y Gupta) demostraron que los espacios de características preentrenados con ImageNet se transfieren sorprendentemente bien a tareas de comparación distribucional más allá de su objetivo de entrenamiento original.

En el lado de la predicción, la estimación del rendimiento de modelos en dominios objetivo no etiquetados ha ganado impulso. Taori et al.~[17] y Recht et al.~[12] analizaron los comportamientos de correlación lineal (precisión en la línea, accuracy-on-the-line) de clasificadores bajo desplazamientos de distribución. Hendrycks y Dietterich~[8] estableció corrupciones de referencia para perfilar el colapso del modelo. Trabajos recientes como el de Garg et al.~[7] propusieron la Diferencia de Umbral Promedio (ATC, por sus siglas en inglés) para estimar la precisión en desplazamientos no etiquetados, mientras que Deng and Zheng~[deng2021classifier] estimaron la generalización de clasificadores visuales sin anotaciones objetivo etiquetadas. Sin embargo, estos métodos se evalúan principalmente en tareas de clasificación. En contraste, Dehghani et al.~[3] (The Efficiency Misnomer) ilustraron que las métricas proxy estáticas no reflejan el comportamiento a nivel de sistema bajo desplazamiento; aplicamos una advertencia similar a las métricas proxy en MLOps. Además, Doll\'ar et al.~[5] (Fast and Accurate Model Scaling) demostraron que el número de parámetros o los FLOPs por sí solos son predictores insuficientes de la eficiencia de ejecución; dado que las distancias globales como la FID no pueden resolver la disposición espacial o los desplazamientos de complejidad, introducimos una covariable de complejidad de la escena para calibrar el predictor.

El aseguramiento de la calidad orientado a los datos, formulado por Ng~[11] y formalizado en sistemas de control (gatekeeping) shift-left~[16], valida la \emph{estructura} pero no la \emph{estadística}. Nuestro gatekeeper anterior rechaza conjuntos de datos con imágenes corruptas u ontologías malformadas; no puede prever un colapso de mAP de 30 pp proveniente de un flujo bien estructurado pero estadísticamente desplazado. El rigor estadístico para comparar configuraciones de modelos se establece mediante el remuestreo bootstrap~[6, 4], que adoptamos para asociar incertidumbre a la estimación de degradación en lugar de a una hipótesis puntual.

La brecha científica que abordamos: según nuestro conocimiento, ningún pipeline industrial combina la distancia de desplazamiento a nivel de representación con la complejidad de la escena para predecir la degradación del mAP downstream bajo desplazamiento de dominio, proporcionando intervalos de confianza calibrados para la detección de objetos antes del despliegue.

## 4. Arquitectura Propuesta / Metodología
El flujo de ejecución del predictor de degradación se estructura como un pipeline de procesamiento lineal:

![Diagrama de flujo del pipeline predictivo para la estimación del rendimiento downstream.](figures/prediction.pdf)

Todas las operaciones se ejecutan después del entrenamiento en los flujos objetivo candidatos antes de la aprobación de salida del modelo. Para facilitar la trazabilidad y la reproducibilidad, los siete pares de dominios reales evaluados en este trabajo están mapeados con sus estadísticas de distancia empírica en el archivo `domain\_pairs.npz` publicado: Par 0 (línea base de desplazamiento leve, $\text{FID}=18.3$), Par 1 (Sintético$\rightarrow$DíaReal, $\text{FID}=43.8$), Par 2 (DíaReal$\rightarrow$Lluvia, $\text{FID}=72.3$), Par 3 (Despejado$\leftrightarrow$Lluvioso, $\text{FID}=90.74$), Par 4 (Día$\rightarrow$Noche, $\text{FID}=127.6$), Par 5 (Sintético$\rightarrow$Noche, $\text{FID}=142.93$), y Par 6 (Interior$\leftrightarrow$Exterior, $\text{FID}=149.86$).

### 10.1 Extracción de Características y Distancia de Desplazamiento
Dado un conjunto de imágenes de origen (entrenamiento) $\mathcal{D}_S$ y un conjunto de despliegue candidato $\mathcal{D}_T$, extraemos embeddings con una red InceptionV3 preentrenada $f_\theta: \mathbb{R}^{299\times299\times3} \to \mathbb{R}^{2048}$, utilizando la misma transformación y agrupación (pooling) del módulo de dominio cruzado (cross-domain) que ya se encuentra presente en el pipeline~[14]. Ajustamos estadísticas Gaussianas para cada dominio:

$$

    \mu_S, \Sigma_S = \text{mean}(\mathbf{F}_S), \text{cov}(\mathbf{F}_S), \qquad
    \mu_T, \Sigma_T = \text{mean}(\mathbf{F}_T), \text{cov}(\mathbf{F}_T)

$$

y calculamos la distancia de Fr\'echet:

$$

    \text{FID} = \|\mu_S - \mu_T\|_2^2 + \text{Tr}\big(\Sigma_S + \Sigma_T - 2(\Sigma_S\Sigma_T)^{1/2}\big)

$$

onde la raíz cuadrada de la matriz se obtiene mediante descomposición en autovalores, descartando cualquier residuo complejo. Los embeddings se almacenan en caché en la primera extracción, por lo que el predictor solo añade la regresión y el cálculo de bootstrap.

### 10.2 Índice de Complejidad de la Escena
FID compara las distribuciones a nivel global, pero no es sensible a qué tan exigente es una escena en el momento de la inferencia. Definimos un índice de complejidad determinista:

$$

    \text{SC} = \alpha \cdot \bar{E} + \beta \cdot \bar{O}, \qquad
    \bar{E} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{edge\_density}(x_i), \quad
    \bar{O} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{objects}(x_i)

$$

donde la densidad de bordes es la fracción de píxeles de borde Canny (normalizada de 0 a 1) y objects es el promedio de detecciones por imagen. Para evitar fugas metodológicas (dado que $\bar{O}$ depende del propio modelo detector), evaluamos $\bar{O}$ utilizando un modelo base YOLOv8n desacoplado y fijo en lugar del modelo específico bajo prueba, asegurando que la métrica de complejidad de la escena siga siendo una propiedad independiente del dominio de destino. Los coeficientes $\alpha=0.6, \beta=0.4$ se definen a priori.

### 10.3 Regresión y Calibración Bootstrap
Ajustamos el modelo lineal en $N$ pares de dominios observados:

$$

    \Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \varepsilon_i

$$

empleando mínimos cuadrados ordinarios (OLS) por defecto, y opcionalmente la forma con dos covariables $\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \beta_2\,\text{SC}_i + \varepsilon_i$ como la variante conservadora de alta certeza. Para evaluar la significancia de la covariable SC, calculamos el p-valor de $\beta_2$ bajo los supuestos de OLS, asegurando que la complejidad de la escena añada una explicación estadísticamente válida ($p < 0.05$).

Para asociar incertidumbre a una nueva predicción $\hat{y} = \mathbf{x}^T \hat{\beta}$, realizamos $B = 1000$ remuestreos bootstrap de los pares observados, reajustamos $\hat{\beta}^{(b)}$ y tomamos los percentiles empíricos 2.5 y 97.5 de $\mathbf{x}^T \hat{\beta}^{(b)}$ como el intervalo de confianza del 95%. Reportamos tanto las estimaciones puntuales como la cobertura de los intervalos en los pares reservados.

### 10.4 Integración
El estimador se ejecuta como un estado posterior al entrenamiento después de los estados cross-domain y de predicción. Su salida es un archivo JSON legible por máquina que contiene $\hat{y}$, el intervalo de confianza del 95%, las covariables de FID y SC, y una bandera de riesgo cuando el límite inferior del intervalo supera un umbral configurable (predeterminado en 10 pp). Se emite una alerta de MLOps dirigida al operador únicamente cuando el intervalo de confianza, y no la estimación puntual, cruza dicho umbral; un conservadurismo deliberado que evita falsas alarmas ante estimaciones con ruido.

## 5. Configuración Experimental & Detalles de Implementación

### 10.5 Pares de Dominios y Datos
Utilizamos un conjunto de datos industriales de defectos con 250k imágenes, organizado en seis dominios ambientales: sintético, día, noche, lluvia, despejado, interiores y exteriores. Siete pares de dominios reales medidos en el ecosistema forman el conjunto de regresión; un par (Día$\rightarrow$Noche) se reserva como una simulación de despliegue held-out para la predicción principal. Para evaluar los límites estadísticos bajo tamaños de muestra mayores, formulamos una simulación in-silico de Monte Carlo que genera $M=20$ pares de dominios sintéticos muestreados a partir de las distribuciones empíricas. El conjunto de evaluación total para el estudio de ablación consta de 15 escenarios (5 semillas aleatorias $\times$ los 3 pares de dominios severos con degradación $> 30$ pp: Par 4 Día$\rightarrow$Noche, Par 5 Sintético$\rightarrow$Noche y Par 6 Interior$\leftrightarrow$Exterior).

### 10.6 Modelos y Hardware
Cuatro variantes de YOLO (YOLOv8n, YOLOv8s, YOLOv8m y YOLO26n, basadas en la arquitectura YOLOv8~[10], donde YOLO26n representa una variante YOLO personalizada de 26 capas optimizada en el cuello del modelo y diseñada para cómputo ligero en el borde industrial) se entrenan con un tamaño de imagen de 640 durante 250 épocas. La extracción de características utiliza InceptionV3 (pesos de ImageNet) en un tamaño de 299$\times$299. Todas las pruebas de rendimiento (profiling) y regresión se ejecutan en una sola GPU NVIDIA RTX 4090 (24 GB); el cálculo de FID y SC requiere 1,000 imágenes de muestra por dominio. El profiling de tiempo de ejecución real de los 2.1 s de sobrecarga se mide mediante la función `time.perf\_counter()` de Python, promediada en 100 ejecuciones consecutivas.

### 10.7 Protocolo de Evaluación
Para cada uno de los pares de dominios registramos el FID, el SC y la degradación observada de mAP$_{50}$ (promedio sobre 5 semillas). Ajustamos la regresión en seis pares y predecimos el séptimo (leave-one-out), calculando $R^2$, el MAE y la cobertura empírica de los intervalos bootstrap. Adicionalmente, realizamos una ablación eliminando la covariable SC y otra desactivando el predictor por completo.

## 6. Resultados & Discusión

### 10.8 Ajuste Predictivo
La tab:regression detalla los coeficientes ajustados y la calidad del ajuste en los siete pares de dominios principales. El modelo solo-FID explica el 98.8% de la varianza en la degradación observada con un MAE de 1.05 pp; el modelo aumentado con SC alcanza un $R^2 = 0.995$ con un MAE de 0.62 pp. Bajo pruebas de hipótesis de OLS, el coeficiente de complejidad de la escena $\beta_2 = 2.475$ es marginalmente significativo ($t = 2.438, p = 0.0713$ con $df=4$) debido a una colinealidad severa ($\text{VIF} = 21.4$ para ambas covariables) en el pequeño conjunto de datos de 7 pares. En lugar de ser un factor principal, la complejidad de la escena sirve como una covariable de diagnóstico y regularización que ensancha los intervalos de bootstrap.

Para evaluar los límites estadísticos bajo tamaños de muestra mayores, ejecutamos una simulación in-silico de Monte Carlo que genera $M=20$ pares de dominios sintéticos muestreados a partir de las distribuciones empíricas. En este corpus simulado, la regresión se mantiene estable: el ajuste de solo-FID produce $R^2 = 0.983 \pm 0.007$ y un MAE de $0.97 \pm 0.17$ pp, mientras que el modelo aumentado con SC produce $R^2 = 0.995 \pm 0.002$ y un MAE de $0.59 \pm 0.11$ pp. Estos resultados confirman la robustez del marco predictivo lineal a través de diversos conjuntos de datos simulados.

**Table 1.** Modelos predictivos de degradación (siete pares de dominios reales).

| lccc@{}}

**Modelo** | $\beta_1$ (FID) | $\beta_2$ (SC) | **MAE (pp)** |
| --- | --- | --- | --- |
| Solo FID | $0.250$ | --- | $1.05$ |
| FID $+$ SC | $0.156$ | $2.475$ | $0.62$ |
| $R^2$ solo-FID | $0.988$ |
| $R^2$ FID$+$SC | $0.995$ |
| LOO MAE (solo FID) | $1.45$ pp |
| LOO MAE (FID$+$SC) | $1.17$ pp |

### 10.9 Predicción de Despliegue en Datos Reservados
Para el par Día$\rightarrow$Noche, excluido del entrenamiento, el predictor solo-FID calcula $\hat{y} = 32.9$ pp con un IC del 95% de $31.5$--$34.2$ pp. La degradación observada real es de $30.4$ pp. Aunque el valor real se encuentra ligeramente fuera del estrecho intervalo (lo que representa la cobertura empírica fuera de muestra del $57.1%$ del modelo bootstrap de solo-FID), el modelo aumentado con SC produce una estimación de $\hat{y} = 32.6$ pp con un intervalo más amplio de $30.0$--$33.5$ pp, conteniendo exitosamente el valor real y sacrificando precisión por una tasa de cobertura del $100%$ ($B = 1000$ remuestreos bootstrap, con una semilla determinista $= 42$ para el bootstrap de pares reservados para mantener la alineación exacta).

![Degradación observada de mAP$_{50](figures/prediction.pdf)

### 10.10 Estudios de Ablación
La tab:ablation aísla cada componente. Al eliminar el término de FID, el modelo colapsa: un ajuste que solo contempla la complejidad de la escena eleva el MAE de LOO a 1.92 pp, y sus intervalos solo cubren el 71.4% (IC de Wilson del 95%: $[35.9%, 91.8%]$) de los puntos reservados. Agregar la covariable SC al FID mejora la cobertura de los intervalos del 57.1% (IC de Wilson del 95%: $[25.0%, 84.2%]$) al 100% (IC de Wilson del 95%: $[64.6%, 100.0%]$) mientras reduce el MAE de LOO. Debido al pequeño tamaño de muestra $N=7$, estos intervalos de cobertura se superponen, lo que indica que la ganancia estadística en la cobertura a partir de SC no es matemáticamente distinguible a esta escala.

Desactivar el predictor por completo hace que el pipeline regrese a un comportamiento de fallos silenciosos (definido como cualquier despliegue que avanza sin advertencia ante un desplazamiento severo de $> 25$ pp). De los 15 escenarios de evaluación (3 pares de dominios severos a través de 5 semillas), la línea base sin gatekeeper falla en los 15 escenarios (100% de tasa de fallos silenciosos), mientras que las compuertas tanto del predictor solo-FID como del completo interceptan los 15 escenarios (0% de fallos silenciosos).

La aplicación de la compuerta basada en intervalos (límite inferior $> 10$ pp) en el modelo solo-FID señala exactamente los 5 pares cuya degradación real supera los 15 pp (RealDay$\rightarrow$Rain, Clear$\leftrightarrow$Rainy, Synthetic$\rightarrow$Night, Day$\rightarrow$Night e Indoor$\leftrightarrow$Outdoor) y nunca señala los 2 pares de bajo riesgo (la línea base de desplazamiento leve y Synthetic$\rightarrow$RealDay), aunque la degradación real de Synthetic$\rightarrow$RealDay es de $11.03$ pp (con un límite inferior conservador del IC LOO de $7.52$ pp, manteniéndolo de forma segura por debajo del umbral de riesgo de $10$ pp).

**Table 2.** Ablación del predictor de degradación (siete pares reales).

| lccc@{}}

**Configuración** | **LOO MAE (pp)** | **Cobertura de IC** | **Fallos Silenciosos** |
| --- | --- | --- | --- |
| Predictor completo (FID + SC) | $1.17$ | $100%$ | $0/15$ (0%) |
| Solo FID | $1.45$ | $57.1%$ | $0/15$ (0%) |
| Solo SC | $1.92$ | $71.4%$ | $0/15$ (0%) |
| Sin gatekeeper (línea base) | --- | --- | $15/15$ (100%) |

El comportamiento de la validación basada en intervalos merece especial énfasis: la estimación puntual del modelo de solo-FID en el par reservado difiere en solo 2.5 pp, pero el ancho de su IC del 95% está condicionado por el tamaño de muestra de siete pares; el modelo aumentado con SC ensancha el intervalo para asegurar una cobertura nominal. En nuestros datos, el gate por intervalo señala de manera precisa los pares de alto riesgo y nunca señala un par de bajo riesgo.

## 7. Disponibilidad de Datos & Código
Esta arquitectura opera bajo un Modelo de Licencia Dual (PolyForm Noncommercial / AGPLv3). Para desplegar el proyecto y reproducir estos experimentos, utilice el repositorio <https://github.com/wisrovi/wyoloservice2\_production>:

\begin{verbatim}
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
\end{verbatim}

El código fuente del predictor está disponible en `wyoloservice2\_worker/executor\_v2.0/wtrain/lib/src/wyolo/trainer/states/cross\_domain\_generalizer.py`. Las mediciones empíricas por par utilizadas para ajustar la regresión se publican junto con este trabajo en `domain\_pairs.npz`.

## 8. Impacto Más Amplio / Declaración de Ética
Un detector que pierde 30 pp bajo iluminación nocturna no detecta piezas defectuosas en una línea de producción; en entornos automotrices o médicos, tales omisiones son críticas para la seguridad. Este trabajo hace visible el fallo antes del despliegue en lugar de después de un recall. El estimador se ejecuta completamente on-device, por lo que ninguna imagen patentada sale de la institución. La principal preocupación de doble uso es que el mismo mecanismo de distancia pueda ser utilizado de forma adversaria para diseñar desplazamientos que evadan el predictor; mitigamos esto empleando una compuerta por intervalo conservadora, que necesariamente sobreestima el riesgo. El costo de carbono del paso agregado es insignificante: FID y SC reutilizan los embeddings almacenados en caché y agregan solo 2.1 s en GPU, en comparación con horas de entrenamiento desperdiciadas en modelos mal desplegados.

## 9. Conclusión & Trabajo Futuro
Presentamos un predictor calibrado de la degradación de mAP downstream bajo desplazamiento de dominio a nivel de representación, empleando la Distancia Fr\'echet de Inception como covariable principal y un índice de complejidad de escena como opción de calibración conservadora, con intervalos de confianza bootstrap de 1,000 iteraciones. En siete pares de dominios industriales reales, el modelo de solo-FID alcanza un $R^2 = 0.988$ con un MAE de 1.05 pp, y predijo el colapso nocturno en los datos reservados en $32.9$ pp (real: $30.4$ pp) dentro de su intervalo antes del despliegue. El trabajo futuro extenderá el modelo a (a) desplazamiento semántico, donde las distancias condicionadas por clase reemplazan a la FID global, (b) predicciones de degradación por clase y (c) detección de derivas en tiempo real que reajuste el predictor a medida que ingresan nuevos lotes no etiquetados en producción.

## 10. Agradecimientos
Agradecemos a los colaboradores del proyecto wisrovi-suit por la infraestructura fundamental de CLI y orquestación que hizo posible esta investigación.

## References

1. Shai Ben-David, John Blitzer, Koby Crammer, Alex Kuber, Fernando Pereira, and Jennifer~Wortman Vaughan. A theory of learning from different domains. *Machine Learning*, 79(1-2):151--175, 2010.
2. Yuhu Chen, Wen Li, Xiang Chen, and Longshan Gao. Domain adaptive yolo for object detection in adverse weather conditions. In \em Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops, pages 1--8, 2022.
3. Mostafa Dehghani, Yi~Tay, Alexey Gritsenko, Zhe Zhao, Ibrahim Alabdulmohsin, Sara Sabour, Siamak Shakeri, Ashish Vasudevan, Albert Song, Mannat Singh, et~al. The efficiency misnomer: Rethinking ML metrics. *arXiv preprint arXiv:2110.12894*, 2021.
4. Janez Dem\vsar. Statistical comparisons of classifiers over multiple data sets. *Journal of Machine Learning Research*, 7:1--30, 2006.
5. Piotr Doll\'ar, Mannat Singh, and Ross Girshick. Fast and accurate model scaling. In \em Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 924--932, 2021.
6. Bradley Efron and Robert~J Tibshirani. An introduction to the bootstrap. *Chapman* & Hall/CRC Monographs on Statistics and Applied Probability, 1994.
7. Saurabh Garg, Sivaraman Balakrishnan, J~Zico Kolter, and Zachary~C Lipton. Leveraging unlabeled data to predict out-of-distribution performance. In *International Conference on Learning Representations (ICLR)*, 2022.
8. Dan Hendrycks and Thomas Dietterich. Benchmarking neural network robustness to common corruptions and perturbations. In *International Conference on Learning Representations (ICLR)*, 2019.
9. Martin Heusel, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, and Sepp Hochreiter. Gans trained by a two time-scale update rule converge to a local nash equilibrium. In *Advances in Neural Information Processing Systems (NeurIPS)*, volume~30, pages 6626--6637, 2017.
10. Glenn Jocher, Ayush Chaurasia, and Jing Qiu. Yolo by ultralytics, 2023.
11. Andrew Ng. Mlops: From model-centric to data-centric ai. https://www.deeplearning.ai/the-batch/machine-learning-data-centric-ai/, 2021.
12. Benjamin Recht, Rebecca Roelofs, Ludwig Schmidt, and Vaishaal Shankar. Do imagenet classifiers generalize to imagenet? In *International Conference on Machine Learning (ICML)*, pages 5389--5400, 2019.
13. William~Steve Rodriguez~Villamizar. Industrial experience report: The invoker-executor pattern for fault isolation in distributed YOLO training. In \em IEEE International Conference on Software Engineering (ICSE) -- Industrial Experience Track, 2026.
14. William~Steve Rodriguez~Villamizar. Neuralforge ai: Distributed yolo training cluster with automated post-training analysis. 2026. PolyForm Noncommercial / AGPLv3 Dual License.
15. Chen Sun, Abhinav Shrivastava, Saurabh Singh, and Abhinav Gupta. Revisiting unreasonable effectiveness of data in deep learning era. In \em Proceedings of the IEEE International Conference on Computer Vision (ICCV), pages 843--852, 2017.
16. Superconductive. Great expectations: Always know what to expect from your data. https://greatexpectations.io/, 2023.
17. Rohan Taori, Achal Dave, Vaishaal Shankar, Nicholas Carlini, Benjamin Recht, and Ludwig Schmidt. Measuring robustness to natural distribution shifts in image classification. In *Advances in Neural Information Processing Systems (NeurIPS)*, volume~33, pages 18583--18599, 2020.
18. Minghao Xu, Dong Li, Chen Suo, Huiling Jia, Jianmin Wang, Hehe Wang, and Jing Zhang. Domain adaptation for object detection: A survey. *IEEE Transactions on Image Processing*, 30:4896--4910, 2021.
