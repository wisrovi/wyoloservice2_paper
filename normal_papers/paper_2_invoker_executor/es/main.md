# Estudio Empírico de Rendimiento del Patrón Invocador-Ejecutor para Orquestación Resiliente de MLOps

# Resumen & Palabras Clave
**Resumen:** La gestión de cargas de trabajo de GPU distribuidas para el entrenamiento de visión por computadora presenta desafíos para mantener la estabilidad de los nodos frente a altas demandas de VRAM. La ejecución tradicional de tareas mediante demonios puede provocar fallas en los nodos físicos debido a eventos de falta de memoria (Out-Of-Memory, OOM) desencadenados por cargas pesadas. En este estudio empírico de rendimiento, evaluamos el patrón Invocador-Ejecutor, un enfoque de orquestación donde un demonio ligero de Celery (Invocador) delega la ejecución de GPU a contenedores Docker efímeros (Ejecutor). Comparamos este enfoque con Kubernetes Jobs, Ray y Slurm en términos de sobrecarga de orquestación y tolerancia a fallos. Nuestros resultados indican que esta estrategia de aislamiento elimina las fallas críticas de los nodos causadas por picos de memoria, al tiempo que introduce una sobrecarga predecible de 2.1 segundos para la creación de contenedores, proporcionando una alternativa viable para la orquestación ligera y resiliente de MLOps.

**Palabras Clave:** Computación Distribuida, Contenedores Efímeros, Gestión de Memoria GPU, Tolerancia a Fallos, MLOps, Estudio Empírico.

# Introducción
El entrenamiento de modelos de visión por computadora, particularmente con arquitecturas avanzadas, ejerce un estrés significativo en la VRAM de la GPU y la memoria del sistema. En los pipelines distribuidos de MLOps, un intermediario centralizado distribuye tareas de entrenamiento a nodos de trabajo. Una implementación común se basa en un demonio persistente que recibe la tarea y ejecuta el ciclo de entrenamiento en su propio espacio de procesos.

Cuando ocurre un evento OOM, el asesino OOM del kernel de Linux termina procesos para recuperar memoria, lo que puede incluir al propio demonio persistente. Esto deja al nodo físico en línea pero desconectado de la cola distribuida, requiriendo intervención manual.

Para abordar esto, analizamos el patrón Invocador-Ejecutor. En lugar de ejecutar la carga directamente, el demonio actúa estrictamente como Invocador. Crea dinámicamente un contenedor Docker efímero y con recursos limitados (el Ejecutor) y le delega el entrenamiento, garantizando el aislamiento de fallos.

# Trabajo Relacionado
La gestión de recursos en clústeres de GPU multi-inquilino ha sido ampliamente estudiada. Tiresias [gu2019tiresias] y Optimus [peng2018optimus] presentan gestores de clústeres adaptados para el aprendizaje profundo. Para aplicaciones de IA distribuidas, Ray [moritz2018ray] ofrece un marco robusto, aunque su gestión de estado centralizada difiere de los enfoques ligeros basados en demonios.

Kubernetes [burns2016borg] proporciona amplias capacidades de orquestación de contenedores, incluida la gestión de Jobs. Slurm [yoo2003slurm] sigue siendo un estándar para la programación de cargas de trabajo de computación de alto rendimiento. Nuestro estudio compara el enfoque Invocador-Ejecutor con estos sistemas establecidos para evaluar su viabilidad como alternativa ligera.

# Arquitectura Propuesta / Metodología
El nodo físico se divide en dos capas lógicas: el Plano de Control Persistente (Invocador) y el Plano de Cómputo Efímero (Ejecutor).

## El Demonio Invocador
El Invocador es un trabajador ligero que opera con un uso mínimo de memoria. Sus responsabilidades son el sondeo de la cola y la gestión del ciclo de vida del contenedor. No importa bibliotecas pesadas de aprendizaje automático, mitigando el riesgo de corrupción de memoria relacionada con CUDA.

## El Ejecutor Efímero
Al recibir una tarea, el Invocador ejecuta una llamada al demonio Docker anfitrión. Construye un comando de ejecución del contenedor que vincula los conjuntos de datos requeridos y aplica límites estrictos de cgroup utilizando restricciones de memoria y GPU.

Si el Ejecutor intenta asignar memoria más allá de su límite, el kernel anfitrión termina el contenedor. El Invocador captura el código de salida distinto de cero, actualiza el estado de la tarea a fallida y reanuda el sondeo de la cola. El nodo físico no experimenta tiempo de inactividad.

# Configuración Experimental y Detalles de Implementación
Evaluamos esta arquitectura en un clúster de tres nodos. Cada nodo estaba equipado con una NVIDIA RTX 4090 (24 GB VRAM), 64 GB de RAM y una CPU de 24 núcleos.

Diseñamos una prueba de estrés para evaluar la resiliencia del sistema. Enviamos un lote de 100 tareas de entrenamiento, configurando el 20% con tamaños de lote excesivamente altos para forzar el desbordamiento de VRAM. Medimos el tiempo de actividad del nodo, el consumo máximo de memoria y las tasas de finalización de tareas en diferentes métodos: Demonio Heredado, Invocador-Ejecutor, Kubernetes Jobs, Ray y Slurm.

# Resultados y Discusión
El patrón Invocador-Ejecutor protegió con éxito el sistema operativo de los picos de memoria.

## Benchmark: Resiliencia y Sobrecarga
Comparamos el patrón Invocador-Ejecutor con Kubernetes Jobs, Ray y Slurm bajo las mismas condiciones.

| Métrica | Demonio Heredado | Invocador-Ejecutor | Kubernetes Jobs | Ray | Slurm |
|---|---|---|---|---|---|
| Fallos OOM del Anfitrión | 18 | 0 | 0 | 2 | 0 |
| Muertes de Tareas/Contenedores | 0 | 20 | 20 | 18 | 20 |
| Sobrecarga de Orquestación | N/A | ~2.1s | ~5.4s | ~1.8s | ~3.2s |

En la configuración heredada, las tareas maliciosas provocaron que el demonio fallara 18 veces. El patrón Invocador-Ejecutor experimentó cero fallos, aislando correctamente las 20 fallas en los contenedores efímeros.

Kubernetes Jobs proporcionó un aislamiento de fallos equivalente pero exhibió una mayor sobrecarga de orquestación (5.4 segundos) debido a la comunicación del plano de control. Ray mostró una menor sobrecarga (1.8 segundos) pero experimentó 2 fallas a nivel de anfitrión al no aislar los picos de memoria de manera efectiva. Slurm ofreció un fuerte aislamiento, pero requirió una configuración más compleja y exhibió una sobrecarga de programación de 3.2 segundos.

El patrón Invocador-Ejecutor equilibra una baja sobrecarga de orquestación (2.1 segundos) con un robusto aislamiento de fallos, haciéndolo adecuado para entornos donde implementar un plano de control completo de Kubernetes no es deseable.

# Conclusión y Trabajo Futuro
Este estudio empírico evalúa el rendimiento y la resiliencia del patrón Invocador-Ejecutor para la orquestación de MLOps. Al imponer un estricto límite de contenedores, el sistema mitiga las fallas inducidas por OOM. En comparación con Kubernetes Jobs, Ray y Slurm, este patrón ofrece una alternativa ligera con mínima sobrecarga. El trabajo futuro investigará el redimensionamiento dinámico de los límites de recursos de los contenedores durante el tiempo de ejecución.
