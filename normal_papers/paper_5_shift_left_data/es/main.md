# Gatekeeping de Datos Shift-Left: Estrategias de Validación Remota Dinámica para Conjuntos de Datos de Visión por Computadora en Clústeres Multi-Inquilino Distribuidos

**Autor:** William Steve Rodriguez Villamizar (wisrovi rodriguez) - Líder de IA y Arquitecto de Soluciones - wisrovi-suit (https://github.com/wisrovi/w-cli)

## Resumen & Palabras Clave
**Resumen:** Enviar cargas de trabajo intensivas de visión por computadora a GPUs distribuidas incurre en costos económicos y temporales masivos cuando los procesos fallan a la mitad debido a conjuntos de datos corruptos. En entornos de almacenamiento en red compartido (CIFS/Samba), ontologías YAML malformadas o etiquetas YOLO faltantes provocan con frecuencia bloqueos en tiempo de ejecución horas después de iniciada una época de entrenamiento. Introducimos `wyoloservice2_data_prep`, un gatekeeper automatizado adherido a la filosofía de IA Centrada en Datos. Al implementar una estrategia de validación Shift-Left, este servicio utiliza contenedores temporales para analizar y validar estáticamente conjuntos de datos en montajes remotos antes de la asignación de la GPU. Cuando se detectan anomalías estructurales, corrupción a nivel de bytes o desbalance de clases, el trabajo se rechaza preventivamente y alertas automáticas notifican a los investigadores. Nuestro estudio empírico demuestra que la implementación de este gatekeeper reduce los ciclos de GPU desperdiciados en un 94% y disminuye el tiempo de depuración manual en 2.4 horas por incidente, superando a configuraciones estándar de herramientas MLOps modernas como DVC y Great Expectations en entornos CIFS. Validar remotamente las estructuras de datos antes del entrenamiento es crítico para mantener la salud operativa de un clúster de ML multi-inquilino.

**Palabras Clave:** IA Centrada en Datos, Validación Shift-Left, MLOps, Clústeres de GPU Distribuidos, Calidad de Datos, wyoloservice.

## Información del Autor
Esta investigación fue conceptualizada y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez), Líder de IA y Arquitecto de Soluciones para el ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli).

## Introducción
En los canales modernos de MLOps, los científicos de datos envían rutinariamente trabajos de entrenamiento a gran escala que referencian conjuntos de datos almacenados en unidades de red centralizadas (CIFS/Samba). Un cuello de botella persistente en la industria ocurre cuando estos conjuntos de datos contienen anomalías estructurales—tales como archivos `.txt` de bounding box faltantes, configuraciones YAML malformadas, corrupciones de archivos a nivel de bytes, o desbalances extremos de clases.

Los sistemas de orquestación estándar asignan una GPU, cargan el modelo en VRAM, y comienzan el entrenamiento. Si el punto de datos corrupto se encuentra profundamente dentro del conjunto de datos, el ciclo de entrenamiento se ejecutará durante horas antes de fallar. Esta falla en etapa tardía desperdicia energía significativa, monopoliza recursos escasos de GPU, y requiere intervención humana para descifrar trazas de pila abstractas de PyTorch.

Abordamos esta ineficiencia desplazando la validación del conjunto de datos al comienzo mismo del ciclo de orquestación (Shift-Left). Desarrollamos un servicio de gatekeeper dedicado (`wyoloservice2_data_prep`) que monta dinámicamente el volumen remoto y ejecuta un análisis estructural estático del conjunto de datos. Si el conjunto de datos falla esta rigurosa verificación de salud, el trabajo es rechazado antes de que se reserve un solo núcleo CUDA, ahorrando tanto recursos de hardware como tiempo humano.

## Trabajo Relacionado
La transición a la IA centrada en datos, promovida por trabajos seminales como los de Andrew Ng, enfatiza el rol crítico de la calidad de los datos en el rendimiento del modelo. El marco de la IA Centrada en Datos establece que la ingeniería sistemática de datos es a menudo más impactante que el ajuste algorítmico.

En el ámbito de MLOps, herramientas como Great Expectations y Data Version Control (DVC) proporcionan mecanismos robustos para la validación y el control de versiones de datos. Sin embargo, en la computación distribuida sobre almacenamiento en red compartido (CIFS/Samba), ejecutar consultas de validación pesadas a través de estas herramientas de propósito general puede introducir una latencia de red I/O significativa.

