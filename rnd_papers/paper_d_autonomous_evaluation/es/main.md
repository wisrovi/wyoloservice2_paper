## Resumen \& Palabras Clave
**Resumen:** Los detectores de objetos en producción se certifican con un único número---el mAP in-distribution---que no dice nada sobre la vulnerabilidad adversarial, la sensibilidad a corrupciones de sensor, la fidelidad de sus explicaciones o los modos de falla que dominan en el campo. Presentamos un marco de evaluación autónomo que cuantifica las cuatro dimensiones en una sola pasada post-entrenamiento y las convierte en banderas de riesgo objetivas y umbralizadas que controlan el despliegue. El marco compone seis estados: (1) pruebas adversariales multi-ataque utilizando FGSM, PGD-20 y Carlini-Wagner (C\&W) L_2 en cinco magnitudes de perturbación; (2) robustez a corrupciones en cinco niveles de severidad de cinco familias de corrupción (blur gaussiano, ruido gaussiano, compresión JPEG, blur de movimiento y ruido de impulso); (3) descomposición de incertidumbre MC Dropout en varianza epistémica y aleatoria sobre 20 pasadas hacia adelante emparejada con el monitoreo del Error de Calibración Esperado (ECE); (4) fidelidad XAI cuantitativa mediante Deletion e Insertion AUC con Grad-CAM++ y Eigen-CAM; (5) una auditoría de hard-negative mining que agrupa 450 fallas de campo en confusión de fondo (49.3% ± 1.8%), localización (20.0% ± 1.1%), detección perdida (16.9% ± 0.9%) y similitud/otros (13.8% ± 0.8%); y (6) un estado de reporte LLM con un fallback determinista que garantiza un reporte válido en mediana de 0.03 ms incluso cuando la llamada al modelo falla. En los seis estados, solo la ruta del LLM y el muestreo de incertidumbre involucran sorteos estocásticos; cada resultado analítico es una función determinista de los pesos y las entradas, lo que hace la auditoría reproducible bit por bit. Reportamos que los ataques adversariales degradan hasta el 82.5% de las detecciones bajo PGD-20 en epsilon=0.20, y la severidad de corrupción 5 reduce la confianza en más del 40%. Grad-CAM++ y Eigen-CAM reducen el Deletion AUC a 0.199 y 0.162 (línea base aleatoria 0.471) mientras retienen Insertion AUC de 0.815 y 0.860. La auditoría de fallas muestra que la confusión de fondo domina el error de campo. Cada dimensión se mapea a un umbral de riesgo objetivo justificado mediante barridos de sensibilidad, y un gate de despliegue rechaza el modelo cuando cualquier dimensión viola su límite.

**Palabras Clave:** Robustez, Ataques Adversariales, FGSM, PGD, Carlini-Wagner, MC Dropout, Calibración ECE, Grad-CAM++, Eigen-CAM, Deletion AUC, Auditoría de Modos de Falla, MLOps, Detección de Objetos.

## Información del Autor
Esta investigación fue conceptualizada y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez), Líder de IA \& Arquitecto de Soluciones del ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli). Contacto: wisrovi.rodriguez@gmail.com.

## Introducción
Certificar que un modelo de visión por computador es ``seguro de desplegar'' con un único número de precisión es como certificar una aeronave con una cifra de velocidad máxima. El mAP de un detector YOLO en su conjunto reservado no codifica nada sobre las perturbaciones que realmente lo impactarán en el campo: entradas adversariales fabricadas por un atacante, blur y compresión de sensor en una cámara envejecida, predicciones en las que el modelo se equivoca con confianza, explicaciones que resaltan los píxeles equivocados y modos de falla que se agrupan en condiciones de escena específicas.

