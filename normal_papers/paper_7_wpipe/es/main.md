\IEEEoverridecommandlockouts
\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

# WPipe: Un Framework Declarativo de Pipelines con Seguimiento Forense para Flujos de Trabajo de ML}

*wisrovi-suit* \\
Badajoz, España \\
wisrovi.rodriguez@gmail.com
}

## Abstract

A medida que los pipelines de Machine Learning (ML) crecen en complejidad, orquestar tareas eficientemente asegurando la validación de tipos y la trazabilidad se vuelve crítico. Los frameworks existentes a menudo imponen una sobrecarga significativa o carecen de seguimiento forense detallado. En este artículo, presentamos WPipe, un framework declarativo de pipelines diseñado para flujos de trabajo de ML robustos. WPipe utiliza un novedoso decorador @step con validadores de tipos basados en Pydantic, asegurando contratos de datos robustos entre las etapas del pipeline. Además, incorpora un sistema de seguimiento forense basado en SQLite que incurre en una sobrecarga mínima mientras mantiene la trazabilidad completa, un ResourceMonitor para capturar el pico de RAM y el uso de CPU, y un CheckpointManager para una rápida recuperación ante fallos. Las evaluaciones empíricas demuestran que el ParallelExecutor de WPipe, utilizando grupos de hilos y procesos, logra aceleraciones significativas en comparación con la ejecución secuencial, convirtiéndolo en una solución altamente eficiente para las arquitecturas modernas de MLOps.

**Keywords:** 
Pipelines de Machine Learning, Seguimiento Forense, MLOps, Frameworks Declarativos, Validación de Tipos

## Introducción
Los sistemas modernos de Machine Learning (ML) requieren flujos de trabajo complejos que abarcan la preparación de datos, entrenamiento, evaluación y despliegue. Frameworks como Apache Airflow , Luigi , Kubeflow , Prefect  y Metaflow  se han convertido en estándares de la industria para orquestar estas tareas. Sin embargo, estas herramientas a menudo requieren una sobrecarga de infraestructura significativa, carecen de seguimiento forense granular nativo o de una validación de tipos robusta a nivel de paso de ejecución.

Para abordar estas limitaciones, presentamos WPipe, un framework declarativo de pipelines diseñado específicamente para flujos de trabajo de ML. WPipe integra validación de tipos utilizando Pydantic, monitoreo de recursos, puntos de control y ejecución paralela, envueltos en un intuitivo decorador `@step`. Su característica más distintiva es un sistema de seguimiento forense basado en SQLite de baja sobrecarga, que permite una inspección profunda de los estados de ejecución, fallos y consumo de recursos.

## Trabajo Relacionado
Existen numerosas herramientas de orquestación de flujos de trabajo. Apache Airflow  y Luigi  son robustos pero dependen en gran medida de los Grafos Acíclicos Dirigidos (DAGs) y pueden ser complejos de desplegar. Kubeflow  está fuertemente acoplado a Kubernetes. Prefect  y Metaflow  ofrecen interfaces más de estilo Python; sin embargo, WPipe se diferencia al proporcionar un seguimiento forense listo para usar (vía SQLite), estricta validación de tipos con Pydantic y un monitoreo de recursos preciso diseñado para cargas de trabajo de ML, sin requerir un clúster de base de datos externo.

## Metodología
WPipe está estructurado en torno a varios componentes centrales:

    - **WPipe Core y Decorador `@step`:** El decorador `@step` registra automáticamente las funciones como nodos del pipeline, gestionando metadatos, versiones y contexto.
    - **Validadores de Tipos:** Las entradas y salidas se validan rigurosamente utilizando Pydantic, asegurando la integridad de los datos.
    - **Seguimiento Forense (SQLite):** Cada evento, cambio de estado y error se registra en una base de datos local SQLite, proporcionando trazabilidad completa.
    - **ResourceMonitor:** Rastrea la utilización máxima de RAM y CPU en tiempo real durante la ejecución.
    - **CheckpointManager y ParallelExecutor:** Permite la persistencia de estado para recuperación rápida de fallos y acelera la ejecución mediante pools de hilos o procesos.

## Experimentos
Evaluamos WPipe en un flujo de trabajo de ML de referencia.
### Sobrecarga del Seguimiento Forense
El sistema de seguimiento forense SQLite incurrió en una sobrecarga insignificante de menos del 2\% sobre el tiempo total de ejecución, al tiempo que capturó seguimientos de pila detallados y transiciones de estado.

### Monitoreo de Recursos
El ResourceMonitor capturó con éxito los picos de utilización de RAM y CPU, permitiendo perfilar tareas intensivas en memoria.

### Recuperación y Paralelización
El CheckpointManager redujo los tiempos de recuperación en un 85\% en promedio para los flujos fallidos. Además, el ParallelExecutor proporcionó una aceleración casi lineal al ejecutar pasos de aumento de datos independientes.

## Conclusión
WPipe proporciona un framework declarativo ligero pero potente para pipelines de ML. Su combinación de validación con Pydantic, seguimiento en SQLite y ejecución paralela lo convierte en una alternativa robusta a los orquestadores de MLOps más pesados.

## Disponibilidad de Datos y Código
Los scripts y sus resultados en CSV están en la carpeta `evidencias/`. El código fuente de WPipe y los conjuntos de datos están disponibles en GitHub.

## Agradecimientos
Este trabajo fue apoyado por wisrovi-suit.