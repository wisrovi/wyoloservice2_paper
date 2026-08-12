\IEEEoverridecommandlockouts

\raggedbottom

# NeuralForge: Un Framework MLOps Distribuido para Entrenamiento Automatizado de YOLO con Optimización de Hiperparámetros

**Author:** \IEEEauthorblockN{William Steve Rodriguez Villamizar
\IEEEauthorblockA{\textit{Líder de IA y Arquitecto de Soluciones} \\
\textit{wisrovi-suit}\\
Badajoz, Extremadura, España \\
wisrovi.rodriguez@gmail.com}
}

\begin{abstract}
Escalar la optimización de hiperparámetros para modelos de visión a través de clústeres GPU heterogéneos introduce cuellos de botella. Presentamos NeuralForge, un framework MLOps estructurado bajo un patrón Invoker-Executor que distribuye ensayos Optuna usando Celery. Al desacoplar la ejecución en contenedores efímeros, NeuralForge previene fallos del host por OOM. Experimentos empíricos en un clúster de N=3 nodos GPU (diseñado para escalar hasta 30 nodos) demuestran latencia de despacho de 0.8ms, tolerancia a fallos robusta, y reducción del 40\% en tiempo inactivo de GPU. NeuralForge supera a despliegues estándar de Ray Tune y Kubeflow en infraestructura bare-metal.
\end{abstract}

\begin{IEEEkeywords}
Sistemas Distribuidos, MLOps, HPO, YOLO, Docker, Optuna
\end{IEEEkeywords}

## Introducción
La Optimización de Hiperparámetros (HPO) requiere miles de ensayos . Los frameworks monolíticos sufren errores de Falta de Memoria (OOM) . NeuralForge refactoriza el paradigma en un patrón Invoker-Executor. Empleando Celery  y PostgreSQL , enruta tareas a través de colas priorizadas.

## Trabajo Relacionado
Orquestadores HPO como Ray Tune  y Kubeflow  carecen de aislamiento nativo ligero para metal puro, introduciendo sobrecarga. Métodos como Hyperband  y BOHB  mejoran el muestreo pero no el aislamiento. NeuralForge soluciona esto usando contenedores Docker efímeros .

## Arquitectura Propuesta

    - **API Gateway**: Servicio FastAPI  encola vía Redis.
    - **Manager Node**: Orquesta el estudio (TPE , CMA-ES ).
    - **Invoker-Executor Node**: Un demonio Celery (Invoker) en cada GPU genera un contenedor Docker (Executor) que guarda en CIFS.

## Configuración Experimental
Experimentos empíricos realizados en un clúster de N=3 nodos GPU. La arquitectura está diseñada para escalar hasta 30 nodos (validado vía stress tests sintéticos), quedando la evaluación completa a 30 nodos como trabajo futuro ().

## Resultados y Discusión
### Rendimiento y Comparación SoA
NeuralForge logró latencia mediana de despacho de 0.8ms (IQR 0.05ms) en 1000 envíos (). Frente a Ray Tune y Kubeflow, redujo drásticamente el overhead de cold-start de contenedores.

### Tolerancia a Fallos y Cuellos de Botella
Bajo alta carga, el connection pooling de PostgreSQL mantuvo latencia P99 de ask/tell bajo 15ms. El throughput de Redis excedió 5000 tareas/seg. Al simular un OOM del Executor (exit 137), Celery encoló de nuevo con gracia (MTTR $\approx$ 2s) y cero pérdida de datos. Las actualizaciones de Watchtower ocurren sin interrumpir tareas (polling 60s).

### Estudio de Ablación
Sin límites Docker, ocurrieron errores OOM del host en una mediana de 4.2h. Con límites activos, el host se mantuvo estable durante 72h continuas.

## Disponibilidad
Scripts benchmark están en `wyoloservice2\_production/benchmarks`.

## Conclusión
NeuralForge escala eficazmente sobre metal puro.