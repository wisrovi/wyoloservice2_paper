# MLOps Agéntico: Orquestación Autónoma Dirigida por LLMs de Clústeres de Entrenamiento de Visión Distribuida mediante Model Context Protocol (MCP)

**William Steve Rodriguez Villamizar (wisrovi rodriguez)**  
AI Leader & Solutions Architect  

## Resumen y Palabras Clave

**Resumen:** Las arquitecturas tradicionales de Machine Learning Operations (MLOps) enfrentan desafíos de escalabilidad y estabilidad al orquestar cargas de trabajo de visión artificial distribuidas. Presentamos un marco aplicado que utiliza el Model Context Protocol (MCP) para interconectar Modelos de Lenguaje Grande (LLMs) con clústeres físicos de GPU. Al aislar los nodos del clúster a través de un patrón Invoker-Executor mediante demonios de tareas, mitigamos los fallos de Out-Of-Memory (OOM) que de otra manera colapsan los procesos host durante sesiones intensivas de entrenamiento YOLO. Además, integramos un mecanismo de validación de datos "shift-left" para rechazar preventivamente conjuntos de datos corruptos antes de asignar memoria de GPU. Evaluaciones empíricas frente a líneas base de la industria (Ray Train y Kubeflow) demuestran que este enfoque reduce la sobrecarga de orquestación, disminuye el consumo máximo de memoria del host de 28GB a un límite de 16GB, y previene los fallos OOM en pruebas de estrés de 72 horas. La integración de LLMs para la gestión de clústeres proporciona una metodología reproducible para la comunidad de ingeniería de ML.

**Palabras Clave:** MLOps Agéntico, Model Context Protocol, Computación Distribuida, Orquestación de LLMs, Validación Shift-Left.

## Información del Autor
Esta investigación fue conceptualizada y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez).

## Introducción
La escalabilidad de clústeres de entrenamiento distribuidos para modelos de visión artificial de alta resolución presenta desafíos de ingeniería significativos. Las fugas de memoria y los scripts de programación frágiles pueden degradar el rendimiento del clúster. En sistemas distribuidos, los fallos silenciosos de Out-Of-Memory (OOM) a menudo causan que el demonio de entrenamiento principal asigne memoria más allá de los límites físicos de la GPU, bloqueando el nodo entero.

Para abordar estos desafíos, introducimos un paradigma de MLOps Agéntico. Utilizamos un Modelo de Lenguaje Grande (LLM) equipado con herramientas especializadas del Model Context Protocol (MCP) [7], que permite el monitoreo dinámico de nodos, validación de datasets y despacho de trabajos aislados. Este enfoque adapta el enrutamiento de la carga de trabajo dinámicamente, en contraste con la orquestación YAML estática [3].

La ejecución del entrenamiento está aislada dentro de contenedores efímeros de Docker administrados por una cola de tareas Celery, introduciendo un patrón Invoker-Executor. Esto asegura que si un script de entrenamiento encuentra un error OOM, solo el contenedor aislado termina, preservando la estabilidad del demonio host.

## Trabajos Relacionados
La convergencia de agentes autónomos e ingeniería ML ha ganado tracción. Estudios recientes [4] demostraron que los LLMs pueden utilizar herramientas externas para realizar tareas complejas, incluyendo interacciones de API. En MLOps [3], la orquestación eficiente del entrenamiento distribuido sigue siendo un área activa de investigación. Marcos de trabajo como Ray [2] y Kubernetes [5] proporcionan bases sólidas para la computación distribuida, pero a menudo requieren configuración compleja y carecen de integración nativa con LLMs.

La validación de datos es crítica en los pipelines de ML. Breck et al. [1] enfatizaron la importancia de la validación de datos antes del entrenamiento del modelo. Construimos sobre esto implementando un mecanismo estricto de validación shift-left. Además, el impacto ambiental de una programación eficiente y la reducción de ciclos de cómputo desperdiciados ha sido bien documentada [6].

## Arquitectura y Metodología Propuesta
Nuestro sistema desacopla la orquestación de la ejecución física a través de tres capas: la Interfaz LLM-MCP, el Gateway Invoker y el Ejecutor Efímero.