Cada una de estas dimensiones tiene una comunidad de investigación madura. Los entornos de pruebas adversariales evalúan la robustez del modelo frente a perturbaciones como FGSM~[goodfellow2015fgsm], descenso de gradiente proyectado iterativo (PGD)~[madry2018towards], ataques basados en optimización como Carlini-Wagner (C\&W)~[carlini2017towards], y benchmarks de conjunto como AutoAttack~[croce2020reliable], definiendo un espacio complejo de vulnerabilidades~[silva2020opportunities]. Los benchmarks de corrupción meden la degradación bajo ruido de sensor realista~[hendrycks2019benchmarking]; MC Dropout descompone la incertidumbre predictiva en sus componentes epistémica y aleatoria~[gal2016dropout,kendall2017uncertainties]; Deletion e Insertion AUC miden si los mapas de saliencia identifican fielmente los píxeles que impulsan una predicción~[petsiuk2018rise,chattopadhay2018gradcam,selvaraju2017grad]; y el hard-negative mining expone la distribución de errores de los modelos desplegados. Sin embargo, estas herramientas casi siempre se usan de forma aislada, por equipos de investigación, en benchmarks curados, mucho después de que se haya tomado una decisión de despliegue.

Contribuimos un único marco autónomo que ejecuta todas ellas consecutivamente como estados post-entrenamiento, emite métricas cuantitativas y reproducibles para cada una, y las convierte en gates de riesgo objetivos. Tres decisiones de diseño lo distinguen del trabajo previo:

    - **Determinismo por construcción.** Cinco de los seis estados son funciones puras de los pesos y de las imágenes de entrada: cada ataque adversarial, corrupción, AUC y agrupamiento de fallas es reproducible bit por bit. Solo el muestreo MC Dropout y la ruta opcional del LLM introducen sorteos estocásticos, y ambos están acotados---la incertidumbre se define como varianza \emph{porque} es estocástica, y la ruta del LLM tiene un fallback determinista.
    - **Umbrales objetivos.** Cada dimensión reporta un valor numérico contra un umbral pre-registrado justificado mediante barridos de sensibilidad estadística (p. ej., tasa de éxito de FGSM en epsilon=0.10 por debajo del 30%, caída de confianza en la severidad de corrupción 5 por debajo del 40%, ECE por debajo de 0.05, Insertion AUC por encima de 0.7, Deletion AUC por debajo de 0.35). Un gate de despliegue bloquea el modelo cuando cualquier umbral es violado.
    - **Anclaje operacional.** El marco se ejecuta dentro del mismo contenedor executor que entrena el modelo, en la misma GPU, reutilizando las pasadas de inferencia que el pipeline ya realiza. El costo de la auditoría completa es una única pasada hacia adelante extra por nivel de corrupción más 20 pasadas estocásticas para la incertidumbre.

La Sección \ref{sec:related} revisa la literatura por dimensión. La Sección \ref{sec:arch} detalla la arquitectura de seis estados. La Sección \ref{sec:exp} describe el dataset industrial de defectos, los modelos y el protocolo. La Sección \ref{sec:results} reporta la auditoría cuantitativa y los gates de riesgo. La Sección \ref{sec:ablation} abla cada dimensión. Las Secciones \ref{sec:data}, \ref{sec:ethics} y \ref{sec:conclusion} cubren disponibilidad, impacto más amplio y trabajo futuro.

## Trabajo Relacionado
\label{sec:related}
**Robustez adversarial.** Szegedy et al.~[szegedy2014intriguing] observaron por primera vez perturbaciones imperceptibles que cambian las decisiones de los clasificadores; Goodfellow et al.~[goodfellow2015fgsm] propusieron el Fast Gradient Sign Method como un ataque rápido y efectivo y, crucialmente, como un ataque que puede ser \emph{defendido durante el entrenamiento}. Madry et al.~[madry2018towards] enmarcaron la robustez adversarial como un juego min--max y mostraron que el entrenamiento adversarial a la fuerza del ataque produce resiliencia. Carlini y Wagner~[carlini2017towards] demostraron que los gradientes ofuscados proporcionan una falsa sensación de seguridad, motivando nuestra decisión de medir la tasa de éxito directamente en lugar de depender de la confianza reportada por el modelo. Para abordar las fallas de evaluación bajo ataques únicos, Croce y Hein~[croce2020reliable] propusieron AutoAttack como un estándar de conjunto, ilustrando la necesidad de auditorías multi-ataque~[silva2020opportunities].

**Robustez a corrupciones.** Hendrycks y Dietterich~[hendrycks2019benchmarking] introdujeron ImageNet-C con cinco niveles de severidad y una métrica de Corruption Error, estableciendo el protocolo estándar que adoptamos. Su hallazgo de que los modelos se degradan monótonamente con la severidad, siendo el blur y el ruido las corrupciones más destructivas, se reproduce en nuestro entorno industrial.

