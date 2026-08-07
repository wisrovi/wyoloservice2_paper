# Agentic MLOps: LLM-Driven Autonomous Orchestration of Distributed Vision Training Clusters using Model Context Protocol (MCP)

## Abstract
Traditional MLOps orchestration requires a high degree of infrastructure and configuration expertise (YAML/Bash). This work presents the integration of the *Model Context Protocol (MCP)* into a YOLO training cluster. We demonstrate how a Large Language Model (LLM) Agent can mount remote resources, perform shift-left dataset validation, generate dynamic configurations, and launch massive training sessions using exclusively natural language.

## 1. Introduction
Deploying computer vision models at scale requires complex tools that isolate Machine Learning researchers. We address this issue by equipping LLM agents with domain-specific MLOps tools via MCP, allowing them to operate the cluster autonomously.

## 2. Related Work
The intersection of LLM Agents and MLOps has gained recent traction.
- **ML-Agent: Reinforcing LLM Agents for Autonomous Machine Learning Engineering (2026):** Highlights RL-based training for agents to autonomously assume ML engineering roles.
- **AutoML-Agent: A Multi-Agent LLM Framework for Full-Pipeline AutoML (2024/2026):** Proposes specialized multi-agent systems to manage the complete ML lifecycle.
- **A Survey on AgentOps: Categorization, Challenges, and Future Directions (2025):** Discusses architectural and monitoring challenges in "AgentOps" workflows.

## 3. System Architecture
The `wyolo-mcp` server acts as a bridge between the LLM client (Claude, Antigravity) and the cluster's API Gateway (FastAPI).

## 4. Conclusion
The Agentic MLOps paradigm drastically reduces the learning curve and deployment time for researchers.
