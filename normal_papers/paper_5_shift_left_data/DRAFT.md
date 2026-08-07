# Shift-Left Data Gatekeeping: Dynamic Remote Validation Strategies for Computer Vision Datasets in Distributed Multi-Tenant Clusters

## Abstract
Enviar cargas intensivas a GPUs distribuidas es costoso si el proceso falla a la mitad por datasets corruptos o mal estructurados en unidades compartidas (CIFS/Samba). Introducimos `wyoloservice2_data_prep` como un "Gatekeeper" automatizado en la filosofía Data-centric AI, que ejecuta validaciones estáticas remotas (Shift-Left) previas al despliegue en GPU.

## 1. Introduction
Trasladamos la validación del dataset al inicio del ciclo (Shift-Left) para ahorrar recursos de hardware y tiempo humano, integrándolo con alertas automáticas (Slack).

## 2. Related Work
- **Position: Early-Stage Quality Assurance in Annotation Pipelines Is More Cost-Effective Than Late-Stage Validation (2026):** Demuestra que aplicar Shift-Left reduce drásticamente los costos.
- **Data Quality Profiling at Scale with Progressive Sampling: A Benchmark for Data-Centric AI Pipelines (2026):** Estrategias de muestreo para validación masiva.
- **Data-Centric Artificial Intelligence: A Survey (Zha et al., 2023):** Revisión del paradigma data-centric enfocado en recolección y validación estática de datos.

## 3. Remote Validation Mechanism
Uso de contenedores temporales para montar volúmenes Samba y comprobar la ontología del modelo (YAML) y la estructura de directorios de YOLO.

## 4. Conclusion
Validar la estructura de datos remotamente antes del entrenamiento es crítico para mantener la salud económica y operativa de un clúster multi-tenant.
