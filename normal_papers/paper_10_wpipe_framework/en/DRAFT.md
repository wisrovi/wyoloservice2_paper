# Paper 10: WPipe — A Declarative Pipeline Framework with Forensic Tracking for ML Workflows

**Category:** Standard Papers (MLOps Engineering)  
**Status:** DRAFT  
**Target Venue:** ICSE / ESEC/FSE / OOPSLA

---

## 🎯 Core Idea

This paper presents **WPipe**, a custom-built pipeline framework designed specifically for ML workflows that require:
1. **Declarative step definition** via `@step` decorator
2. **Forensic tracking** of every execution in SQLite
3. **Resource monitoring** (RAM/CPU) during execution
4. **Conditional branching** within pipelines
5. **Retry with configurable backoff**

### Key Contribution
A **lightweight, ML-focused pipeline framework** that provides the observability of enterprise tools (Airflow, Kubeflow) without the overhead — designed for single-node GPU workstations.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    WPipe Core                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Pipeline                                        │  │
│  │  ├── set_steps([step1, step2, ...])              │  │
│  │  ├── add_error_capture([error_handler])          │  │
│  │  └── run(initial_data) → results                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  @step decorator                                 │  │
│  │  ├── name: str                                   │  │
│  │  ├── version: str                                │  │
│  │  ├── tags: list[str]                             │  │
│  │  └── @to_obj(Model) — Pydantic validation        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Forensic Tracking (SQLite)                      │  │
│  │  ├── StepExecution: id, name, version, status    │  │
│  │  ├── ResourceMetrics: ram_peak, cpu_avg, time    │  │
│  │  └── ErrorCapture: stack_trace, input_data       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Conditional Logic                               │  │
│  │  └── Condition(expression, branch_true, branch_false) │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔬 Modules (15 total)

| Module | File | Description |
|--------|------|-------------|
| Pipeline | `pipe.py` | Core pipeline orchestration |
| AsyncPipeline | `pipe_async.py` | Async version for I/O-bound tasks |
| Step Decorator | `decorators/step.py` | `@step` with metadata |
| Type Validators | `type_hinting/validators.py` | Pydantic validation |
| CheckpointManager | `checkpoint/checkpoint.py` | State persistence |
| ParallelExecutor | `parallel/executor.py` | ThreadPool/ProcessPool |
| ResourceMonitor | `resource_monitor/monitor.py` | RAM/CPU tracking |
| ProgressManager | `components/progress.py` | Progress bars |
| AlertManager | `tracking/alerts.py` | Alert system |
| AnalysisManager | `tracking/analysis.py` | Metrics analysis |
| QueryManager | `tracking/queries.py` | SQL queries on events |
| TimeoutManager | `timeout/timeout.py` | Task timeouts |
| Dashboard | `dashboard/main.py` | Web UI for monitoring |
| ExportManager | `export/exporter.py` | Multi-format export |
| APIClient | `api_client/api_client.py` | HTTP communication |

---

## 📊 Expected Figures

1. **Pipeline Execution Flow** — Mermaid diagram of step execution
2. **Forensic Tracking Schema** — ER diagram of SQLite tables
3. **Resource Monitoring Dashboard** — Screenshot of web UI
4. **Comparison Table** — WPipe vs. Airflow vs. Kubeflight vs. Prefect

---

## 📚 Key References

- Apache Airflow (2014) — Workflow orchestration
- Kubeflow Pipelines (2019) — ML workflows on Kubernetes
- Prefect (2018) — Modern workflow orchestration
- Dagster (2019) — Data asset orchestration

---

## 🛠️ Implementation Status

| Module | Status |
|--------|--------|
| Pipeline (pipe.py) | ✅ **FUNCIONAL** |
| AsyncPipeline (pipe_async.py) | ✅ **FUNCIONAL** |
| @step decorator | ✅ **FUNCIONAL** |
| Type Validators | ✅ **FUNCIONAL** |
| CheckpointManager | ✅ **FUNCIONAL** |
| ParallelExecutor | ✅ **FUNCIONAL** |
| ResourceMonitor | ✅ **FUNCIONAL** |
| ProgressManager | ✅ **FUNCIONAL** |
| AlertManager | ✅ **FUNCIONAL** |
| AnalysisManager | ✅ **FUNCIONAL** |
| QueryManager | ✅ **FUNCIONAL** |
| TimeoutManager | ✅ **FUNCIONAL** |
| Dashboard | ✅ **FUNCIONAL** |
| ExportManager | ✅ **FUNCIONAL** |
| APIClient | ✅ **FUNCIONAL** |

**Status:** All 15 modules are **fully implemented and functional**.

---

## 📝 Notes

- WPipe is embedded directly in the executor (`_wpipe/` directory)
- The framework uses SQLite for forensic tracking (no external DB required)
- ResourceMonitor tracks peak RAM and average CPU in real-time
- Dashboard provides a web UI for monitoring pipeline execution
- The `@step` decorator automatically captures metadata (name, version, tags)
- Conditional branching is supported via the `Condition` class
