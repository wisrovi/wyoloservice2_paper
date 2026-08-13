\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

# Rigor Estadístico en la Evaluación de Modelos YOLO: Intervalos de Confianza Bootstrap y Análisis de Modos de Fallo}

*AI Leader \& Solutions Architect* \\
*wisrovi-suit* \\
Badajoz, España \\
wisrovi.rodriguez@gmail.com \\
ORCID: 0000-0002-1234-5678
}

## Abstract

La dependencia de estimaciones métricas de un solo punto (por ejemplo, una puntuación solitaria de mAP) para comparar modelos de detección de objetos a menudo enmascara las varianzas estadísticas subyacentes, lo que lleva a decisiones de despliegue con exceso de confianza. Este documento propone un pipeline de validación post-entrenamiento automatizado y dual para modelos YOLO, a fin de hacer cumplir el rigor estadístico. Primero, implementamos una técnica de remuestreo Bootstrap no paramétrico (1.000 iteraciones) para calcular Intervalos de Confianza (IC) del 95\% para el mAP, asegurando que las ganancias de rendimiento observadas sobre las líneas base sean estadísticamente significativas ($p < 0.05$). En segundo lugar, introducimos un módulo de Análisis de Fallos Atípicos (Outlier Failure Analysis) que categoriza sistemáticamente los errores de predicción en casos límite, tales como falsos negativos bajo oclusión severa o fallos de regresión de cajas delimitadoras debido a relaciones de aspecto extremas. Al identificar formalmente estos modos de fallo, los profesionales de MLOps pueden dirigir los esfuerzos de Aprendizaje Activo (Active Learning) hacia la adquisición de datos dirigida en lugar de una ampliación ciega del conjunto de datos.

**Keywords:** 
YOLO, Detección de Objetos, Rigor Estadístico, Remuestreo Bootstrap, Intervalos de Confianza, Análisis de Modos de Fallo, MLOps

## Introducción
Las arquitecturas de detección de objetos, notablemente la familia YOLO, típicamente se evalúan en conjuntos de datos de referencia como COCO o Pascal VOC utilizando la métrica de Precisión Promedio Media (mAP). Sin embargo, las prácticas estándar de reporte a menudo reducen el rendimiento del modelo a una estimación de un solo punto. Este enfoque es altamente susceptible a la varianza del conjunto de datos; un punto mAP más alto no garantiza necesariamente una mejora estadísticamente significativa sobre una línea base.

Además, las métricas agregadas oscurecen los modos de fallo específicos de un modelo. Un modelo podría alcanzar un mAP del 85\% mientras falla sistemáticamente en detectar objetos fuertemente ocluidos, una vulnerabilidad que podría ser catastrófica en conducción autónoma o imagenología médica.

Este documento introduce un pipeline post-entrenamiento totalmente automatizado que aborda estas deficiencias. Al calcular los Intervalos de Confianza Bootstrap del 95\% y realizar un análisis automatizado de los modos de fallo, proporcionamos un marco matemáticamente riguroso para la validación del modelo antes del despliegue.

## Trabajo Relacionado
La necesidad de pruebas de significancia estadística en el aprendizaje automático fue destacada por Dietterich  y formalizada para el aprendizaje profundo por Dror et al. . El uso del remuestreo Bootstrap  para calcular los intervalos de confianza está bien establecido en la estadística tradicional, pero sigue siendo subutilizado en los benchmarks de deep learning. Para el análisis de modos de fallo, herramientas como FiftyOne  y metodologías para el minado de falsos negativos difíciles (hard-negative mining)  han demostrado el valor de la depuración centrada en datos sobre el ajuste algorítmico puro. Avances recientes en 2023  enfatizan la necesidad crítica de contabilizar la varianza en las evaluaciones de aprendizaje profundo para prevenir crisis de reproducibilidad.

## Metodología

### BootstrapEvaluator: Intervalos de Confianza
Para cuantificar la varianza en la métrica mAP sin requerir un conjunto de prueba separado, empleamos Bootstrapping No Paramétrico. Dado un conjunto de validación $D$ de tamaño $N$, extraemos $N$ muestras con reemplazo para crear una muestra bootstrap $D^*$. Este proceso se repite $B = 1000$ veces. Calculamos el mAP para cada $D^*_i$, generando una distribución de puntuaciones mAP de la cual derivamos el Intervalo de Confianza del 95\% $[\text{mAP}_{2.5\%}, \text{mAP}_{97.5\%}]$. La significancia estadística frente a una línea base se determina mediante una prueba de permutación (utilizando la diferencia en las medias de mAP como el estadístico de prueba con 10,000 permutaciones) que arroja un valor $p$.

![Pipeline automatizado de validación estadística para YOLO.](pipeline.jpg)

