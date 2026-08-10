# Paper A: Arquitectura MLOps Descentralizada para Entrenamiento Autónomo y Explicabilidad Integrada

**Autores:** William Rodriguez
**Keywords:** MLOps, Distributed Training, Explainable AI, Grad-CAM, Celery, YOLO

## Resumen (Abstract)
El desarrollo y despliegue de modelos de Inteligencia Artificial (IA) requiere infraestructuras capaces de gestionar tanto la carga computacional como la interpretabilidad de los resultados. Este documento presenta una arquitectura MLOps descentralizada ("train_service") basada en contenedores efímeros y colas de tareas distribuidas (Celery) que automatiza todo el ciclo de vida del aprendizaje automático. A diferencia de las plataformas tradicionales de entrenamiento distribuido, nuestra arquitectura integra Inteligencia Artificial Explicable (XAI) mediante Grad-CAM directamente en los nodos de procesamiento (*workers*). Esta integración garantiza que la evaluación visual del modelo (auditoría de las decisiones de las redes neuronales convolucionales) escale de forma inherente junto con el entrenamiento de los modelos YOLO, proporcionando un ecosistema donde el entrenamiento autónomo y la explicabilidad están indisolublemente unidos.

## 1. Introducción
- Contexto de MLOps y el problema de las "cajas negras".
- Limitaciones del entrenamiento distribuido tradicional sin explicabilidad in situ.
- Aportación de la arquitectura `train_service2`.

## 2. Metodología y Arquitectura
- Componentes del sistema: Manager, Invoker, Worker (Executor) y Control Server.
- Orquestación dinámica mediante `wpipe`.
- Aislamiento efímero de contenedores Docker para reproducibilidad.

## 3. Integración Nativa de XAI (Grad-CAM)
- Descripción del estado `ImageECamYOLO`.
- Adaptación de Grad-CAM de xaviercanche para auditar modelos YOLO (detección de objetos).

## 4. Experimentación y Resultados
- Tiempos de ejecución y escalabilidad en clusters.
- Validación de mapas de calor generados post-entrenamiento.

## 5. Conclusión
- Impacto de tener XAI descentralizado en entornos de producción.
- Trabajo futuro.
