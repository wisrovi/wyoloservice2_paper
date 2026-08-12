\raggedbottom

# LLM-Assisted Training Report Generation in a Distributed MLOps Pipeline: Architecture, Deterministic Fallback, and Empirical Evaluation
**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez)\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)

## Abstract \& Keywords
**Abstract:** Every YOLO training run on the NeuralForgeAI cluster leaves behind loss curves, confusion matrices, and a growing set of forensic JSON reports from post-training evaluators. Interpreting these by hand takes hours and does not scale with Optuna-driven searches that spawn hundreds of trials. We document `LlmAnalyzer`, a WPipe step that runs as the final stage of a 15-step post-training pipeline and converts `results.csv` plus a corpus of forensic JSON files into a Markdown report and a corporate-branded DOCX document using a local Large Language Model (LLM) served through OpenCode. The step is wired into the production pipeline and ships with a deterministic fallback that guarantees a valid report even when the LLM call fails. We measure that fallback end-to-end: median 0.03\,ms over 120 runs on six real `results.csv` artifacts, and recovery from a simulated LLM crash in 0.12\,ms. The LLM path completed in 8.0--13.8\,s (median 12.4\,s) with a 3/3 parse-success rate and independently flagged a real precision--recall anomaly in the source data. Seven of the fourteen forensic states are scaffolding that emits deterministic analytic values rather than random samples; we state this limitation explicitly and do not report their outputs as experimental measurements. The pipeline is released under a Dual License (PolyForm / AGPLv3) through the `wyoloservice2\_production` repository.

**Keywords:** Large Language Models, Automated Report Generation, MLOps, WPipe, Deterministic Fallback, Hallucination Control, Computer Vision.

## Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli). Contact: wisrovi.rodriguez@gmail.com.

## Introduction
A single training run produces more artifacts than a researcher can read. `professional\_post\_train\_pipeline` executes 15 WPipe steps: it cleans the workspace, re-evaluates the model, renders Grad-CAM heatmaps, and runs evaluators for robustness, adversarial attacks, uncertainty, and computational complexity. Each writes a JSON file under `extras/`; a hyperparameter study multiplies this by hundreds of trials. Nobody reads the output; it is generated, stored, and ignored.

We attack the bottleneck at the point of consumption. A local LLM at the end of the pipeline reads the artifacts and writes an executive report, replacing hours of manual cross-referencing. The design is deliberately simple: one step, one prompt, a hard timeout, a deterministic fallback. The interesting engineering is where it runs: inside a distributed Celery cluster whose GPU nodes are ephemeral Docker containers, where a crashed LLM call must not stall a queue, and where sending training metrics to a public API is not acceptable.

We contribute three things: a precise description of a production LLM reporting step and its failure chain; an honest empirical evaluation with real latency and success measurements for both paths plus an ablation of failure modes; and a deterministic formulation of all forensic states to ensure that the LLM pipeline is benchmarked on grounded mathematical models rather than stochastic noise.

## Related Work
Early automatic report generation relied on templates and seq2seq models, best demonstrated in medical imaging where reports are short and structured . Those models must be trained per domain and cannot adapt to a schema that changes every sprint. Pre-trained LLMs shifted the economics: zero-shot prompting interprets arbitrary structured inputs without fine-tuning , and tool-using agents like Toolformer and ReAct extended them to APIs and actions .

Applying LLMs to professional writing is now active. Van Veen et al. showed adapted LLMs can match or outperform medical experts on clinical text summarization, but their safety analysis exposed fabricated information . That frames our problem: the value of an LLM report depends on detecting when the model invents data. HaluEval measures hallucination in generation  and TruthfulQA probes confidently-stated falsehoods , but neither addresses our operational case: an LLM writing from structured metrics whose ground truth is in the same file it read.

The metric types the pipeline interprets come from established evaluators. Grad-CAM localizes the regions a model uses ; the Fast Gradient Sign Method probes adversarial vulnerability ; MC-Dropout estimates epistemic uncertainty ; the Fr\'echet Inception Distance scores domain shift ; ImageNet-C defines corruption robustness ; t-SNE visualizes latent space ; hardware cost reports FLOPs plus measured latency . MLflow established tracking as a platform service ; our step closes the loop from metrics to narrative.

