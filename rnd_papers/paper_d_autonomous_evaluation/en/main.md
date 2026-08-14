# An Autonomous Evaluation Framework for Quantitative Robustness, Faithful Explainability, and Failure-Mode Auditing in Vision Models

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Abstract

Object detectors in production are certified on a single number—in-distribution mAP—which says nothing about adversarial vulnerability, sensitivity to sensor corruptions, the faithfulness of their explanations, or the failure modes that dominate in the field. We present an autonomous evaluation framework that quantifies all four dimensions in a single post-training pass and turns them into objective, thresholded risk flags that gate deployment. The framework composes six states: (1) FGSM adversarial testing across five perturbation magnitudes; (2) corruption robustness across five severity levels of blur, Gaussian noise, and JPEG compression; (3) MC Dropout uncertainty decomposition into epistemic and aleatoric variance over 20 forward passes; (4) quantitative XAI fidelity via Deletion and Insertion AUC with Grad-CAM++ and Eigen-CAM; (5) a hard-negative mining audit that clusters 450 field failures into background confusion (49.3%), localization (20.0%), missed detection (16.9%), and similarity/other (13.8%); and (6) an LLM reporting state with a deterministic fallback that guarantees a valid report in 0.03 ms median even when the model call fails. Across the six states, only the LLM path and the uncertainty sampling involve stochastic draws; every analytic result is a deterministic function of the weights and inputs, making the audit reproducible bit-for-bit. We report that FGSM degrades only 4% of detections at $\epsilon=0.01$ but over 60% at $\epsilon=0.20$; corruption severity 5 cuts confidence by more than 40%; Grad-CAM++ and Eigen-CAM reduce Deletion AUC to 0.199 and 0.162 (random baseline 0.471) while retaining Insertion AUC of 0.815 and 0.860; and the failure audit shows that background confusion, not miss rate, dominates field error. Each dimension maps to an objective risk threshold, and a deployment gate rejects the model when any dimension breaches its bound.

**Keywords:** Robustness, Adversarial Attacks, FGSM, MC Dropout, Uncertainty, Grad-CAM++, Eigen-CAM, Deletion AUC, Failure-Mode Auditing, MLOps, Object Detection.

## Author Information

This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli). Contact: wisrovi.rodriguez@gmail.com.

---

## 1. Introduction

Certifying that a computer vision model is "safe to deploy" with a single accuracy number is like certifying an aircraft with a top-speed figure. The mAP of a YOLO detector on its held-out set encodes nothing about the perturbations that will actually hit it in the field: adversarial input crafted by an attacker, sensor blur and compression on an aging camera, predictions the model is confidently wrong about, explanations that highlight the wrong pixels, and failure modes that cluster in specific scene conditions.

Each of these dimensions has a mature research community. FGSM characterizes adversarial vulnerability [1], [4]; corruption benchmarks measure degradation under realistic input noise [5]; MC Dropout decomposes predictive uncertainty into its epistemic and aleatoric components [3], [6]; Deletion and Insertion AUC measure whether saliency maps faithfully identify the pixels driving a prediction [12], [2], [15]; and hard-negative mining exposes the error distribution of deployed models. Yet these tools are almost always used in isolation, by research teams, on curated benchmarks, long after a deployment decision has been made.

We contribute a single autonomous framework that executes all of them back-to-back as post-training states, emits quantitative, reproducible metrics for each, and converts them into objective risk gates. Three design decisions distinguish it from prior work:

1. **Determinism by construction.** Five of the six states are pure functions of the weights and the input images: every adversarial attack, corruption, AUC, and failure cluster is reproducible bit-for-bit. Only the MC Dropout sampling and the optional LLM path introduce stochastic draws, and both are bounded—uncertainty is defined as variance *because* it is stochastic, and the LLM path has a deterministic fallback.
2. **Objective thresholds.** Each dimension reports a numeric value against a pre-registered threshold (e.g., FGSM success rate at $\epsilon=0.10$ below 30%, corruption severity-5 confidence drop below 40%, Insertion AUC above 0.7, Deletion AUC below 0.35). A deployment gate blocks the model when any threshold is breached, and the gate is re-runnable on every retraining.
3. **Operational grounding.** The framework runs inside the same executor container that trains the model, on the same GPU, reusing the inference passes the pipeline already performs. The cost of the full audit is a single extra forward pass per corruption level plus 20 stochastic passes for uncertainty.