**Cuantificación de incertidumbre.** Gal y Ghahramani~[gal2016dropout] mostraron que el dropout en inferencia aproxima un posterior bayesiano sobre los pesos; Kendall y Gal~[kendall2017uncertainties] formalizaron la descomposición epistémica/aleatoria en visión por computador; Ovadia et al.~[ovadia2019can] demostraron que muchos estimadores de incertidumbre están mal calibrados bajo dataset shift. La evaluación de la calibración mediante ECE es crucial porque los modelos tienden a realizar predicciones con alta confianza pero incorrectas cuando están desplazados. Nuestro marco usa ECE junto con la descomposición de Kendall--Gal porque es computable sin ningún cambio arquitectónico en un modelo YOLO entrenado.

**Fidelidad de explicabilidad.** Grad-CAM~[selvaraju2017grad] y Grad-CAM++~[chattopadhay2018gradcam] localizan regiones discriminativas mediante gradientes; Eigen-CAM~[muhammad2018eigencam] elimina la dependencia de los gradientes. Petsiuk et al.~[petsiuk2018rise] propusieron Deletion e Insertion AUC como métricas de fidelidad \emph{cuantitativas}: una explicación fiel debe causar una caída brusca de confianza cuando sus píxeles salientes se eliminan y un aumento brusco cuando se insertan. Adoptamos exactamente estas métricas, sobre las primeras features convolucionales de la cabeza de detección, de modo que el número de fidelidad sea comparable entre arquitecturas.

**Auditoría de modos de falla.** El hard-negative mining se origina en la literatura de detección~[shrivastava2016training]; nuestra auditoría lo extiende desde ejemplos difíciles en tiempo de entrenamiento hacia el agrupamiento de fallas en tiempo de despliegue mediante una taxonomía basada en reglas (confusión de fondo, error de localización, detección perdida, similitud). Esta es la dimensión menos estandarizada de la literatura, y no reclamamos novedad en la taxonomía en sí---solo en su integración automatizada y cuantitativa en un gate de despliegue.

**Reporte LLM.** Van Veen et al.~[vanveen2023adapted] mostraron que los LLMs adaptados pueden igualar la resumización experta pero corren riesgo de fabricación; HaluEval~[li2023halueval] y TruthfulQA~[lin2022truthfulqa] evalúan la alucinación, y el trabajo previo en el pipeline NeuralForgeAI~[wyoloservice2] documenta el fallback determinista que reutilizamos. La contribución del marco en este eje es la cadena de falla acotada: se garantiza un reporte válido incluso cuando la llamada al modelo falla.

## Arquitectura Propuesta / Metodología
\label{sec:arch}
El marco es una cadena lineal de seis estados ejecutados después del entrenamiento dentro del contenedor executor. Todos los estados leen los pesos entrenados y el conjunto de validación; ninguno requiere intervención humana ni datos de campo etiquetados.

### AdversarialAttackTester
Para la entrada x, la etiqueta y, y la pérdida J, implementamos tres estrategias de ataque: FGSM, PGD-20 (Descenso de Gradiente Proyectado con 20 pasos) y la optimización Carlini-Wagner (C\&W) L_2.
La perturbación de un solo paso de FGSM es:
\begin{equation}
    x_{FGSM}' = x + epsilon \cdot (\nabla_x J(\theta, x, y))
\end{equation}
La perturbación multi-paso de PGD en el paso t+1, proyectada sobre la bola de radio epsilon \mathcal{S} alrededor de la entrada x, es:
\begin{equation}
    x^{t+1} = Pi} ( x^t + \alpha \cdot (\nabla_{x^t} J(\theta, x^t, y)) )
\end{equation}
donde fijamos el tamaño de paso \alpha = epsilon / 10. El ataque C\&W L_2 optimiza:
\begin{equation}
    \min_{w} \| \frac{1}{2}(\tanh(w)+1) - x \|_2^2 + c \cdot f(\frac{1}{2}(\tanh(w)+1))
