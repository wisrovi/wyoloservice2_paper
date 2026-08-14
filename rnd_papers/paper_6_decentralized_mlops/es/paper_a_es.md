# Paper A: Arquitectura MLOps Descentralizada para el Entrenamiento Escalable de Modelos de Visión Artificial en el Borde (Edge)

## Resumen
El entrenamiento de modelos de visión artificial (como YOLO) requiere habitualmente de infraestructuras monolíticas costosas. Este documento presenta la arquitectura del ecosistema `train_service2`, una solución MLOps altamente distribuida que desacopla la orquestación de tareas de la ejecución de cómputo intensivo. Utilizando colas de tareas con Celery, contenedores efímeros Docker y almacenamiento centralizado (Samba/MinIO/MLflow), se logra un sistema resiliente, escalable y tolerante a fallos, ideal para proyectos I+D e infraestructuras con recursos heterogéneos.

## 1. Introducción
El ciclo de vida del Machine Learning (ML) ha evolucionado, exigiendo arquitecturas que permitan una integración y despliegue continuos (CI/CD) aplicados a modelos (MLOps). El ecosistema `train_service2` fue concebido como un proyecto de I+D para democratizar el entrenamiento de modelos YOLO distribuyéndolo a través de una red de nodos "workers". 

## 2. Arquitectura del Sistema
El sistema divide su responsabilidad en múltiples repositorios especializados:
- **NeuralForgeAI / UI**: La interfaz de usuario que abstrae la complejidad.
- **Control Server & Manager**: Gestionan el enrutamiento de tareas y el estado global mediante Redis.
- **Invokers**: Nodos Celery que escuchan colas de tareas específicas y actúan como puentes hacia el hardware local.
- **Executors**: Contenedores Docker efímeros creados bajo demanda por los Invokers para ejecutar el entrenamiento y destruidos inmediatamente después de reportar los resultados, asegurando un entorno inmaculado para cada experimento.

## 3. Beneficios I+D
1. **Aislamiento de Carga de Trabajo**: Cada tarea de entrenamiento se ejecuta en un contenedor efímero, limpiando artefactos residuales (como la carpeta `extras`) en cada inicio para evitar fugas de datos.
2. **Escalabilidad Horizontal**: Añadir nuevos nodos de cómputo solo requiere iniciar un nuevo Invoker en el cluster apuntando al Redis central.
3. **Optimización de Recursos**: Las canalizaciones de datos usan montajes CIFS/Samba compartidos y bases de datos ligeras (Redis) para evitar cuellos de botella.

## 4. Conclusión
El paradigma descentralizado implementado por `train_service2` establece un nuevo estándar para la experimentación MLOps en entornos corporativos o académicos. Permite escalar dinámicamente recursos GPU sin requerir arquitecturas monolíticas masivas.
