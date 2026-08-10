# Paper B: Más allá de las métricas: Evaluación Autónoma de Redes Neuronales mediante Grad-CAM y LLMs Locales

**Autores:** William Rodriguez
**Keywords:** Autonomous Evaluation, Grad-CAM, Large Language Models (LLM), Explainable AI, Image Classification, Bias Detection

## Resumen (Abstract)
La evaluación de modelos de visión por computadora tradicionalmente recae en métricas cuantitativas como exactitud (accuracy) o precisión promedio (mAP). Sin embargo, estas métricas fallan al revelar si el modelo ha aprendido correlaciones espurias o sesgos del conjunto de datos. En este artículo presentamos un marco de evaluación autónomo que supera estas limitaciones combinando Inteligencia Artificial Explicable (Grad-CAM) con Modelos de Lenguaje Grande (LLMs) ejecutados de forma local. En nuestra implementación dentro del ecosistema `train_service2`, tras la fase de entrenamiento y predicción, el sistema genera automáticamente mapas de calor Grad-CAM. Posteriormente, un agente LLM local (OpenCode) analiza estos mapas de calor junto con las métricas tabulares para redactar reportes de interpretabilidad. Demostramos cómo esta sinergia permite detectar automáticamente sesgos en tareas de clasificación de imágenes sin requerir la intervención de un científico de datos humano, democratizando la auditoría de modelos a gran escala.

## 1. Introducción
- Insuficiencia de las métricas tradicionales (accuracy, F1-score) para detectar sesgos.
- El costo humano de auditar modelos manualmente.
- Hipótesis: La IA generativa (LLMs) puede auditar las explicaciones visuales (Grad-CAM) de la IA discriminativa (CNNs).

## 2. Marco Teórico y Trabajos Relacionados
- Fundamentos de Grad-CAM y mapeo de activaciones.
- Análisis automatizado mediante Modelos de Lenguaje.
- Soporte para estructuras de directorios de Clasificación vs Detección de Objetos.

## 3. Arquitectura del Evaluador Autónomo
- Pipeline Secuencial en el nodo de trabajo (Worker):
  1. `PostTrain` (Inferencia y Predicciones Clásicas).
  2. `ImageECamYOLO` (Generación de explicaciones visuales basadas en Grad-CAM).
  3. `LlmAnalyzer` (Redacción autónoma del análisis post-entrenamiento cruzando resultados).

## 4. Casos de Estudio: Detección de Sesgos (Bias)
- Experimento en Clasificación de Imágenes usando la arquitectura YOLO26.
- Demostración: El LLM detectando que el clasificador enfoca el fondo en lugar del sujeto.
- Eficiencia computacional de ejecutar OpenCode de manera distribuida.

## 5. Conclusión
- Hacia la IA auto-auditada en ecosistemas de producción.
- Implicaciones para la ética y seguridad en sistemas autónomos de clasificación.