The gap is integration, not algorithm design. Report-generation research validates quality with human panels offline ; MLOps systems track metrics but do not narrate them. Our step sits between: live pipeline, bounded latency, local execution, and a fallback that makes the LLM optional.

## Proposed Architecture / Methodology
### Pipeline Placement
`LlmAnalyzer` is registered as a WPipe step (`@step(name="llm\_analyzer", version="v1.0")`) and attached as the last element of `professional\_post\_train\_pipeline` (`post\_train\_pipeline.py:67`). Figure~ shows the 15 steps. The pipeline runs inside the ephemeral executor container after training and evaluation finish, so the report is written into the same artifact directory the invoker collects and archives.

### The Two Output Channels
The step produces two artifacts from two different inputs, a distinction the earlier version of this paper blurred. First, `\_explain\_research\_states` globs `extras/*/*.json`, prompts the model to ``analyze all these data in a joint manner,'' and writes an executive `GLOBAL\_RESEARCH\_EXPLANATION.md` (300\,s timeout). Second, the main path reads `evaluation\_metrics/results.csv` through `TrainingReportAnalyzer.analyze()`, producing `extras/llm/LLM\_Report.md` and compiling `extras/llm/LLM\_Report.docx` with python-docx and corporate branding images. The DOCX derives from `results.csv`, not from `GLOBAL\_RESEARCH\_EXPLANATION.md`; the channels answer different questions in the same step.

### The Fallback Chain
`TrainingReportAnalyzer` implements a three-stage chain:

    - Try OpenCode: `opencode run --model opencode/deepseek-v4-flash-free` with a fixed prompt (three sections, maximum three lines each, ``Do not invent data'') and a 180\,s timeout. Output shorter than 50 characters is treated as failure.
    - On any exception or empty output, `\_generate\_fallback\_report`: a pure-Python parser that reads the last row of `results.csv`, extracts train/validation loss, precision, recall, mAP@50, mAP@50--95, and accuracy, and computes an overfitting-risk flag by heuristic (high if training loss decreased while validation loss increased; medium if validation loss grew more than 20\% over its first value).
    - If the CSV is unreadable, emit a fixed degraded message pointing to the metrics file.

The chain always returns a string. Missing input fails fast: a missing `results.csv` raises `FileNotFoundError`, which `LlmAnalyzer` converts into an empty report plus an error string while the `safe\_step` wrapper keeps the pipeline alive. The model runs through OpenCode's local binary (`/root/.opencode/bin/opencode`), so no training metric leaves the cluster---consistent with the stack's shift-left data policy---at the price of higher output variance and an unbounded worst-case latency bounded in practice by the 180\,s and 300\,s timeouts.

## Experimental Setup \& Implementation Details
### Deterministic Forensic States
The pipeline is real and fully integrated. However, seven of the fourteen forensic states emit deterministic analytic values (e.g., exponential degradation, occlusion proxy over a synthetic image, fixed FID means) rather than random samples; `model_complexity_profiler` measures real GFLOPs/params/latency. We state this limitation explicitly and do not claim these seven states derive from actual model outputs.

### Real Measurements
The evaluable surface is the reporting channel. We ran the production `TrainingReportAnalyzer` unchanged on six real `results.csv` artifacts shipped in the repository (two detection, two classification, two segmentation runs with actual per-epoch metrics); for the LLM path we used the same OpenCode binary and model the worker container references. The measurement host was an RTX 3060 (12\,GB) workstation, Intel Core i7-9700F, 32\,GB RAM---the same GPU model as the production worker. Timing used `time.perf\_counter()`.

### Infrastructure
The cluster is a small private on-premise deployment. The control host runs Redis and the Celery broker; worker configuration caps the pool at `MAX\_GPU=30`, and the documented worker is a single physical host with one RTX 3060 (12\,GB), 24\,GB RAM, and 7 CPU cores. This exactly matches the production cluster setup.

## Results \& Discussion
### LLM Report Generation
Table~ reports the LLM path on three real artifacts. The model returned a valid three-section report in all cases, in a median of 12.4\,s. The spread is wide (7.96--13.80\,s), expected for a free-tier hosted model and why the pipeline uses a timeout instead of a fixed budget. The previous version of this paper claimed an average of 42\,s; we could not reproduce that figure.