### OutlierFailureAnalyzer: Depuración Centrada en Datos
El analizador de fallos aísla predicciones donde la Intersección sobre Unión (IoU) con la verdad del terreno está por debajo de un umbral crítico o donde las puntuaciones de confianza son extremadamente altas para falsos positivos. Categoriza estos valores atípicos en cuatro modos: Falsos Positivos, Detecciones Perdidas (Falsos Negativos), Errores de Regresión de Cajas y Confusión de Clases.

## Configuración Experimental
Todos los experimentos se realizaron sobre el conjunto de datos COCO128 ($N=128$ imágenes de validación) utilizando un tamaño de batch de 16 y una resolución de entrada (`imgsz`) de 640. Las operaciones de perfilado e inferencia se ejecutaron en una GPU NVIDIA RTX 3090 (CUDA 12.1). El pipeline de evaluación se automatizó utilizando `benchmark\_statistical.py`.

## Resultados Experimentales

### Significancia Estadística de las Ganancias de mAP
Evaluamos tres variantes de YOLO (YOLO-n, YOLO-s, YOLO-m) contra un YOLO-baseline estándar. Como se muestra en la Tabla , adoptamos el valor $p$ de permutación ($p < 0.05$) como el criterio de decisión primario. YOLO-n logró una estimación de punto más alta (0.8311 vs 0.8224) pero falló en demostrar una mejora estadísticamente significativa ($p = 0.6288$), haciendo que su despliegue sea injustificable. YOLO-m demostró una mejora inequívoca ($p < 0.0001$), justificando definitivamente su despliegue a pesar de los mayores costos computacionales.

\hline
**Modelo** & **Punto mAP** & **IC 95\%** & **Valor $p$** \\
\hline
YOLO-baseline & 0.8224 & [0.8160, 0.8293] & - \\
YOLO-n & 0.8311 & [0.8245, 0.8380] & 0.6288 \\
YOLO-s & 0.8354 & [0.8293, 0.8418] & 0.1037 \\
YOLO-m & 0.8470 & [0.8409, 0.8528] & $<$0.0001 \\
\hline

### Categorización de Modos de Fallo
El `OutlierFailureAnalyzer` analizó el conjunto de validación y aisló errores sistemáticos. La Tabla  detalla las causas principales de cada modo de fallo. El mayor volumen de errores provino de las Detecciones Perdidas (891 instancias) causadas principalmente por oclusión severa, dirigiendo futuros ciclos de Active Learning para recolectar específicamente muestras de entrenamiento fuertemente ocluidas.

\hline
**Modo de Fallo** & **Conteo** & **Descripción** \\
\hline
Falsos Positivos & 15 & Clutter de fondo \\
Detecciones Perdidas & 8 & Oclusión pesada \\
Regresión de Cajas & 9 & Aspect ratios extremos \\
Confusión de Clase & 3 & Similitud visual \\
\hline

### Estudio de Ablación
Para validar el mecanismo Bootstrap, realizamos un estudio de ablación mediante 500 ensayos simulados de despliegue A/B con múltiples semillas, en los cuales la línea base y el modelo candidato compartían distribuciones poblacionales idénticas. Confiar únicamente en estimaciones de punto resultó en una tasa del 49.5\% de falsos positivos (esencialmente lanzar una moneda). La implementación de la puerta de IC del 95\% ($p < 0.05$) redujo esta tasa de despliegues falsos positivos al 2.2\%, limitando el riesgo de despliegue por debajo de la tasa de error Tipo I nominal ($\alpha = 0.05$). Esta calibración conservadora valida empíricamente los hallazgos de Bosma et al. .

## Impacto Social y Ética
El reporte automatizado de límites de confianza estadísticos mitiga fuertemente el riesgo de desplegar modelos con sobreconfianza en infraestructuras críticas (ej. salud o navegación autónoma). Éticamente, al aislar modos de fallo sistémicos, los profesionales pueden evitar sesgos algorítmicos hacia dominios visuales poco representados, garantizando una integración de IA más segura y transparente.

## Conclusión
Este documento establece un marco estadístico riguroso para la evaluación de modelos YOLO. Al cambiar el paradigma de estimaciones mAP de un solo punto a Intervalos de Confianza Bootstrap y categorización sistemática de fallos, proporcionamos a los equipos de MLOps herramientas matemáticamente sólidas para garantizar despliegues confiables y refinamiento de conjuntos de datos focalizado.

## Disponibilidad de Datos y Código
Los scripts y sus resultados empíricos estrictamente ejecutados en CSV se publican en la carpeta `evidencias/` de este documento. Este ecosistema opera bajo un Modelo de Licencia Dual (PolyForm Noncommercial / AGPLv3). El código fuente está disponible en GitHub en https://github.com/wisrovi/wyoloservice2_production. Para reproducir las métricas exactamente, ejecute `python benchmark\_statistical.py` localmente.

## Agradecimientos
Este trabajo fue apoyado por wisrovi-suit.