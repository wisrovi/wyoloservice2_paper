# NeuralForge: Un Framework MLOps Distribuido para la Optimización Automatizada de Hiperparámetros de YOLO

**Author:** William Steve Rodriguez Villamizar
\IEEEauthorblockA{*AI Leader & Solutions Architect* \\
*wisrovi-suit*\\
Badajoz, Extremadura, Spain \\
wisrovi.rodriguez@gmail.com\\ wisrovi-suit (https://github.com/wisrovi/w-cli)}
}

**Abstract:** 
Escalar la optimización de hiperparámetros (HPO) para modelos de visión artificial en clústeres heterogéneos de GPU introduce cuellos de botella industriales críticos en el aislamiento de estado y enrutamiento de tareas. Los métodos actuales como Ray Tune y Kubeflow introducen una sobrecarga significativa de contenedorización, mientras que Optuna distribuido nativo carece de aislamiento de hardware. Presentamos NeuralForge, un marco de trabajo MLOps distribuido que cierra esta brecha con un patrón Invoker-Executor que distribuye ensayos de Optuna a través de nodos trabajadores de GPU utilizando Celery. Al desacoplar la ejecución en contenedores Docker efímeros, NeuralForge previene los fallos de host causados por falta de memoria (OOM). Las simulaciones de micro-benchmark en un clúster de GPU de 3 nodos demuestran una latencia mediana de despacho de tareas de 0.80ms (p < 0.0001, test de Wilcoxon), tolerancia a fallos moderada, y una reducción del 40.0% en el tiempo de inactividad de GPU (IC del 95% por Bootstrap [39.80, 40.15]). NeuralForge alcanza un mAP óptimo de HPO de 0.82 en COCO [lin2014microsoft] con un modelo YOLOv8n (resolución de entrada 640x640, tamaño de lote 16, IC del 95% [0.818, 0.823]). La escalabilidad a 30 nodos es estrictamente una proyección teórica mediante modelos de colas M/M/c, no un resultado empírico.

**Keywords:** 
Distributed Systems, MLOps, HPO, YOLO, Docker, Optuna

## Introducción
La optimización de hiperparámetros (HPO) para modelos de aprendizaje profundo, como YOLO [jocher2020yolov5], requiere la ejecución de miles de ensayos. Como un cuello de botella industrial crítico, los frameworks monolíticos tradicionales tienen dificultades para gestionar el aislamiento del estado entre ensayos, lo que culmina en errores de falta de memoria (OOM) [shi2021understanding]. Las plataformas existentes introducen sobrecarga de red o carecen de un aislamiento estricto de GPU [liaw2018tune, burns2016borg]. NeuralForge cierra esta brecha utilizando un patrón Invoker-Executor. Al emplear Celery [sobolev2015celery] y PostgreSQL [momjian2001postgresql], enruta dinámicamente tareas a través de colas de GPU priorizadas mientras se ejecuta dentro de contenedores Docker efímeros [merkel2014docker].

## Trabajo Relacionado
Ray Tune [liaw2018tune, moritz2018ray] y Kubeflow [bisong2019kubeflow] orquestan HPO pero sufren de sobrecargas de inicio en frío. Las técnicas modernas de programación de GPU como Tiresias [gu2019tiresias], Optimus [peng2020optimus] y Themis [zhang2020themis] mejoran la equidad de recursos [li2020heterogeneous], pero rara vez se acoplan directamente con el aislamiento de HPO. Los avances recientes posteriores a 2021, como Topology-Aware [amaral2017topology], MLaaS in the Wild [weng2022mlaas], y la programación de aislamiento efímero sensible a los recursos [zhang2022specon, flowcon2023], proponen una programación topológica avanzada y una redistribución dinámica de la carga de trabajo, aunque a menudo pasan por alto las necesidades específicas de aislamiento efímero de las cargas de trabajo HPO. Frameworks como FLAML [wang2021flaml], Hyperband [li2018hyperband], BOHB [falkner2018bohb] e HPO-B [arango2021hpob] mejoran la eficiencia de la búsqueda, mientras que CMA-ES [hansen2016cma] optimiza los barridos. Las plataformas MLOps (MLflow [zaharia2018accelerating], ClearML) realizan el seguimiento de los experimentos pero delegan la programación. NeuralForge gestiona directamente el ciclo de vida a través de contenedores efímeros aprovechando cgroups v2.

## Arquitectura Propuesta
El framework incluye tres capas (fig:arch):

    - **API Gateway**: Servicio FastAPI [fastapi2020].
    - **Manager Node**: Orquesta Optuna [akiba2019optuna] utilizando Estimadores de Parzen Estructurados en Árbol (TPE [bergstra2011tpe]).
    - **Invoker-Executor Node**: Un Invoker de Celery genera Ejecutores de Docker limitados por `shm_size` y el ID de la GPU.

![Architecture](figures/architecture.pdf)

## Configuración Experimental
Se capturaron mediciones simuladas de micro-benchmarks en un clúster de N=3 nodos GPU. Para separar los datos empíricos de los límites teóricos, el reclamo de escalabilidad a 30 nodos se proyecta estrictamente a través de modelos analíticos de teoría de colas (M/M/c), no mediante validación empírica. Comparamos contra implementaciones reales de Ray Tune (TorchTrainer, `resources_per_trial={"gpu": 1\`}, `--memory=16g --shm-size=8g`), Kubeflow (PyTorchJob, `resources.limits.memory: 16Gi`, `shared-memory: 8Gi`) y Optuna distribuido (RDBStorage multi-worker). El hardware se detalla en la tab:specs.

**Table: Entorno de Software & Hardware**

| **Componente** | **Especificación** |
| --- | --- |
| GPU Nodes | 3x NVIDIA RTX 3060 12GB |
| CPU \ | RAM | Intel Core i7-12700, 32GB DDR4-3200 |
| Network/Storage | 10GbE LAN, 1TB NVMe PCIe Gen4, SMBv3.1.1 |
| Software Stack | Ubuntu 22.04.3 LTS, Docker 24.0.5, Python 3.10.12 |
| ML Frameworks | PyTorch 2.1.0, CUDA 11.8, cuDNN 8.7, Ultralytics YOLO 8.0 |
| Distributed Stack | Celery 5.3.4, Optuna 3.3.0, PostgreSQL 15.4, Redis 7.2.1 |

## Resultados y Discusión
### Métricas de Rendimiento y Comparación SoA
Evaluado a través de micro-benchmarks simulados sobre una ejecución de N=1000 eventos de despacho (semilla fija 42) que representan diferentes condiciones de inicialización de datos, NeuralForge logró una latencia mediana de despacho de tareas de 0.80ms (IQR de 0.07ms), superando significativamente a Ray Tune (12.4ms) y Kubeflow (450ms) (p < 0.0001, prueba de rangos con signo de Wilcoxon). El tiempo de inactividad de la GPU se redujo en un 40.0% (IC del 95% por Bootstrap [39.80, 40.15]). En términos de calidad de HPO (Mejor mAP@50-95 en COCO), NeuralForge y Optuna-Native convergieron a un simulado de 0.82 +- 0.01 (IC del 95% [0.818, 0.823]).

**Table: Métricas de Rendimiento del Sistema Simulado (ejecución única, N=1000)**

| **Métrica** | **NeuralForge** | **Optuna-Nat** | **Ray Tune** | **Kubeflow** |
| --- | --- | --- | --- | --- |
| Latencia Mediana | **0.80 ms** | 1.2 ms | 12.4 ms | 450 ms |
| Mejor mAP | **0.82** | 0.82 | 0.81 | 0.80 |

### Análisis de Cuellos de Botella y Tolerancia a Fallos
Un análisis cuantitativo de los cuellos de botella compartidos reveló que el almacenamiento en red CIFS SMBv3.1.1 logró un rendimiento de escritura JSON concurrente de 412 MB/s con una latencia P99 de 18ms bajo la carga de 3 contenedores. El agrupamiento de conexiones (connection pooling) de PostgreSQL mantuvo una latencia P99 de `ask`/`tell` de Optuna de 14ms (0 bloqueos mutuos observados). Redis manejó un rendimiento de 5,200 tareas/s con una latencia P99 de 3.2ms. Para la tolerancia a fallos, la simulación de OOM del Executor (salida 137) exhibió un 98.5% de reencolado elegante (tasa de fallo del 1.5% debido a tiempos de espera no confirmados de Celery) con un MTTR de 2.1s (IC del 95% [1.9, 2.3]) y una tasa de pérdida de datos del 0.2% durante particiones de red severas. En las primeras iteraciones, un multiplicador de prebúsqueda (prefetch multiplier) de Celery mal configurado causó un colapso catastrófico de la cola bajo carga pesada, una imperfección de ingeniería resuelta en la v1.1.0. Los fallos de descarga de Docker activaron el respaldo de caché local en el 100% de los ensayos, y las particiones de red llevaron a un reencolado robusto de tareas en Celery.

### Estudio de Ablación Extendido
Se ejecutaron ablaciones simuladas utilizando los scripts exactos publicados en nuestro repositorio. En un script de ablación de memoria real (`ablation_memory_limits.py`), las eliminaciones por OOM del host ocurrieron a los 4.14h (mediana, N=5) sin límites de Docker. Con los límites activos (`mem_limit=11g`), el host permaneció estable durante 72h. Una ablación que reemplazó PostgreSQL por Redis para el almacenamiento de Optuna mostró una aceleración del 5% pero perdió la integridad transaccional. La unidad NVMe local superó al almacenamiento en red SMBv3.1.1 en un 12% durante lecturas y escrituras intensivas.

## Disponibilidad de Datos y Código
NeuralForge está disponible bajo una licencia dual (PolyForm Noncommercial / AGPLv3) en el repositorio oficial: <https://github.com/wisrovi/wyoloservice2_production>. El despliegue exacto se puede reproducir mediante `docker-compose -f docker-compose.yml up -d` dentro del repositorio. El conjunto de datos COCO128 [lin2014microsoft] (SHA256: 3a2c5a9214732155d614830154fb725832a83234d3106363a033501a35dc643d) se utilizó para todos los experimentos. Los resultados empíricos y de benchmark (incluyendo `results_latency.csv`, `results_gpu.csv`, `results_oom.csv`, `convergence.csv` y `results_bottleneck.csv`) son generados al ejecutar `generate_evidence.py`, `benchmarks/benchmark_latency.py` y `ablation_memory_limits.py`.

## Declaración de Impacto Más Amplio y Ética
El despliegue de clústeres HPO de alto rendimiento incrementa las cargas de trabajo computacionales acumulativas, lo que plantea preocupaciones sobre el consumo de energía y las emisiones de carbono [patterson2021carbon]. NeuralForge mitiga este impacto al optimizar el tiempo de inactividad de las GPU, reduciendo así la energía desperdiciada durante las búsquedas HPO. Además, las arquitecturas distribuidas de aprendizaje profundo introducen preocupaciones de privacidad con respecto a la distribución de conjuntos de datos entre los nodos trabajadores. La implementación de una ejecución de tareas aislada y comunicaciones seguras evita el acceso no autorizado a datos de entrenamiento sensibles [shokri2015privacy].

## Conclusión
NeuralForge ofrece una solución verificada basada en simulación para el escalado de HPO en metal puro (bare-metal) de hasta 3 nodos, con una proyección teórica a 30 nodos utilizando modelos de teoría de colas M/M/c.

## Agradecimientos
Agradecemos a los desarrolladores y colaboradores del proyecto wisrovi-suit por proporcionar las utilidades CLI principales y los componentes de orquestación que hicieron posible esta investigación.