### La Interfaz LLM-MCP
La API del clúster se expone a través de un servidor Model Context Protocol (MCP) personalizado [7]. El LLM actúa como cliente, recibiendo prompts en lenguaje natural y traduciéndolos en payloads REST concretos despachados de manera asíncrona. Esta capa de abstracción simplifica las interacciones del usuario con las colas distribuidas.

### Validación de Datos Shift-Left
Antes del despacho del trabajo, el LLM activa una herramienta de validación estática [1] para verificar cabeceras de imágenes y anotaciones de bounding box. Modelamos el clúster como una cola M/M/c donde los trabajos llegan a una tasa $\lambda$. Al rechazar preventivamente los datasets inválidos, la tasa de llegada efectiva de trabajos fallidos $\lambda_{fail}$ se reduce a 0, maximizando la tasa de servicio $\mu$ para trabajos válidos y minimizando la probabilidad de bloqueo del sistema.

### El Patrón Invoker-Executor
Una vez validados, las tareas se encolan en un broker distribuido. Crucialmente, el invoker no ejecuta el bucle de entrenamiento en su propio espacio de procesos. Genera un contenedor Docker efímero (el Ejecutor) con un límite de memoria estricto. Si el contenedor se cierra abruptamente por un pico de memoria, se destruye protegiendo el demonio invoker. 

![Arquitectura Invoker-Executor](../en/figures/fig1.pdf)

## Configuración Experimental y Detalles de Implementación
Desplegamos la arquitectura a través de un clúster local de cuatro nodos. El nodo manager ejecutó el broker Redis y el servidor FastAPI. Tres nodos worker, cada uno con una GPU NVIDIA RTX 4090 (24GB VRAM) y 64GB de RAM de sistema, ejecutaron el demonio invoker. El dataset comprendió 250,000 imágenes de alta resolución.

Sometimos el clúster a una prueba de estrés continua de 72 horas y comparamos nuestro enfoque con despliegues estándar de Ray Train [2] y Kubeflow [5] ejecutando las mismas cargas YOLO.

## Resultados y Discusión

### Estudio de Ablación: Aislamiento de Hardware y Líneas Base
Para validar el patrón Invoker-Executor, comparamos nuestra arquitectura contra Ray Train y un demonio local heredado. En la configuración heredada, registramos 12 fallos críticos de OOM sobre 72 horas. Ray Train manejó mejor las cargas pero aún sufrió 4 bloqueos a nivel de nodo debido a preasignación de memoria agresiva y falta de límites estrictos por contenedor en los jobs.

Al aplicar el límite efímero de Docker, nuestra arquitectura redujo las caídas del demonio a cero. El consumo de memoria host pico se limitó a 16GB, comparado con 28GB de la configuración heredada y 24GB en Ray Train.

| Métrica | Demonio Heredado | Ray Train | MLOps Agéntico (Nuesto) |
| --- | --- | --- | --- |
| Caídas OOM Host (72h) | 12 | 4 | 0 |
| Uso Pico de Memoria Host | 28GB | 24GB | 16GB |
| Tiempo de Cómputo Perdido | 18 horas | 5 horas | 0 horas |

![Comparación de caídas y uso de memoria](../en/figures/fig2.pdf)

### Estudio de Ablación: Validación Shift-Left
Introdujimos 500 archivos de imagen deliberadamente corruptos. Sin la validación shift-left, los trabajos de entrenamiento colapsaban a los 15 minutos en la primera época. Con la herramienta de validación habilitada, el agente rechazó los trabajos corruptos en 3.4 segundos. Este rechazo temprano mejoró el rendimiento general del clúster un 35% comparado con la línea base.

## Declaración de Disponibilidad de Datos y Código
Esta arquitectura opera bajo un Modelo de Licencia Dual (PolyForm Noncommercial / AGPLv3). Para desplegar el proyecto y reproducir los experimentos, se utiliza el repositorio https://github.com/wisrovi/wyoloservice2_production.

## Conclusión y Trabajo Futuro
Integrar LLMs con el Model Context Protocol proporciona una interfaz resiliente para MLOps distribuido. La combinación del guardián de datos shift-left y el patrón Invoker-Executor elimina fuentes comunes de degradación de clústeres, superando las líneas base estándar en tolerancia a fallos. Investigaciones futuras explorarán la negociación descentralizada de tareas sin un broker centralizado.