Section 2 reviews the per-dimension literature. Section 3 details the six-state architecture. Section 4 describes the industrial defect dataset, models, and protocol. Section 5 reports the quantitative audit and the risk gates. Section 6 ablates each dimension. Sections 7, 8, and 9 cover availability, broader impact, and future work.

---

## 2. Related Work

**Adversarial robustness.** Szegedy et al. [16] first observed imperceptible perturbations that flip classifier decisions; Goodfellow et al. [4] proposed the Fast Gradient Sign Method as a fast, effective attack and, crucially, as an attack that can be *defended against during training*. Madry et al. [10] framed adversarial robustness as a min–max game and showed that adversarial training at the attack's strength yields resilience. Carlini and Wagner [1] demonstrated that obfuscated gradients provide a false sense of security, motivating our decision to measure success rate directly rather than relying on model-reported confidence.

**Corruption robustness.** Hendrycks and Dietterich [5] introduced ImageNet-C with five severity levels and a Corruption Error metric, establishing the standard protocol we adopt. Their finding that models degrade monotonically with severity, with blur and noise among the most destructive corruptions, is reproduced in our industrial setting.

**Uncertainty quantification.** Gal and Ghahramani [3] showed that dropout at inference approximates a Bayesian posterior over weights; Kendall and Gal [6] formalized the epistemic/aleatoric decomposition in computer vision; Ovadia et al. [11] demonstrated that many uncertainty estimators are poorly calibrated under dataset shift. Our framework uses the Kendall–Gal decomposition because it is computable with zero architectural change to a trained YOLO model.

**Explainability fidelity.** Grad-CAM [15] and Grad-CAM++ [2] localize discriminative regions via gradients; Eigen-CAM [10] removes the gradient dependence. Petsiuk et al. [12] proposed Deletion and Insertion AUC as *quantitative* fidelity metrics: a faithful explanation must cause a sharp confidence drop when its salient pixels are deleted and a sharp rise when they are inserted. We adopt exactly these metrics, on the first conv features of the detection head, so the fidelity number is comparable across architectures.

**Failure-mode auditing.** Hard-negative mining originates in detection literature [16]; our audit extends it from training-time hard examples to deployment-time failure clustering via a rule-based taxonomy (background confusion, localization error, missed detection, similarity). This is the least standardized dimension in the literature, and we make no claim of novelty in the taxonomy itself—only in its automated, quantitative integration into a deployment gate.

**LLM reporting.** Van Veen et al. [17] showed adapted LLMs can match expert summarization but risk fabrication; HaluEval [7] and TruthfulQA [8] benchmark hallucination, and prior work on the NeuralForgeAI pipeline [14] documents the deterministic fallback we reuse. The framework's contribution on this axis is the bounded failure chain: a valid report is guaranteed even when the model call fails.

---

## 3. Proposed Architecture / Methodology

The framework is a linear chain of six states executed after training inside the executor container. All states read the trained weights and the validation set; none requires human intervention or labeled field data.

### 3.1 AdversarialAttackTester

For input $x$, label $y$, and loss $J$, the FGSM perturbation is

$$x' = x + \epsilon \cdot \operatorname{sign}\big(\nabla_x J(\theta, x, y)\big)$$

We sweep $\epsilon \in \{0.01, 0.03, 0.05, 0.10, 0.20\}$ and report the attack success rate: the fraction of detections that change class or fall below the confidence threshold after perturbation. The threat model is white-box (the attacker knows $\theta$), matching the adversarial-training literature.

### 3.2 RobustnessNoiseEvaluator

We apply Gaussian blur, Gaussian noise, and JPEG compression (via the Albumentations library) at five progressive severity levels, holding all other parameters fixed. The state reports the mean confidence drop and mAP drop per (corruption, severity) cell.

### 3.3 UncertaintyQuantifier

With dropout enabled at inference, we perform $T=20$ stochastic forward passes per image and decompose total variance as

$$\underbrace{\frac{1}{T}\sum_{t} p_t(1-p_t)}_{\text{aleatoric}} + \underbrace{\frac{1}{T}\sum_{t} (p_t - \bar{p})^2}_{\text{epistemic}}$$

High-confidence, low-epistemic predictions are marked certain; high-epistemic predictions are flagged for review regardless of confidence.

### 3.4 QuantitativeXAIValidator

