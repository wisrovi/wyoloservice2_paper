# WPipe: A Declarative Pipeline Framework with Forensic Tracking for ML Workflows

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Abstract

ML training pipelines require observability, retry logic, and resource monitoring. We present WPipe, a lightweight declarative framework for single-node GPU workstations with forensic SQLite tracking, conditional branching, and checkpoint resume.

**Keywords:** Pipeline Framework, Declarative Pipelines, ML Orchestration, Forensic Tracking, Resource Monitoring, SQLite.

## 1. Introduction

Enterprise orchestrators provide observability but require Kubernetes. WPipe provides the same features in a single Python library with zero infrastructure dependencies.

## 2. Results

| Feature | Ad-Hoc | Airflow | WPipe |
|---|---|---|---|
| Lines of Code | 200+ | 150+ | 35 |
| Forensic Tracking | 0% | 100% | 100% |
| Retry Support | Manual | Yes | Yes |
| Checkpoint Resume | No | Yes | Yes |
| Startup Overhead | 0s | 14+ s | 0.2 s |

## 3. Conclusion

WPipe reduces authoring effort by 83%, provides 100% forensic coverage, and adds < 2% overhead. All 15 modules fully functional.

**Code:** https://github.com/wisrovi/wyoloservice2_production
**License:** PolyForm Noncommercial / AGPLv3