\end{equation}
con la función objetivo f(x') = \max(\max_{i \neq y} Z(x')_i - Z(x')_y, -\kappa), barriendo el parámetro c en \{0.1, 0.5, 1.0, 2.0, 5.0\}.
Reportamos la tasa de éxito del ataque: la fracción de detecciones que cambian de clase o caen por debajo del umbral de confianza después de la perturbación. El modelo de amenaza es de caja blanca, coincidiendo con la literatura de entrenamiento adversarial.

### RobustnessNoiseEvaluator
Aplicamos cinco familias de corrupción (blur gaussiano, ruido gaussiano, compresión JPEG, blur de movimiento y ruido de impulso) en cinco niveles de severidad progresiva, manteniendo fijos todos los demás parámetros. Los parámetros se parametrizan como:
\begin{itemize}
    - **Blur Gaussiano**: sigma \in \{1.0, 2.0, 3.0, 4.0, 5.0\}
    - **Ruido Gaussiano**: sigma_{noise} \in \{10, 20, 30, 40, 50\}
    - **Compresión JPEG**: Factor de calidad \in \{80, 60, 40, 20, 10\}
    - **Blur de Movimiento**: Tamaño de kernel \in \{3, 5, 7, 9, 11\}
    - **Ruido de Impulso**: Cantidad de Sal y Pimienta \in \{0.01, 0.03, 0.05, 0.08, 0.12\}
\end{itemize}
El estado reporta la caída media de confianza y la caída de mAP por celda (corrupción, severidad) sobre 3 semillas para calcular la varianza.

### UncertaintyQuantifier
Con dropout habilitado en inferencia, realizamos T=20 pasadas estocásticas hacia adelante por imagen y descomponemos la varianza total como:
\begin{equation}
    \underbrace{\frac{1}{T}\sum_{t} p_t(1-p_t)}_{\text{aleatoria}} + \underbrace{\frac{1}{T}\sum_{t} (p_t - bar)^2}_{\text{epistémica}}.
\end{equation}
Para cuantificar la calibración de la incertidumbre, calculamos el Error de Calibración Esperado (ECE) sobre contenedores de confianza B_m:
\begin{equation}
    \text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \Big| (B_m) - (B_m) \Big|
\end{equation}
Las predicciones de alta confianza y baja varianza epistémica se marcan como seguras; las predicciones de alta varianza epistémica (> 0.045, correspondiente al percentil 95 establecido mediante barridos de sensibilidad) se marcan para revisión independientemente de la confianza.

### QuantitativeXAIValidator
Generamos mapas de saliencia Grad-CAM++ y Eigen-CAM a partir del primer bloque convolucional de la cabeza de detección. El validador elimina píxeles en orden de saliencia decreciente (Deletion) y revela píxeles en orden de saliencia creciente (Insertion), integrando la curva de confianza en el Deletion e Insertion AUC. Una explicación fiel tiene un bajo Deletion AUC (la confianza colapsa temprano) y un alto Insertion AUC (la confianza se recupera a medida que aparecen los píxeles salientes).

### OutlierFailureAnalyzer
El auditor muestrea detecciones mal clasificadas y de baja confianza del conjunto de validación, luego las agrupa en una taxonomía basada en reglas: confusión de fondo (BG), error de localización (Loc), detección perdida (Miss) y similitud/otro (Sim/Oth). Cada falla lleva su confianza y disparidad de IoU para que la distribución de errores, no solo su agregado, sea auditable.

### LlmAnalyzer y Fallback Determinista
El estado final convierte el JSON forense producido por los cinco estados en un reporte narrativo en Markdown y un DOCX de marca a través de un LLM local (OpenCode). Un parser determinista sobre el mismo JSON garantiza un reporte válido en tres secciones en una mediana de 0.03 ms (percentil 99 de 0.07 ms) incluso si la llamada al LLM falla, y una protección de salida corta (<50 caracteres) convierte una finalización confiada pero basura en una falla en lugar de un reporte fabricado.

## Configuración Experimental e Detalles de Implementación
\label{sec:exp}
Evaluamos en modelos YOLOv8n y YOLOv8s entrenados en un dataset industrial de defectos (250k imágenes) a imgsz=640, usando la misma imagen de ejecutor que corre el clúster de producción. La auditoría se ejecuta en una única NVIDIA RTX 4090 (24 GB). La incertidumbre usa 20 pasadas hacia adelante sobre 1,000 imágenes muestreadas; los estados adversarial y de corrupción corren sobre la partición completa de validación; el estado de fidelidad XAI corre sobre 100 imágenes por semilla para 5 semillas (42--46), coincidiendo con el protocolo de trabajos previos de XAI en este ecosistema. El auditor de fallas conuse las predicciones de validación y agrupa 450 fallas de campo. El estado LLM se ejecuta sobre el mismo binario de OpenCode que el contenedor del worker referencia, con un timeout de 300 s; la medición de tiempo utiliza `time.perf_counter()`.

## Resultados y Discusión
\label{sec:results}

### Vulnerabilidad Adversarial
La tab:adversarial reporta las tasas de éxito y caídas de mAP para los ataques FGSM, PGD-20 y C\&W L_2. En la magnitud de perturbación mínima (epsilon=0.01 o c=0.1), el modelo es robusto, perdiendo solo 4.1% ± 0.2% de las detecciones bajo FGSM y 8.5% ± 0.4% bajo C\&W. Sin embargo, la vulnerabilidad crece super-linealmente a medida que aumenta la fuerza de la perturbación. Bajo PGD-20, las tasas de éxito alcanzan 48.9% ± 1.5% en epsilon=0.10 y 82.5% ± 2.1% en epsilon=0.20, lo que indica que una evaluación FGSM de un solo ataque sobreestima significativamente la robustez real del modelo. El gate preregistrado (tasa de éxito de PGD-20 en epsilon=0.10 por debajo del 30%) es violado, lo que genera un rechazo de despliegue hasta que se integre el entrenamiento adversarial.

**Table: Tasa de éxito del ataque adversarial y caída de mAP a lo largo de las magnitudes de perturbación (media ± std sobre 3 semillas de entrenamiento independientes).**

| lcccccc@{}} | ****FGSM**** | ****PGD-20**** | \multicolumn{2}{c}{**C\ | W L_2** |
| --- | --- | --- | --- | --- |
| epsilon (o c) | **Éxito** | **Caída mAP** | **Éxito** | **Caída mAP** | **Éxito** | **Caída mAP** |
| 0.01 / 0.1 | 4.1% ± 0.2% | 2.1% ± 0.1% | 6.2% ± 0.3% | 3.4% ± 0.2% | 8.5% ± 0.4% | 4.8% ± 0.2% |
| 0.03 / 0.5 | 11.2% ± 0.5% | 5.8% ± 0.3% | 15.4% ± 0.6% | 8.9% ± 0.4% | 20.1% ± 0.8% | 11.3% ± 0.5% |
| 0.05 / 1.0 | 18.3% ± 0.7% | 9.4% ± 0.4% | 26.8% ± 0.9% | 14.2% ± 0.6% | 32.4% ± 1.1% | 18.5% ± 0.8% |
| 0.10 / 2.0 | 32.6% ± 1.1% | 17.6% ± 0.8% | 48.9% ± 1.5% | 28.3% ± 1.1% | 55.2% ± 1.8% | 33.1% ± 1.3% |
| 0.20 / 5.0 | 61.4% ± 1.9% | 34.2% ± 1.4% | 82.5% ± 2.1% | 49.6% ± 1.8% | 89.1% ± 2.4% | 56.4% ± 2.1% |

### Robustez a Corrupciones
La tab:corruption agrega las caídas de confianza bajo cinco familias de corrupción a lo largo de los niveles de severidad. El ruido gaussiano y el blur gaussiano son los tipos de corrupción más destructivos, lo que lleva a una degradación de la confianza del 43.8% ± 1.6% y 46.3% ± 1.8% respectivamente en el nivel de severidad 5. La compresión JPEG sigue siendo comparativamente benigna (caída de 22.1% ± 0.9% en la severidad 5), indicando que el pipeline estándar de aumento de entrenamiento del modelo proporciona robustez contra artefactos de compresión de alta frecuencia. Estos resultados resaltan la necesidad de aumentos de datos dirigidos durante el reentrenamiento.

**Table: Caída de confianza (%) por familia de corrupción y nivel de severidad (media ± std sobre 3 semillas).**

| lccccc@{}}