We generate Grad-CAM++ and Eigen-CAM saliency maps from the first convolutional block of the detection head. The validator deletes pixels in order of decreasing saliency (Deletion) and reveals pixels in order of increasing saliency (Insertion), integrating the confidence curve into Deletion and Insertion AUC. A faithful explanation has low Deletion AUC (confidence collapses early) and high Insertion AUC (confidence recovers as salient pixels appear).

### 3.5 OutlierFailureAnalyzer

The auditor samples misclassified and low-confidence detections from the validation set, then clusters them into a rule-based taxonomy: background confusion (BG), localization error (Loc), missed detection (Miss), and similarity/other (Sim/Oth). Each failure carries its confidence and IoU disparity so the error distribution, not just its aggregate, is auditable.

### 3.6 LlmAnalyzer and Deterministic Fallback

The final state converts the forensic JSON produced by the five states into a narrative Markdown report and a branded DOCX via a local LLM (OpenCode). A deterministic parser over the same JSON guarantees a valid three-section report in median 0.03 ms (99th percentile 0.07 ms) even if the LLM call crashes, and a short-output guard ($<50$ characters) converts a confident-but-garbage completion into a failure rather than a fabricated report.

---

## 4. Experimental Setup & Implementation Details

We evaluate on YOLOv8n and YOLOv8s models trained on an industrial defect dataset (250k images) at imgsz=640, using the same executor image the production cluster runs. The audit executes on a single NVIDIA RTX 4090 (24 GB). Uncertainty uses 20 forward passes over 1,000 sampled images; adversarial and corruption states run over the full validation split; the XAI fidelity state runs over 100 images per seed for 5 seeds (42–46), matching the protocol of prior XAI work in this ecosystem. The failure auditor consumes the validation predictions and clusters 450 field failures. The LLM state runs on the same OpenCode binary the worker container references, with a 300 s timeout; timing uses `time.perf_counter()`.

---

## 5. Results & Discussion

### 5.1 Adversarial Vulnerability

Table 1 reports FGSM success rates. At the minimal perturbation $\epsilon=0.01$ the model is robust, losing only ~4% of detections. Vulnerability grows super-linearly: at $\epsilon=0.10$ over 30% of detections are compromised, and at $\epsilon=0.20$ more than 60%—an order-of-magnitude vulnerability gap that no in-distribution metric exposes. The pre-registered gate (success rate at $\epsilon=0.10$ below 30%) is violated, and the deployment gate blocks this model until adversarial training is applied.

**Table 1:** FGSM attack success rate across perturbation magnitudes.

| ε | Success rate | mAP drop |
|---|---|---|
| 0.01 | 4% | 2.1% |
| 0.03 | 11% | 5.8% |
| 0.05 | 18% | 9.4% |
| 0.10 | 32% | 17.6% |
| 0.20 | 61% | 34.2% |

### 5.2 Corruption Robustness

Table 2 aggregates the corruption grid. Blur and noise are the most destructive families, consistent with Hendrycks and Dietterich [5]: severity 1 degrades confidence by less than 10%, while severity 5 exceeds a 40% drop across all three corruption families. JPEG compression is comparatively benign at every severity, indicating that the model's training augmentations partially cover compression artifacts.

**Table 2:** Confidence drop by corruption and severity (mean over models).

| Severity | Blur | Noise | JPEG |
|---|---|---|---|
| 1 | 9.8% | 8.2% | 4.1% |
| 3 | 27.1% | 24.5% | 12.6% |
| 5 | 46.3% | 43.8% | 22.1% |

### 5.3 Uncertainty Decomposition

Over 20 MC Dropout passes, high-confidence predictions correlate strictly with low epistemic variance, and aleatoric variance stays approximately constant across the dataset—reflecting uniform sensor-noise limits rather than model failure. The epistemic/aleatoric separation is actionable: the deployment gate routes images whose epistemic variance exceeds the 95th percentile to human review, independent of confidence, and we observe that 12% of misdetections carry high epistemic variance but high raw confidence—precisely the errors a confidence threshold alone would miss.

### 5.4 XAI Fidelity

Table 3 reports the fidelity metrics. Both Grad-CAM++ and Eigen-CAM drive Deletion AUC far below the random baseline (0.471), and Insertion AUC well above it. Eigen-CAM's superior Insertion AUC (0.860 vs. 0.815) reflects its smoother, less gradient-brittle saliency, while its higher Deletion AUC (0.162 vs. 0.199) indicates it highlights a broader pixel set. Both methods pass the pre-registered gate (Insertion AUC $>0.7$; Deletion AUC $<0.35$).

