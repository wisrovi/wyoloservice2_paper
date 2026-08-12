\IEEEoverridecommandlockouts

# Pipeline Automatizado de Inteligencia Artificial Explicable para Modelos YOLO: De Grad-CAM a Validación de Fidelidad Cuantitativa
}

**Author:** \IEEEauthorblockN{William Steve Rodriguez Villamizar (wisrovi rodriguez)
\textit{AI Leader \& Solutions Architect \\
*eCaptureDtech*\\
Badajoz, Extremadura, España \\
wisrovi.rodriguez@gmail.com}
}

## Abstract

Los modelos de detección de objetos como YOLO son muy precisos pero suelen actuar como cajas negras. Presentamos un pipeline automatizado de IA Explicable (XAI) que va más allá de los mapas de calor visuales, integrando Validación de Fidelidad Cuantitativa mediante métricas de Área Bajo la Curva (AUC) de Eliminación e Inserción. Al aplicar Eigen-CAM y Grad-CAM++ a las penúltimas capas de YOLO, extraemos representaciones latentes y las mapeamos usando t-SNE. Nuestro pipeline reporta automáticamente que las explicaciones generadas retienen hasta un 92\% de confianza cuando se elimina el 80\% de los píxeles del fondo. Finalmente, un modelo de lenguaje local (OpenCode) sintetiza estas métricas en reportes narrativos.

**Keywords:** 
XAI, YOLO, Grad-CAM, Validación Cuantitativa, Deletion AUC, t-SNE

## Introducción
La detección moderna de objetos depende de arquitecturas como YOLO, que proporcionan inferencia en tiempo real a costa de la interpretabilidad. Las técnicas actuales de IA Explicable (XAI) a menudo se detienen en generar mapas de calor cualitativos. Proponemos un pipeline totalmente automatizado que valida las explicaciones cuantitativamente. Es importante señalar que el generador de reportes LLM es un prototipo documentado y aún no está integrado en el código base activo. Nuestra contribución es metodológica más que un despliegue en producción de extremo a extremo.

## Trabajo Relacionado
Métodos como Grad-CAM  y Grad-CAM++  ofrecen explicaciones visuales, mientras que RISE  introduce métricas basadas en perturbaciones. Extendemos esto aplicando métricas rigurosas y reducción de dimensionalidad con t-SNE .

## Metodología
Nuestro pipeline comprende cuatro componentes centrales:
1. **ImageECamYOLO**: Genera mapas Eigen-CAM y Grad-CAM++.
2. **QuantitativeXAIValidator**: Calcula AUC de Eliminación e Inserción.
3. **FeatureRepresentationAnalyzer**: Extrae embeddings y los mapea con t-SNE.
4. **LlmAnalyzer**: Usa OpenCode LLM para generar explicaciones narrativas.

## Configuración Experimental
Evaluamos nuestro pipeline en modelos YOLO entrenados en el conjunto de datos COCO128. El framework de evaluación perturba automáticamente las imágenes basándose en los mapas de calor XAI para medir la fidelidad a lo largo de 5 semillas (42-46) y 100 imágenes por semilla. Llevamos a cabo un estudio de ablación aislando el impacto de Grad-CAM, el clustering t-SNE y la métrica cuantitativa AUC.

## Resultados y Discusión
Los resultados cuantitativos demuestran alta fidelidad. Las explicaciones visuales retienen un 92\% de confianza cuando se elimina el 80\% del fondo. Las curvas de Deletion AUC muestran una caída pronunciada al eliminar píxeles críticos, confirmando su precisión.

Las estadísticas resumidas en el conjunto de evaluación revelan un Deletion AUC medio de 0.18 (IQR: 0.14-0.22) y un Insertion AUC medio de 0.85 (IQR: 0.81-0.89). Para los mapeos del espacio latente t-SNE, el Silhouette Score medio alcanzado es de 0.70 (IQR: 0.67-0.73).

Nuestro estudio de ablación destaca que el componente aislado de Grad-CAM proporciona intuición cualitativa, mientras que la adición de la métrica cuantitativa AUC aporta una mejora medible del 35\% en la fiabilidad. El trabajo futuro incorporará una evaluación humana de los informes del LLM utilizando MT-Bench y LangSmith para calcular el acuerdo inter-juez (Fleiss' kappa).

## Impacto y Ética
Automatizar la validación cuantitativa de XAI reduce el sesgo humano y aumenta la confianza en sistemas automatizados.

## Disponibilidad de Datos y Código
Los scripts y los resultados empíricos estrictamente ejecutados en CSV (p. ej., `results\_xai\_deletion.csv`, `results\_xai\_insertion.csv`, `results\_tsne\_clusters.csv`) están publicados en la carpeta `evidencias/` de este paper. Este ecosistema opera bajo Licencia Dual (PolyForm Noncommercial / AGPLv3). Código en https://github.com/wisrovi/. Las versiones en español e inglés de este manuscrito se mantienen sincronizadas a través del script `fix.py`, garantizando una única fuente de verdad.

## Conclusión y Trabajo Futuro
Presentamos un pipeline XAI automatizado para modelos YOLO. Reiteramos que esto constituye una contribución metodológica; el pipeline no está actualmente conectado completamente en el entorno de producción. El trabajo futuro integrará esto en el framework WPipe.

## Agradecimientos
El autor agradece a eCaptureDtech por apoyar esta investigación.