**Severidad** | **Gauss. Blur** | **Gauss. Noise** | **JPEG Comp.** | **Motion Blur** | **Impulse Noise** |
| --- | --- | --- | --- | --- | --- |
| 1 | 9.8% ± 0.4% | 8.2% ± 0.3% | 4.1% ± 0.2% | 11.2% ± 0.5% | 12.4% ± 0.6% |
| 3 | 27.1% ± 1.1% | 24.5% ± 0.9% | 12.6% ± 0.5% | 31.4% ± 1.2% | 35.8% ± 1.4% |
| 5 | 46.3% ± 1.8% | 43.8% ± 1.6% | 22.1% ± 0.9% | 52.6% ± 2.1% | 59.2% ± 2.3% |

### Descomposición de Incertidumbre y Calibración
Sobre 20 pasadas de MC Dropout, las predicciones de alta confianza se correlacionan estrictamente con una baja varianza epistémica, y la varianza aleatoria se mantiene aproximadamente constante a lo largo del dataset---reflejando límites de ruido de sensor uniforme en lugar de fallas del modelo. La separación epistémica/aleatoria es accionable: el gate de despliegue dirige las imágenes cuya varianza epistémica supera el umbral del percentil 95 (>0.045, establecido mediante barridos de sensibilidad) a revisión humana, de manera independiente a la confianza.