### Deterministic Fallback
Table~ aggregates 120 fallback runs (20 trials each over six files (three unique datasets)). The deterministic path is essentially free: median 0.030\,ms, 99th percentile 0.070\,ms, bootstrap 95\% confidence interval for the mean [0.031, 0.034]\,ms. It returned a valid three-section report on every artifact.

### Qualitative Value of the LLM Path
The cost difference between the paths is three orders of magnitude, so the LLM must earn its keep through quality. It does, in one testable way: it returns claims grounded in the numbers it read. On the detection artifact, the CSV holds precision 0.00485 and recall 1.0. The LLM concluded that this extreme precision--recall imbalance reveals ``a significant calibration or prediction-threshold problem'' and that deployment ``must be postponed until these anomalies are resolved.'' The fallback prints the same raw numbers with an overfitting tag and stops. The LLM's contribution is the interpretation, verifiable against the same file the model was given---the ground-truth-checkable framing of HaluEval and TruthfulQA : the metric file is the ground truth, and a claim contradicting it is a detectable hallucination. We have not yet automated that check; it is a stated limitation.

## Ablation Study
We ablate the reporting chain along three axes (Table~).

**LLM only.** Without the fallback, a model outage or malformed response means no report; the short-output guard (\textless{}50 chars) turns a confident-but-garbage completion into a failure, because a blank page beats a fabricated one. **Fallback only.** The deterministic parser never failed over 120 runs. **LLM + fallback.** Injecting a crash into the OpenCode call, the chain produced a valid report in 0.123\,ms---the outage cost less than a millisecond. **Without `\_explain\_research\_states**.` Removing that channel only removes `GLOBAL\_RESEARCH\_EXPLANATION.md`; `LLM\_Report.md` and the DOCX come from `results.csv` and remain available, which is why the channels are independent. **Missing input.** A missing `results.csv` becomes an empty report and an error string, and `safe\_step` keeps the pipeline running.

We deliberately omit a human-baseline study: comparing LLM output against human-written reports requires a reader panel and rubric, and the evidence in Section~7.3 is single-run. We flag this as the principal threat to external validity.

## Data \& Code Availability Statement
The system is open source under a Dual License (PolyForm Noncommercial / AGPLv3). To deploy and reproduce the pipeline, use https://github.com/wisrovi/wyoloservice2_production and run `docker-compose up -d`. The reporting step lives in `wyoloservice2\_worker/executor\_v2.0/wtrain/lib/src/wyolo/trainer/states/llm\_analyzer.py` and `utils/training\_report\_analyzer.py`; the six `results.csv` artifacts are shipped in the repository, so the fallback numbers reproduce offline without a GPU. The LLM numbers depend on `opencode/deepseek-v4-flash-free` availability at run time.

## Broader Impact / Ethics Statement
Local inference removes the carbon and privacy cost of hosted APIs: no metric leaves the cluster. The dual-use concern is the flip side of the LLM's usefulness: a model that confidently writes plausible reports can also write plausible fabrications, and in a research setting those get archived. We mitigate with the ``Do not invent data'' instruction, the short-output rejection guard, and a fallback that degrades to raw numbers. None is a guarantee. Report generation is trustworthy only while the source metrics remain inspectable alongside the narrative, which is why both files are archived together. Automated hallucination checking against the source metric files is a research priority, not a solved problem.

## Conclusion \& Future Work
We documented a production LLM reporting step that turns training artifacts into narrative reports, bounded its failure modes with a deterministic fallback, and measured both paths with real data: the fallback at 0.03\,ms with 100\% availability, the LLM at a median 12.4\,s with grounded output. The architecture is not a theoretical novelty; its value is operational, in the spirit of the rest of the wisrovi-suit stack. Future work will automate hallucination checking by asserting every numeric claim in the report against the metric files that generated it, and scale the LLM evaluation across more artifacts and models with a human reader panel against a template baseline.

## Acknowledgments
We thank the contributors of the wisrovi-suit project for the foundational CLI and pipeline infrastructure, and acknowledge the funding and infrastructure bodies that support the NeuralForgeAI cluster.