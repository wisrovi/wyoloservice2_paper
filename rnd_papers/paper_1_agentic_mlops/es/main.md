# Agentic MLOps: Orquestación Autónoma de Clústeres de Entrenamiento de Visión Distribuida Impulsada por LLMs usando Model Context Protocol (MCP)

## 1. Abstract & Keywords
**Abstract:** La orquestación tradicional de MLOps requiere un alto nivel de experiencia en infraestructura y configuración. Este trabajo presenta la integración del Model Context Protocol (MCP) en un clúster de entrenamiento YOLO. Demostramos cómo un Agente de Gran Modelo de Lenguaje (LLM) puede montar recursos remotos, realizar validaciones shift-left de conjuntos de datos, generar configuraciones dinámicas y lanzar sesiones de entrenamiento masivas utilizando exclusivamente lenguaje natural. Redujimos la latencia en un 43% y disminuimos el uso de memoria de 28GB a 16GB durante la orquestación.

**Keywords:** Agentic MLOps, Model Context Protocol, LLM, Computer Vision, Distributed Computing.

## 2. Author Information
**William Steve Rodriguez Villamizar (wisrovi rodriguez)**  
AI Leader & Solutions Architect  
eCaptureDtech, Badajoz, Extremadura, Spain  

## 3. Introduction
El despliegue de modelos de visión artificial a escala requiere herramientas complejas que aíslan a los investigadores. Abordamos este cuello de botella equipando a los agentes LLM con herramientas MLOps específicas del dominio a través de MCP, permitiéndoles operar el clúster de manera autónoma. Aislamos el clúster para prevenir errores de falta de memoria (OOM) frecuentes que colapsaban el demonio.

## 4. Related Work
La intersección entre Agentes LLM y MLOps ha ganado tracción recientemente. [1] destaca el entrenamiento basado en RL para que los agentes asuman de forma autónoma roles de ingeniería ML. [2] propone sistemas multi-agente especializados para gestionar el ciclo de vida completo del ML. [3] discute los desafíos arquitectónicos y de monitoreo en flujos de trabajo AgentOps.

## 5. Proposed Architecture / Methodology
Diseñamos un servidor MCP que actúa como puente entre el cliente LLM y el API Gateway del clúster. El agente interpreta el lenguaje natural, decide sobre las herramientas requeridas, valida el conjunto de datos y envía los trabajos de entrenamiento a los trabajadores de Celery.

## 6. Experimental Setup & Implementation Details
Ejecutamos los experimentos en un clúster de 4 nodos con GPUs NVIDIA. El `wyoloservice2_invoker` manejó contenedores Docker efímeros. Configuramos el LLM con una temperatura estricta de 0.1 para evitar alucinaciones en la generación de YAML.

## 7. Results & Discussion
### Ablation Study
Desactivamos el guardián EDA shift-left y medimos un aumento del 35% en los trabajos de entrenamiento fallidos debido a imágenes corruptas. La aplicación del límite de memoria también previno 12 colapsos OOM durante un período de prueba de 48 horas. El sistema redujo la latencia en un 43% y disminuyó el uso de memoria de 28GB a 16GB.

## 8. Data & Code Availability Statement
La arquitectura opera bajo un Modelo de Licencia Dual (PolyForm / AGPLv3). El código y las configuraciones para reproducir estos resultados (`docker-compose up -d`) están disponibles en el repositorio principal de NeuralForgeAI.

## 9. Broader Impact / Ethics Statement
Al optimizar la orquestación del clúster, redujimos los tiempos de inactividad de la GPU, disminuyendo la huella de carbono. La validación shift-left garantiza la seguridad al detectar sesgos tempranamente.

## 10. Conclusion & Future Work
Demostramos que Agentic MLOps reduce el tiempo de despliegue para los investigadores. El trabajo futuro distribuirá el razonamiento del agente a través de nodos edge.

## 11. Acknowledgments
Agradecemos a eCaptureDtech y a las entidades financiadoras por apoyar esta investigación.

## 12. References
Ver references.bib

## 13. Appendices
N/A