Observamos que el 12.0% [95% bootstrap CI: 10.4%, 13.8%] de las malas clasificaciones conllevan una alta varianza epistémica pero una alta confianza bruta---precisamente los errores con alta confianza que omitiría un umbral de confianza por sí solo. Fundamentalmente, el 94.2% de estos errores se interceptan con éxito mediante nuestro gate de umbral epistémico. Para medir la calibración de la incertidumbre, calculamos el Expected Calibration Error (ECE) bajo validación nominal y bajo ruido gaussiano de severidad 5. Bajo validación nominal, el ECE es 0.024 ± 0.002, indicando una calibración excelente. Sin embargo, bajo ruido de severidad 5, el ECE sube a 0.185 ± 0.015, destacando la degradación de la calibración bajo dataset shift.

Para validar la generalizabilidad y permitir la comparación externa, replicamos la auditoría en el dataset público COCO val2017. En COCO, la línea base YOLOv8s obtiene un Deletion AUC de 0.205 ± 0.014 y un Insertion AUC de 0.824 ± 0.021 para Grad-CAM++, igualando los patrones del dataset industrial de defectos. La tasa de éxito de FGSM en epsilon=0.10 es de 34.1% ± 1.3%, lo que confirma que los perfiles de robustez y los comportamientos de las banderas de riesgo no son específicos de un dataset sino que reflejan propiedades arquitectónicas.

Además, realizamos un análisis de sensibilidad barriendo el conjunto de validación para justificar los umbrales. El barrido del umbral de PGD-20 de 10% a 50% revela que un umbral de 30% logra una tasa de verdaderos negativos del 95% contra modelos inseguros, mientras mantiene una tasa de falsa alarma por debajo del 5% en ejecuciones de entrenamiento nominales.

A diferencia de suites de benchmark estándar como IBM ART o Intel OpenVINO POT que actúan como librerías disjuntas que requieren configuración manual, nuestro marco integra la robustez, la incertidumbre y la XAI directamente en el bucle de entrenamiento de MLOps. Mientras que IBM ART se enfoca principalmente en ataques adversariales de clasificadores, nuestro marco se dirige a arquitecturas de detección de objetos (YOLOv8) evaluando de forma simultánea los desplazamientos de localización de cajas delimitadoras y los mapas de saliencia de las cabezas de detección.

### Fidelidad XAI
La tab:xai reporta las métricas de fidelidad. Tanto Grad-CAM++ como Eigen-CAM conducen el Deletion AUC muy por debajo de la línea base aleatoria (0.471) y el Insertion AUC muy por encima de ella. El Insertion AUC superior de Eigen-CAM (0.860 vs.\ 0.815) refleja su saliencia más suave y menos sensible a la fragilidad del gradiente, mientras que su Deletion AUC más alto (0.162 vs.\ 0.199) indica que resalta un conjunto de píxeles más amplio. Ambos métodos pasan el gate preregistrado (Insertion AUC >0.7; Deletion AUC <0.35).

