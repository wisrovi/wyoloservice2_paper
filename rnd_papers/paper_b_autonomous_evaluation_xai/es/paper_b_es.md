# Paper B: Inteligencia Artificial Explicable en el Borde: Evaluación Autónoma de Modelos de Visión usando Grad-CAM y Modelos de Lenguaje Grandes (LLMs)

## Resumen
La adopción de modelos de aprendizaje profundo en la industria está limitada por su naturaleza de "caja negra". Este artículo propone un novedoso flujo de trabajo MLOps autónomo e integrado en el ecosistema `train_service2` que no solo entrena modelos YOLO de manera descentralizada, sino que los evalúa automáticamente y provee Explicabilidad (XAI). Mediante la combinación de la técnica Grad-CAM (Gradient-weighted Class Activation Mapping) y Modelos de Lenguaje Grandes (LLMs) locales, el sistema genera reportes interpretables sobre el enfoque de las redes convolucionales sin intervención humana.

## 1. Introducción
El proyecto de I+D `train_service2` aborda un reto fundamental: cómo asegurar que un modelo entrenado distribuídamente ha aprendido características robustas y no simplemente artefactos del conjunto de datos. Tradicionalmente, esto requería que ingenieros de datos visualizaran e interpretaran los resultados manualmente. Aquí proponemos la automatización total del análisis de las capas convolucionales utilizando técnicas derivadas de la investigación de Xavier Canche.

## 2. Metodología: Integración de Grad-CAM
Una vez finalizado el entrenamiento del modelo (YOLO) en el contenedor Executor efímero, se dispara automáticamente un estado de pipeline (`ImageECamYOLO`). 
Este estado toma imágenes de validación/testeo e intercepta los gradientes de la última capa convolucional para generar mapas térmicos (heatmaps). 
Estos mapas indican las regiones espaciales precisas que guiaron la predicción del modelo (por ejemplo, los bordes de un componente electrónico en lugar del fondo de la imagen). 

## 3. Análisis Autónomo con LLMs Locales
Los resultados de los mapas térmicos, junto con las métricas empíricas del modelo (mAP, Precision, Recall, matrices de confusión extraídas con filtros "Fuzzy"), se proporcionan a un LLM ejecutándose localmente (`LlmAnalyzer` usando OpenCode). 
El LLM interpreta la evidencia visual y estadística para emitir un documento forense detallado (`LLM_Report.md` / `.docx`).

## 4. Conclusión
La inclusión de técnicas XAI como Grad-CAM en arquitecturas distribuidas fortalece profundamente el valor I+D del ecosistema. Garantiza la explicabilidad del modelo de inicio a fin (End-to-End), y abre la puerta a auditorías algorítmicas completamente automatizadas, lo cual es crítico para entornos industriales y médicos donde la "caja negra" ya no es aceptable.
