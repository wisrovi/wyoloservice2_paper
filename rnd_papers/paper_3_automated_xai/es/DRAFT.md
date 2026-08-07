# Automated XAI Pipelines in Computer Vision: Integrating Pre-train EDA and On-Device LLM Diagnostics into the MLOps Lifecycle

## Abstract
La desconexión entre el entrenamiento del modelo y la interpretación de métricas requiere horas de análisis humano. Proponemos una arquitectura "Onion-Layer" donde el pipeline de entrenamiento ejecuta automáticamente un Análisis Exploratorio (EDA) estadístico y, tras el entrenamiento, un LLM local (OpenCode) genera informes narrativos y diagnósticos para explicar el comportamiento del modelo.

## 1. Introduction
Abordamos la Explicabilidad y el Diagnóstico Automatizado en MLOps, transformando los archivos CSV y matrices de confusión en información humana legible (MD/DOCX) utilizando IA generativa de forma automática.

## 2. Related Work
- **Are Large Language Models Post Hoc Explainers? (2024/2025):** Investigación sobre cómo los LLMs interpretan características visuales y generan resúmenes legibles.
- **PASTA: Perceptual Assessment System for explanaTion of Artificial Intelligence (2024/2025):** Benchmark que integra análisis explicativo y métricas automatizadas.
- **Automatic Configuration of LLM Post-Training Pipelines (AutoPipe) (2025/2026):** Automatización orientada por agentes para etapas post-entrenamiento.

## 3. Automated XAI Pipeline
Descripción del pipeline interno del *worker*: Extracción de EDA -> Entrenamiento YOLO -> Análisis Post-entrenamiento con LLM local.

## 4. Conclusion
Automatizar el diagnóstico del modelo (XAI) dentro del ciclo MLOps democratiza la toma de decisiones basada en datos sin intervención manual intensiva.