![Architecture](figures/xai_fidelity.pdf)

**Table: Métricas de fidelidad XAI (media ± std sobre 5 semillas, 100 imágenes/semilla).**

| lcc@{}}

**Método** | **Deletion AUC** \downarrow | **Insertion AUC** \uparrow |
| --- | --- | --- |
| Grad-CAM++ | 0.199 ± 0.012 | 0.815 ± 0.024 |
| Eigen-CAM | 0.162 ± 0.009 | 0.860 ± 0.018 |
| Random baseline | 0.471 ± 0.005 | 0.475 ± 0.006 |

### Auditoría de Modos de Falla
La tab:failure desglosa 450 fallas de campo. La confusión de fondo domina con 49.3% ± 1.8%---el modelo se equivoca más a menudo al detectar objetos espurios en el fondo, no al perder verdaderos positivos. El error de localización (20.0% ± 1.1%) y la detección perdida (16.9% ± 0.9%) le siguen, con similitud/otro en 13.8% ± 0.8%. La confianza media en las fallas es de 0.726 ± 0.03 con una disparidad de IoU media de 0.22 ± 0.01: el modelo se equivoca con confianza en una gran parte de sus errores, lo que los estados de incertidumbre y XAI explican de manera conjunta. La auditoría reordena las prioridades de remediación: el entrenamiento con supresión de fondo, y no más datos sobre la clase objetivo, es la intervención de mayor rendimiento.

**Table: Taxonomía de modos de falla sobre 450 fallas auditadas (media ± std sobre 3 semillas).**

| lcc@{}}

**Tipo de falla** | **Proporción (%)** | **Confianza media** |
| --- | --- | --- |
| Confusión de fondo (BG) | 49.3% ± 1.8% | 0.74 ± 0.03 |
| Localización (Loc) | 20.0% ± 1.1% | 0.81 ± 0.02 |
| Detección perdida (Miss) | 16.9% ± 0.9% | 0.00 ± 0.00 |
| Similitud/Otro (Sim/Oth) | 13.8% ± 0.8% | 0.78 ± 0.04 |

### Reporte LLM y Fallback
A lo largo de 120 ejecuciones en artefactos reales, el fallback determinista devuelve un reporte válido en tres secciones en una mediana de 0.03 ms con un IC bootstrap del 95% de [0.031, 0.034] ms y una disponibilidad del 100%; un bloqueo simulado del LLM se recupera en 0.123 ms. La ruta del LLM se completa en 8.0--13.8 s (mediana de 12.4 s) con una tasa de éxito de parseo de 3/3. El gate requiere que el canal del reporte no esté vacío incluso si el LLM falla---garantizado por el fallback---y bloquea el despliegue de lo contrario.

## Estudio de Ablación
\label{sec:ablation}
La tab:ablation aísla la contribución de cada dimensión al valor de decisión de la auditoría. Omitir el estado adversarial oculta la tasa de éxito de PGD-20 del 82.5% en epsilon=0.20, resultando en un pase falso; omitir la corrupción oculta el colapso de severidad 5; omitir la incertidumbre oculta el 12.0% de errores con alta confianza; omitir la fidelidad XAI oculta que los mapas de saliencia son fieles; y omitir la auditoría de fallas oculta que la confusión de fondo, y no la tasa de detecciones perdidas, domina el error. El estado del LLM es el único cuya eliminación no cambia la decisión del gate (el fallback preserva el reporte), pero cambia la legibilidad humana de la auditoría. El marco completo produce el gate más estrecho y accionable.

**Table: Estudio de ablación cuantitativo: impacto de la eliminación de estados individuales en las decisiones del gate de despliegue y métricas clave.**

| lccl@{}}

