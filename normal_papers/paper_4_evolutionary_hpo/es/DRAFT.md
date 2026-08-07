# Decoupled Evolutionary Hyperparameter Search for YOLO Architectures in Edge-to-Core Distributed Computing Environments

## Abstract
La búsqueda de hiperparámetros (Random/Grid) en visión distribuida es ineficiente. Este paper describe una integración de Algoritmos Genéticos usando Optuna (TPESampler) completamente desacoplada a través de Celery y Redis. El modelo evolutivo optimiza dinámicamente aumentaciones de datos y parámetros de entrenamiento a lo largo de un pool de GPUs sin monopolizar recursos.

## 1. Introduction
Presentamos un modelo donde el estado del ensayo genético (Manager/PostgreSQL) reside separado de la ejecución matemática (Worker), permitiendo auto-escalado horizontal.

## 2. Related Work
- **Hyperparameter Optimization for Object Detection Models (YOLO) using Optuna (2023-2025):** Aplicación de TPE en Optuna para ajustar magnitudes de aumentación y entrenamiento en YOLO.
- **Evolutionary Hyperparameter Optimization for Deep Neural Networks using Genetic Algorithms (2024):** Enfoques evolutivos (supervivencia, cruce) para redes complejas.
- **Automated Data Augmentation and Hyperparameter Tuning for YOLO Architectures (2024/2025):** Metodologías para reducir el "domain gap" estabilizando configuraciones de visión.

## 3. Distributed Genetic Manager
Análisis del orquestador Celery (`wyoloservice2_manager`) y la base de datos de estudios en PostgreSQL.

## 4. Conclusion
El desacoplamiento del algoritmo genético reduce el costo computacional y acelera dramáticamente la convergencia del entrenamiento.