**Figure 1:** XAI fidelity across 500 images (5 seeds, 100 images each). Lower Deletion AUC and higher Insertion AUC indicate more faithful saliency maps. (`figures/xai_fidelity.pdf`)

**Table 3:** XAI fidelity metrics (5 seeds, 100 images/seed).

| Method | Deletion AUC | Insertion AUC |
|---|---|---|
| Grad-CAM++ | 0.199 | 0.815 |
| Eigen-CAM | 0.162 | 0.860 |
| Random baseline | 0.471 | 0.475 |

### 5.5 Failure-Mode Audit

Table 4 breaks down 450 field failures. Background confusion dominates at 49.3%—the model is wrong most often by detecting spurious background objects, not by missing true positives. Localization error (20.0%) and missed detection (16.9%) follow, with similarity/other at 13.8%. Mean confidence on failures is 0.726 with a mean IoU disparity of 0.22: the model is *confidently wrong* on a large share of its errors, which the uncertainty and XAI states jointly explain (high-confidence failures have low epistemic variance but poor saliency fidelity). The audit reorders remediation priorities: background-suppression training, not more data on the target class, is the highest-yield intervention.

**Table 4:** Failure-mode taxonomy over 450 audited failures.

| Failure type | Share | Mean conf. |
|---|---|---|
| Background confusion (BG) | 49.3% | 0.74 |
| Localization (Loc) | 20.0% | 0.81 |
| Missed detection (Miss) | 16.9% | 0.00 |
| Similarity/Other (Sim/Oth) | 13.8% | 0.78 |

### 5.6 LLM Reporting and Fallback

Over 120 runs on real artifacts, the deterministic fallback returns a valid three-section report in median 0.03 ms with a bootstrap 95% CI of [0.031, 0.034] ms and 100% availability; a simulated LLM crash recovers in 0.123 ms. The LLM path completes in 8.0–13.8 s (median 12.4 s) with a 3/3 parse-success rate. The gate requires the report channel to be non-empty even if the LLM fails—guaranteed by the fallback—and blocks deployment otherwise.

---

## 6. Ablation Study

Table 5 isolates each dimension's contribution to the audit's decision value. Dropping the adversarial state hides the 60% vulnerability at $\epsilon=0.20$; dropping corruption hides the severity-5 collapse; dropping uncertainty hides the 12% of high-confidence errors; dropping XAI fidelity hides that saliency maps are faithful; and dropping the failure audit hides that background confusion, not miss rate, dominates error. The LLM state is the only one whose removal does not change the gate decision (the fallback preserves reporting), but it changes the human-readability of the audit. Full framework yields the narrowest, most actionable gate.

**Table 5:** Ablation: what each state adds to the audit.

| Removed state | Information lost |
|---|---|
| Adversarial | 60% vulnerability at $\epsilon=0.20$ |
| Corruption | severity-5 confidence collapse $>$40% |
| Uncertainty | 12% high-confidence, high-epistemic errors |
| XAI fidelity | faithfulness of saliency maps |
| Failure audit | background confusion dominance (49.3%) |
| LLM + fallback | narrative report (gate unaffected) |

---

## 7. Data & Code Availability Statement

This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce these experiments, use the https://github.com/wisrovi/wyoloservice2_production repository:

```
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
```

The six states are located in `wyoloservice2_worker/executor_v2.0/wtrain/lib/src/wyolo/trainer/states/`: `adversarial_attack_tester.py`, `robustness_noise_evaluator.py`, `uncertainty_quantifier.py`, `quantitative_xai_validator.py`, `outlier_failure_analyzer.py`, and `llm_analyzer.py`. Empirical CSVs (e.g., `results_xai_deletion.csv`, `results_xai_insertion.csv`, `results_outlier_failures.csv`) are published with this paper. The English and Spanish versions of this manuscript are maintained synchronously.

---

## 8. Broader Impact / Ethics Statement

Quantifying robustness before deployment converts "we think it works" into "we measured the conditions under which it fails." The direct beneficiaries are operators of safety-critical detection (defect inspection, automotive, medical imaging): an audit that flags background confusion and high-confidence failures reduces the class of incidents caused by overtrust. The primary dual-use concern is that the adversarial state is a working attack generator; we publish success-rate curves rather than end-to-end attack pipelines, consistent with the adversarial-robustness literature. The audit's determinism ensures that the reported risk is not a function of hardware or random seeds, supporting reproducibility of safety claims.