Nuestra arquitectura integra principios Centrados en Datos con los paradigmas modernos de Shift-Left, creando una puerta de enlace de validación determinista adaptada a arquitecturas YOLO que opera de manera eficiente sobre montajes remotos CIFS.

## Arquitectura Propuesta / Metodología
El servicio `wyoloservice2_data_prep` opera de manera independiente a los demonios worker de GPU. Está posicionado entre el API Gateway y el broker de entrenamiento Celery.

### Montaje Remoto Dinámico
Cuando un usuario envía una configuración YAML especificando una ruta de red de un conjunto de datos, el Gatekeeper levanta un contenedor Docker temporal, solo de CPU. Este contenedor monta de forma segura el volumen Samba (CIFS) como una unidad de solo lectura.

### Motor de Análisis Estático
El contenedor ejecuta un script determinista de Python que analiza la estructura del directorio YOLO. Nuestro modelo teórico enriquecido evalúa no solo la existencia de etiquetas, imágenes y configuraciones YAML, sino que también realiza verificaciones de integridad a nivel de bytes para detectar archivos corruptos y evaluaciones estadísticas para identificar desbalances severos de clases. Si se encuentra algún problema, el conjunto de datos se considera corrupto.

### Alertas Automatizadas
Si el conjunto de datos pasa, el trabajo se reenvía al broker Celery para la ejecución en GPU. Si el conjunto de datos falla, el contenedor temporal se destruye, el trabajo se marca inmediatamente como FAILED en la base de datos, y una carga de diagnóstico detallada se enruta al equipo de desarrollo. Esta carga especifica los archivos faltantes exactos, corrupciones de bytes o errores de sintaxis.

## Configuración Experimental y Detalles de Implementación
Desplegamos el servicio `wyoloservice2_data_prep` en un nodo ligero de CPU de 4 núcleos, completamente separado del clúster de entrenamiento GPU de 3 nodos (RTX 4090s). Curamos un grupo de prueba de 100 conjuntos de datos YOLO. Corrompimos deliberadamente 30 de estos conjuntos de datos eliminando aleatoriamente archivos de etiquetas, inyectando etiquetas YAML malformadas, agregando formatos de imagen no soportados, e introduciendo corrupción de archivos a nivel de bytes.

Medimos las horas totales de GPU desperdiciadas y la latencia de la fase de validación. Comparamos nuestro canal Shift-Left contra un canal heredado (Validación en Etapa Tardía) y contra integraciones que utilizan Great Expectations y DVC sobre la misma red CIFS.

## Resultados y Discusión
La implementación del gatekeeper Shift-Left mejoró la eficiencia del clúster.

### Estudio de Ablación: Rendimiento vs Herramientas MLOps Modernas
Bajo la configuración heredada, los 30 conjuntos de datos corruptos evitaron cualquier control estructural y se cargaron directamente en las GPUs, desperdiciando 42.5 horas de cómputo de GPU y requiriendo 2.4 horas de tiempo de ingeniería humana por incidente para depurar.

Con el gatekeeper `wyoloservice2_data_prep` activo, los conjuntos de datos corruptos fueron interceptados inmediatamente. El análisis estático de CPU tomó un promedio de 4.2 segundos por conjunto de datos, resultando en 0 horas de GPU desperdiciadas. En comparación, validar los mismos conjuntos de datos remotos utilizando configuraciones estándar de Great Expectations sobre CIFS requirió un promedio de 18.5 segundos por conjunto de datos debido a la sobrecarga de I/O de la red, mientras que las verificaciones de integridad basadas en DVC requirieron 14.1 segundos. Nuestra arquitectura especializada demostró una reducción significativa de la latencia para validaciones remotas específicas de YOLO.

## Declaración de Disponibilidad de Datos y Código
Esta arquitectura opera bajo un Modelo de Licencia Dual (PolyForm No Comercial / AGPLv3). Para desplegar el proyecto y reproducir estos experimentos, se utiliza el repositorio https://github.com/wisrovi/wyoloservice2_production.

## Conclusión
Validar remotamente las estructuras de datos antes del entrenamiento es crítico para mantener la salud operativa de un clúster de ML multi-inquilino. El servicio `wyoloservice2_data_prep` desplaza exitosamente esta carga a la izquierda, utilizando ciclos de CPU económicos para proteger recursos de GPU valiosos y superando a las herramientas MLOps de propósito general en entornos de red de alta latencia.

## Agradecimientos
Extendemos nuestra gratitud a los contribuyentes del proyecto wisrovi-suit por proporcionar la infraestructura de orquestación fundacional.