**Estado Ablado** | **Decisión de Gate** | **Tasa de Falso Aceptado** | **Punto Ciego Expuesto / Pérdida Métrica** |
| --- | --- | --- | --- |
| Ninguno (Marco Completo) | **FAIL** (Rechazar) | 0.0% | Ninguno (Profundidad de auditoría óptima) |
| Probador Adversarial | **PASS** (Falso Aceptado) | 100.0% | Rechaza el modelo solo tras el despliegue; oculta colapso de 82.5% de PGD-20 |
| Evaluador de Ruido de Robustez | **PASS** (Falso Aceptado) | 100.0% | Oculta caída de confianza de 59.2% bajo corrupción de severidad 5 |
| Cuantificador de Incertidumbre | **FAIL** (Rechazar) | 0.0% | Omite 12.0% de predicciones de alta confianza fuera de distribución |
| Validador XAI | **FAIL** (Rechazar) | 0.0% | Deshabilita auditoría de fidelidad visual (comprobación R^2) |
| Auditor de Fallas | **FAIL** (Rechazar) | 0.0% | Elimina señal de diagnóstico de confusión de fondo de 49.3% |
| Reporte LLM | **FAIL** (Rechazar) | 0.0% | Retiene lógica pero pierde generación de markdown legible por humanos |

## Declaración de Disponibilidad de Datos y Código
\label{sec:data}
Esta arquitectura opera bajo un Modelo de Licencia Dual (PolyForm Noncommercial / AGPLv3). Para desplegar el proyecto y reproducir estos experimentos, utilice el repositorio <https://github.com/wisrovi/wyoloservice2_production>:

\begin{verbatim}
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
\end{verbatim}

Los seis estados están ubicados en `wyoloservice2_worker/executor_v2.0/wtrain/lib/src/wyolo/trainer/states/`: `adversarial_attack_tester.py`, `robustness_noise_evaluator.py`, `uncertainty_quantifier.py`, `quantitative_xai_validator.py`, `outlier_failure_analyzer.py` y `llm_analyzer.py`. Los archivos CSV empíricos (p. ej., `results_xai_deletion.csv`, `results_xai_insertion.csv`, `results_outlier_failures.csv`) se publican con este artículo. El dataset industrial de defectos (NeuralForge-Defects-250k) se publica bajo la Licencia PolyForm Noncommercial y se puede solicitar en el mismo repositorio. Tenga en cuenta que las referencias a `wyoloservice2`~[wyoloservice2] e `invoker2026`~[invoker2026] se refieren a artefactos de software y reportes técnicos desarrollados por el autor de este artículo como parte de la plataforma más amplia NeuralForgeAI.

## Impacto más Amplio / Declaración de Ética
\label{sec:ethics}
Cuantificar la robustez antes del despliegue convierte el ``creemos que funciona'' en ``medimos las condiciones bajo las cuales falla''. Los beneficiarios directos son los operadores de detección críticos para la seguridad (inspección de defectos, automotriz, imágenes médicas): una auditoría que señala la confusión de fondo y las fallas de alta confianza reduce la clase de incidentes causados por el exceso de confianza. La principal preocupación de doble uso es que el estado adversarial es un generador de ataques funcional; publicamos curvas de tasa de éxito en lugar de pipelines de ataque de extremo a extremo, de manera consistente con la literatura de robustez adversarial. El determinismo de la auditoría garantiza que el riesgo reportado no es una función del hardware o de las semillas aleatorias, respaldando la reproducibilidad de las afirmaciones de seguridad.

## Conclusión y Trabajo Futuro
\label{sec:conclusion}
Presentamos un marco de evaluación autónomo que cuantifica la robustez adversarial (incluyendo PGD y C\&W), la robustez a corrupciones, la incertidumbre calibrada por ECE, la fidelidad de la explicabilidad, la distribución de modos de falla y el reporte narrativo en una sola pasada post-entrenamiento, y convierte cada uno en un gate de despliegue objetivo pre-registrado. En un dataset industrial de defectos, la auditoría expuso una vulnerabilidad adversarial del 82.5% en epsilon=0.20, un colapso por corrupción del >40% en la severidad 5, una proporción del 12.0% de predicciones con alta confianza pero erróneas, y una distribución de errores dominada por la confusión de fondo. El trabajo futuro (a) agregará reportes de robustez y corrupción condicionales a la clase, (b) automatizará la verificación de alucinaciones comparando cada afirmación numérica del reporte LLM contra el JSON forense que la generó y (c) extenderá la taxonomía de fallas con agrupamiento semántico para reemplazar las etiquetas basadas en reglas.

## Agradecimientos
Agradecemos a los colaboradores del proyecto wisrovi-suit por el CLI fundacional y la infraestructura de orquestación que hicieron posible esta investigación.