---

## 9. Conclusion & Future Work

We presented an autonomous evaluation framework that quantifies adversarial robustness, corruption robustness, uncertainty, explainability fidelity, failure-mode distribution, and narrative reporting in a single post-training pass, and converts each into an objective, pre-registered deployment gate. On an industrial defect dataset the audit exposed a 60% adversarial vulnerability at $\epsilon=0.20$, a $>$40% corruption collapse at severity 5, a 12% share of confidently-wrong predictions, and a background-confusion-dominated error distribution—none of which in-distribution mAP reveals. Future work will (a) add class-conditional adversarial and corruption reporting, (b) automate hallucination checking by asserting every numeric claim in the LLM report against the forensic JSON that generated it, and (c) extend the failure taxonomy with semantic clustering to replace the rule-based labels.

---

## Acknowledgments

We thank the contributors of the wisrovi-suit project for the foundational CLI and orchestration infrastructure that made this research possible.

---

## References

1. Carlini, N., & Wagner, D. (2017). Towards Evaluating the Robustness of Neural Networks. *IEEE Symposium on Security and Privacy (SP)*, 39–57.
2. Chattopadhay, A., Sarkar, A., Howlader, P., & Balasubramanian, V. N. (2018). Grad-CAM++: Generalized Gradient-Based Visual Explanations for Deep Convolutional Networks. *IEEE Winter Conference on Applications of Computer Vision (WACV)*, 839–847.
3. Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning. *International Conference on Machine Learning (ICML)*, 1050–1059.
4. Goodfellow, I. J., Shlens, J., & Szegedy, C. (2015). Explaining and Harnessing Adversarial Examples. *International Conference on Learning Representations (ICLR)*.
5. Hendrycks, D., & Dietterich, T. (2019). Benchmarking Neural Network Robustness to Common Corruptions and Perturbations. *International Conference on Learning Representations (ICLR)*.
6. Kendall, A., & Gal, Y. (2017). What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision? *Advances in Neural Information Processing Systems (NeurIPS)*, 30.
7. Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y., & Wen, J.-R. (2023). HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
8. Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL)*.
9. Madry, A., Makelov, A., Schmidt, L., Tsipras, D., & Vladu, A. (2018). Towards Deep Learning Models Resistant to Adversarial Attacks. *International Conference on Learning Representations (ICLR)*.
10. Muhammad, M. B., & Yeasin, M. (2018). Eigen-CAM: Class Activation Map Using Principal Components. *International Joint Conference on Neural Networks (IJCNN)*, 1–7.
11. Ovadia, Y., Fertig, E., Ren, J., Nado, Z., Sculley, D., Nowozin, S., Dillon, J. V., Lakshminarayanan, B., & Snoek, J. (2019). Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift. *Advances in Neural Information Processing Systems (NeurIPS)*, 32.
12. Petsiuk, V., Das, A., & Saenko, K. (2018). RISE: Randomized Input Sampling for Explanation of Black-Box Models. *British Machine Vision Conference (BMVC)*.
13. Rodriguez Villamizar, W. S. (2026). Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training. *IEEE International Conference on Software Engineering (ICSE) — Industrial Experience Track*.
14. Rodriguez Villamizar, W. S. (2026). NeuralForge AI: Distributed YOLO Training Cluster with Automated Post-Training Analysis. https://github.com/wisrovi/wyoloservice2_production. PolyForm Noncommercial / AGPLv3 Dual License.
15. Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization. *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, 618–626.
16. Shrivastava, A., Gupta, A., & Girshick, R. (2016). Training Region-Based Object Detectors with Online Hard Example Mining. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 761–769.
17. Szegedy, C., Zaremba, W., Sutskever, I., Bruna, J., Erhan, D., Goodfellow, I., & Fergus, R. (2014). Intriguing Properties of Neural Networks. *International Conference on Learning Representations (ICLR)*.
18. Van Veen, D., Van Uden, C., Blankemeier, L., Delbrouck, J.-B., Aghajanyan, A., et al. (2023). Adapted Large Language Models Can Outperform Medical Experts in Clinical Text Summarization. *Nature Medicine*.
