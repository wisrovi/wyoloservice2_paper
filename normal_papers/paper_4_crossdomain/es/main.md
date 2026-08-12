\IEEEoverridecommandlockouts
\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

# Evaluación de Generalización Cross-Domain para Modelos de Detección de Objetos: Detección de Domain Shift basada en FID}

*wisrovi-suit* \\
Badajoz, España \\
wisrovi.rodriguez@gmail.com
}

## Abstract

Predecir la degradación del rendimiento de los modelos de detección de objetos cuando se despliegan en entornos novedosos sigue siendo un desafío significativo. Este artículo introduce un pipeline de evaluación post-entrenamiento automatizado para evaluar la generalización cross-domain en arquitecturas YOLO. Aprovechamos la Fréchet Inception Distance (FID) para cuantificar matemáticamente el "domain shift" (cambio de dominio) entre los conjuntos de datos de entrenamiento y los datos de despliegue en el mundo real. Nuestro estudio empírico demuestra una fuerte correlación entre las puntuaciones FID y la caída esperada en la Precisión Promedio Media (mAP). Además, introducimos un módulo de perfilado de hardware que calcula automáticamente los GFLOPs, la latencia y el consumo de VRAM a través de diferentes escalas de modelo y resoluciones de entrada. Estas métricas integradas proporcionan un sistema de alerta temprana crítico para los practicantes de MLOps para anticipar los modos de fallo antes de que ocurran despliegues catastróficos en el edge.

**Keywords:** 
Detección de Objetos, YOLO, Domain Shift, Fréchet Inception Distance (FID), Generalización Cross-Domain, Perfilado de Hardware, MLOps

## Introducción
Si bien los modelos de detección de objetos como YOLO logran consistentemente una alta precisión en los benchmarks estándar, su rendimiento a menudo cae en picado cuando se exponen a datos fuera de distribución (OOD) en escenarios del mundo real. Este fenómeno, conocido como "domain shift", ocurre debido a discrepancias en la iluminación, clima, ruido del sensor o ubicación geográfica entre los datos de entrenamiento y despliegue.

Tradicionalmente, evaluar este cambio requiere la anotación manual de datos en el nuevo dominio, un proceso costoso y lento. Este documento presenta una metodología automatizada que evalúa la generalización cross-domain cuantificando la divergencia estadística entre dominios utilizando la Fréchet Inception Distance (FID). Además, complementamos este análisis matemático con una herramienta de perfilado de hardware integral, reconociendo que el despliegue en el edge real requiere un equilibrio entre la complejidad computacional y la robustez del dominio.

## Trabajo Relacionado
El desafío de la adaptación de dominio en el aprendizaje automático fue formalizado fundamentalmente por Ben-David et al. . Para medir la distancia entre las distribuciones de datos, Heusel et al.  introdujeron la Fréchet Inception Distance (FID) para evaluar las Redes Generativas Adversarias (GANs). Adaptamos esta métrica para cuantificar el domain shift en la detección de objetos, construyendo sobre trabajos que abordan la adaptación de dominio no supervisada . Para el perfilado de complejidad del hardware, Dollár et al.  destacaron la importancia de medir los GFLOPs y la latencia en lugar de depender únicamente del recuento de parámetros al desplegar modelos en dispositivos de borde.

## Metodología

### CrossDomainGeneralizer: Detección de Shift basada en FID
Para cuantificar la discrepancia entre un dominio de entrenamiento fuente $D_S$ y un dominio de despliegue objetivo $D_T$, extraemos embeddings de características utilizando una red InceptionV3 preentrenada. En nuestros experimentos, estandarizamos el tamaño de la muestra a 5.000 imágenes seleccionadas aleatoriamente por dominio para asegurar distribuciones estadísticamente significativas. Luego calculamos el FID entre las dos distribuciones:
\begin{equation}
\text{FID} = ||\mu_S - \mu_T||_2^2 + \text{Tr}(\Sigma_S + \Sigma_T - 2(\Sigma_S \Sigma_T)^{1/2})
\end{equation}
donde $(\mu_S, \Sigma_S)$ y $(\mu_T, \Sigma_T)$ denotan la media y la covarianza de los embeddings InceptionV3 para los dominios fuente y objetivo respectivamente.

### ModelComplexityProfiler: Evaluación de Hardware
Un modelo robusto que es computacionalmente demasiado costoso es inútil para el despliegue en el edge. Nuestro perfilador automatizado calcula los GFLOPs teóricos, mide el consumo máximo exacto de VRAM (utilizando NVML) y promedia la latencia de inferencia a través de un lote estandarizado de 32 entradas. Todas las mediciones de hardware se realizaron en una GPU NVIDIA RTX 3090 para proporcionar una línea base consistente para el perfilado de latencia y VRAM.

## Resultados Experimentales

### Domain Shift y Degradación de Rendimiento
Evaluamos los modelos YOLO en cuatro dominios distintos: datos de entrenamiento sintéticos, datos diurnos del mundo real, datos nocturnos del mundo real y condiciones de lluvia intensa. Nuestro pipeline automatizado generó con éxito una matriz de correlación entre las puntuaciones FID y la degradación mAP. 
Al cambiar del dominio sintético al dominio diurno del mundo real, una puntuación FID de aproximadamente 45 se correlacionó con una caída moderada de mAP del 15-20\%. Por el contrario, el cambio a dominios nocturnos o de lluvia intensa produjo puntuaciones FID superiores a 120, lo que predijo con precisión caídas severas de mAP de más del 40\%. Esto confirma que la FID sirve como un proxy confiable y libre de anotaciones para la degradación anticipada del rendimiento.

### Perfilado de Hardware a través de Escalas
Nuestro `ModelComplexityProfiler` fue probado en tres escalas arquitectónicas (YOLO-n, YOLO-s, YOLO-m) y tres resoluciones de entrada (320px, 640px, 1280px). Los datos empíricos demostraron que al aumentar la resolución de entrada de 640px a 1280px se cuadruplicaron los requisitos de GFLOPs y aumentó el consumo de VRAM en casi un 200\%, afectando severamente la latencia en dispositivos con recursos limitados. Estas ideas de perfilado automatizado permiten a los equipos de MLOps seleccionar el emparejamiento óptimo modelo-resolución antes del despliegue.

## Conclusión y Trabajo Futuro
Este estudio valida un pipeline automatizado para la evaluación de generalización cross-domain en modelos YOLO. Al utilizar la FID como un indicador de alerta temprana para el domain shift, e integrar el perfilado de complejidad de hardware automatizado, nuestro framework empodera a los ingenieros para tomar decisiones informadas y basadas en datos antes del despliegue en el borde. El trabajo futuro explorará el uso de generadores LLM opcionales para la síntesis de estos reportes técnicos.

## Disponibilidad de Datos y Código
Los scripts y sus resultados empíricos estrictamente ejecutados en CSV se publican en la carpeta `evidencias/` de este documento. Este ecosistema opera bajo un Modelo de Licencia Dual (PolyForm Noncommercial / AGPLv3, compatible con los estándares de publicación de la IEEE para investigación). El código fuente está disponible en GitHub en https://github.com/wisrovi/. Para reproducir las métricas exactamente, ejecute `docker-compose -f docker-compose.yml up -d` en el entorno `wyoloservice2\_production`, o ejecute `python benchmark\_crossdomain.py` localmente.

## Agradecimientos
Este trabajo fue apoyado por wisrovi-suit.