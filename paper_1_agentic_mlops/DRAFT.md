# Agentic MLOps: LLM-Driven Autonomous Orchestration of Distributed Vision Training Clusters using Model Context Protocol (MCP)

## Abstract
La orquestación de plataformas MLOps tradicionales requiere un alto grado de experiencia en infraestructura y configuración (YAML/Bash). Este trabajo presenta la integración del *Model Context Protocol (MCP)* en un clúster de entrenamiento YOLO. Se demuestra cómo un Agente basado en Grandes Modelos de Lenguaje (LLM) puede montar recursos remotos, validar datasets mediante el enfoque "shift-left", generar configuraciones dinámicas y lanzar entrenamientos masivos utilizando exclusivamente lenguaje natural.

## 1. Introduction
El despliegue de modelos de visión por computador a gran escala requiere herramientas complejas que aíslan a los investigadores del Machine Learning. Abordamos este problema dotando a los agentes LLM de herramientas (tools) específicas del dominio MLOps a través de MCP, permitiéndoles operar el clúster de forma autónoma.

## 2. Related Work
La intersección de Agentes LLM y MLOps ha ganado tracción recientemente.
- **ML-Agent: Reinforcing LLM Agents for Autonomous Machine Learning Engineering (2026):** Destaca el entrenamiento basado en RL para que los agentes asuman roles de ingeniería ML de forma autónoma.
- **AutoML-Agent: A Multi-Agent LLM Framework for Full-Pipeline AutoML (2024/2026):** Propone sistemas multi-agente especializados para gestionar el ciclo de vida completo del ML.
- **A Survey on AgentOps: Categorization, Challenges, and Future Directions (2025):** Discute los desafíos de monitoreo y arquitectónicos en flujos de trabajo "AgentOps".

## 3. System Architecture
El servidor `wyolo-mcp` actúa como puente entre el cliente LLM (Claude, Antigravity) y el API Gateway del clúster (FastAPI).

## 4. Conclusion
El paradigma Agentic MLOps reduce drásticamente la curva de aprendizaje y el tiempo de despliegue para investigadores.
