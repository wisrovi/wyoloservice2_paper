\IEEEoverridecommandlockouts
\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

# Cuantificando la Robustez de Modelos YOLO: Ataques Adversarios, Resiliencia al Ruido y Estimación de Incertidumbre en Despliegues Reales}

*wisrovi-suit* \\
Badajoz, España \\
wisrovi.rodriguez@gmail.com
}

## Abstract

A medida que los modelos de detección de objetos YOLO se despliegan cada vez más en entornos críticos para la seguridad, comprender su robustez y modos de fallo es fundamental. Este artículo presenta un marco de evaluación completo y automatizado para cuantificar la resiliencia de los modelos YOLO bajo condiciones adversas. Evaluamos los modelos utilizando ataques adversarios del Método del Signo del Gradiente Rápido (FGSM), midiendo las tasas de éxito del ataque a través de diversas perturbaciones epsilon. Además, evaluamos la degradación del rendimiento en cinco niveles de severidad de corrupciones de imagen comunes, incluyendo desenfoque gaussiano, ruido y compresión JPEG. Finalmente, implementamos Monte Carlo (MC) Dropout para realizar una descomposición Bayesiana de la incertidumbre Epistémica (del modelo) y Aleatoria (de los datos) a través de 20 pases hacia adelante. Nuestros resultados empíricos proporcionan métricas procesables para desplegar sistemas de visión por computadora resilientes y establecen un pipeline de auditoría de robustez post-entrenamiento completamente automatizado.

**Keywords:** 
YOLO, Robustez, Ataques Adversarios, FGSM, MC Dropout, Estimación de Incertidumbre, Incertidumbre Epistémica

## Introducción
Los sistemas de detección de objetos en tiempo real, particularmente las arquitecturas YOLO, han alcanzado una precisión de vanguardia bajo condiciones ideales de laboratorio. Sin embargo, los despliegues en el mundo real a menudo están sujetos al ruido de los sensores, condiciones climáticas y perturbaciones adversarias potencialmente maliciosas. Las métricas de precisión tradicionales (como mAP) no logran capturar la confiabilidad de un modelo cuando se enfrenta a datos fuera de distribución (OOD).

Este estudio introduce un pipeline de robustez post-entrenamiento automatizado que cuantifica las vulnerabilidades del modelo a lo largo de tres ejes críticos: resiliencia adversaria, tolerancia al ruido y estimación de incertidumbre. Al integrar estas métricas, proporcionamos una visión holística de la confiabilidad del modelo adecuada para entornos MLOps.

## Trabajo Relacionado
Las vulnerabilidades adversarias en redes neuronales profundas fueron destacadas por Goodfellow et al. , introduciendo el Método del Signo del Gradiente Rápido (FGSM). Hendrycks y Dietterich  establecieron benchmarks estandarizados para evaluar la robustez contra corrupciones comunes. Para la cuantificación de incertidumbre, Gal y Ghahramani  demostraron que el Dropout puede usarse como una aproximación Bayesiana para estimar la incertidumbre epistémica. Trabajos posteriores  han formalizado aún más la descomposición de la incertidumbre epistémica y aleatoria en tareas de visión por computadora.

## Metodología
Nuestro pipeline de robustez comprende tres evaluadores especializados:

### AdversarialAttackTester
Implementamos FGSM para generar perturbaciones adversarias $\eta = \epsilon \cdot \text{sign}(\nabla_x J(\theta, x, y))$. Evaluamos la tasa de éxito del ataque a lo largo de variaciones de $\epsilon \in \{0.01, 0.03, 0.05, 0.1, 0.2\}$, midiendo la caída proporcional en mAP.

### RobustnessNoiseEvaluator
Utilizamos la biblioteca Albumentations para simular corrupciones ambientales y de sensores, específicamente desenfoque gaussiano, ruido gaussiano, compresión JPEG y lluvia simulada. Cuantificamos la degradación de mAP en 5 niveles de severidad progresivos.

### UncertaintyQuantifier
Estimamos la incertidumbre predictiva usando MC Dropout. Para cada imagen de entrada, realizamos $T=20$ pases estocásticos hacia adelante con el dropout activado en el momento de la inferencia. Descomponemos la varianza total en:
1. **Incertidumbre Aleatoria:** Ruido inherente a los datos, estimado a través de la varianza predictiva media.
2. **Incertidumbre Epistémica:** Ignorancia del modelo, estimada a través de la varianza de las predicciones medias a través de los pases.

## Resultados Experimentales
El pipeline fue evaluado en modelos YOLO entrenados en el conjunto de datos COCO128.

### Vulnerabilidad Adversaria
Como se esperaba, la confianza del modelo se degrada linealmente con la magnitud de la perturbación $\epsilon$. Con una perturbación mínima de $\epsilon=0.01$, la tasa de éxito del ataque se observó en aproximadamente el 4\%, manteniendo un mAP robusto. Sin embargo, a medida que $\epsilon$ aumentó a 0.10 y 0.20, la tasa de éxito del ataque escaló exponencialmente, comprometiendo más del 30\% y 60\% de las detecciones respectivamente, destacando un espacio de vulnerabilidad crítico.

### Resiliencia al Ruido
A lo largo de los cinco niveles de severidad, el desenfoque gaussiano y el ruido gaussiano indujeron las caídas de rendimiento más pronunciadas. En el nivel de severidad 1, el mAP se degradó en menos del 10\%. Para el nivel de severidad 5, las caídas de confianza superaron el 40\% en todos los tipos de corrupción, indicando que las aumentaciones estándar de YOLO son insuficientes para una generalización extrema OOD.

### Descomposición de Incertidumbre
El análisis de MC Dropout a través de 20 pases desentrañó exitosamente las fuentes de incertidumbre. Observamos que las predicciones de alta confianza se correlacionaban estrictamente con una baja varianza Epistémica (certeza del modelo). Por el contrario, la varianza Aleatoria se mantuvo relativamente constante en todo el conjunto de datos, reflejando límites uniformes de ruido del sensor.

## Conclusión
Hemos presentado un pipeline de robustez automatizado que cuantifica estrictamente la vulnerabilidad adversaria, la resiliencia al ruido y la incertidumbre para modelos YOLO. Integrar estas métricas en pipelines CI/CD estándar asegura que los modelos desplegados posean límites de resiliencia verificados. El trabajo futuro explorará la integración de estas métricas en nuestro framework declarativo WPipe.

## Disponibilidad de Datos y Código
Los scripts y sus resultados empíricos en CSV están en la carpeta `evidencias/` de este documento. Este ecosistema opera bajo Licencia Dual (PolyForm Noncommercial / AGPLv3, compatible con normativas de publicación de IEEE). El código fuente está disponible en GitHub en https://github.com/wisrovi/. Para reproducir las métricas, ejecute `python benchmark\_robustness.py` localmente.

## Agradecimientos
Este trabajo fue apoyado por wisrovi-suit.