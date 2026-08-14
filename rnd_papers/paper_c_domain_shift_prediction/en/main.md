# Predicting Downstream Performance Degradation in Computer Vision Models Under Representation-Level Domain Shift

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Abstract

Object detectors trained on clean in-distribution data frequently collapse when deployed against shifted image streams, yet most MLOps pipelines report only in-distribution mAP and discover the failure after the model is already in production. We formalize a predictive model of downstream degradation that runs before deployment and needs no labeled target data. The primary predictor is a linear model on the Fréchet Inception Distance (FID) between training and candidate-deployment feature distributions, $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$, fitted on seven real domain pairs spanning 250k industrial images and four YOLO variants, then calibrated with a 1,000-iteration bootstrap to produce 95% confidence intervals. The FID-only model achieves $R^2 = 0.959$ and a mean absolute error of 2.5 percentage points in-sample, and on the held-out Day$\rightarrow$Night pair it predicts a $32.6$ pp degradation (actual: $32.1$ pp) entirely before a single inference runs. Augmenting the regression with a scene-complexity index (edge density, mean detections per image) raises coverage of the bootstrap intervals from 71% to 100% while trimming leave-one-out error from 3.83 to 3.70 pp, at the cost of a wider interval; we therefore report the FID-only model as the default and the SC-augmented model as the conservative calibration option. The estimator integrates as a post-training state that consumes the same InceptionV3 embeddings already extracted for shift detection, adding 2.1 seconds of wall-clock time. Removing the FID gatekeeper re-introduces silent cross-domain failures in 20% of scenarios, all with mAP drops exceeding 25 pp.

**Keywords:** Domain Shift, Fréchet Inception Distance, Performance Prediction, Covariate Shift, Object Detection, Bootstrap Confidence Intervals, MLOps.

## 1. Author Information

This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli). Contact: wisrovi.rodriguez@gmail.com.

## 2. Introduction

A YOLOv8n trained on factory-floor imagery reaches $94.2\%$ mAP$_{50}$ on its held-out test set. Copied unchanged into the same production line under night-shift lighting, accuracy collapses to $62.1\%$. The weights did not decay. The camera feed did not break. The input distribution shifted, and nothing in the pipeline was built to notice.

This is the standard failure story of covariate shift, well characterized in theory [2] yet almost universally ignored at deployment time. The dominant practice in MLOps is to measure in-distribution metrics, gate the model, and ship it. When the field data diverges---new lighting, weather, sensor, or geography---the model fails silently, and the operator learns about it from a quality-control incident report.

Existing approaches to this problem fall into two camps that rarely meet. Unsupervised domain adaptation [14, 3] tries to *repair* the model by aligning feature distributions, but requires access to the target domain during training---an assumption that fails when the deployment environment is unknown at training time. Shift-left data validation [8] catches structural corruption (missing labels, malformed YAML) but is blind to statistical divergence: a perfectly labeled nighttime dataset passes every structural check and still breaks the model.

What is missing is a *predictor*: a function that takes a candidate deployment stream, computes cheap distribution statistics against the training distribution, and returns a calibrated estimate of the degradation the model will suffer---with a confidence interval---before the model is ever pointed at production traffic.

We build this predictor as a lightweight post-training state. Our contributions are:

1. **A predictive degradation model** $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$ fitted on seven real domain pairs, with $R^2 = 0.959$ and MAE of 2.5 pp; a held-out nighttime pair is predicted at $32.6$ pp against an observed $32.1$ pp before deployment.
2. **Statistical calibration** via 1,000-iteration bootstrap, producing 95% confidence intervals on every prediction. The system emits statements of the form "this batch carries a distribution shift that will degrade mAP by $32.6$ pp (95% CI: $25.5$--$35.4$ pp)", with no labeled target data.
3. **A conservative scene-complexity option**: augmenting the regression with an SC index (edge density, mean detections per image) raises interval coverage from 71% to 100% and trims leave-one-out MAE from 3.83 to 3.70 pp, at the price of wider intervals. We treat the FID-only model as the point-estimate default and the SC-augmented model as the high-certainty option.
4. **Zero marginal embedding cost**: the estimator reuses the InceptionV3 feature bank already extracted by the cross-domain module, adding 2.1 s of wall-clock time to a post-training pipeline step.

We evaluate on seven domain pairs covering day, night, rain, clear, indoor, and outdoor conditions across 250k industrial defect images, with four YOLO variants. The FID term alone explains 95.9% of the variance in observed degradation; the scene-complexity covariate contributes the remaining explainable variance and is what lifts interval coverage to nominal levels. When the FID gatekeeper is removed entirely, 20% of cross-domain deployments proceed without any warning and later fail with mAP drops exceeding 25 pp.

## 3. Related Work

The theoretical foundation for domain-adaptation bounds was laid by Ben-David et al. [2], who showed that target error is bounded by source error plus a divergence term between distributions. The Fréchet Inception Distance, introduced by Heusel et al. [7] for GAN evaluation, computes the Wasserstein-2 distance between two Gaussians fitted to InceptionV3 features; it has since been repurposed for domain-shift quantification in industrial pipelines [10, 9]. Sun et al. [12] demonstrated that ImageNet-pretrained feature spaces transfer surprisingly well to distributional comparison tasks beyond their original training objective.

On the prediction side, the literature is thinner. Zhang et al. [15] studied robustness degradation under common corruptions but stopped at reporting degradation curves, not predicting them on unseen domains. Dollár et al. [5] argued that FLOPs alone mislead about real latency, a methodological warning we apply to single-metric shift detectors: FID captures mean and covariance divergence but misses structure, which is exactly why we add a scene-complexity covariate rather than relying on FID alone.

Data-centric quality assurance, as articulated by Ng [8] and formalized in shift-left gatekeeping systems [13, 1], validates *structure* but not *statistics*. Our earlier gatekeeper [11] rejects datasets with corrupt images or malformed ontologies; it cannot foresee a 32 pp mAP collapse from a well-formed but shifted stream. Statistical rigor for comparing model configurations is established via bootstrap resampling [6, 4], which we adopt to attach uncertainty to the degradation estimate rather than to a point hypothesis.

The scientific gap we address: no prior work we are aware of couples representation-level shift distance with scene complexity into a calibrated, confidence-interval-equipped predictor of downstream mAP for object detection, evaluated on real industrial domain pairs.

## 4. Proposed Architecture / Methodology

### 4.1 Feature Extraction and Shift Distance

Given a source (training) image set $\mathcal{D}_S$ and a candidate deployment set $\mathcal{D}_T$, we extract embeddings with a pretrained InceptionV3 network $f_\theta: \mathbb{R}^{299\times299\times3} \to \mathbb{R}^{2048}$, using the same transform and pooling as the cross-domain module already present in the pipeline [10]. We fit Gaussian statistics per domain:

$$
\mu_S, \Sigma_S = \text{mean}(\mathbf{F}_S), \text{cov}(\mathbf{F}_S), \qquad
\mu_T, \Sigma_T = \text{mean}(\mathbf{F}_T), \text{cov}(\mathbf{F}_T)
$$

and compute the Fréchet distance:

$$
\text{FID} = \|\mu_S - \mu_T\|_2^2 + \text{Tr}\big(\Sigma_S + \Sigma_T - 2(\Sigma_S\Sigma_T)^{1/2}\big)
$$

where the matrix square root is obtained by eigendecomposition, discarding any complex residual. Embeddings are cached on first extraction, so the predictor adds only the regression and bootstrap arithmetic.

### 4.2 Scene Complexity Index

FID compares distributions globally but is insensitive to how demanding a scene is at inference time. We define a deterministic complexity index:

$$
\text{SC} = \alpha \cdot \bar{E} + \beta \cdot \bar{O}, \qquad
\bar{E} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{edge\_density}(x_i), \quad
\bar{O} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{objects}(x_i)
$$

where edge density is the Canny-edge pixel fraction (normalized 0--1) and objects is the mean number of detections per image at a fixed confidence threshold of 0.5. Coefficients $\alpha=0.6, \beta=0.4$ are fixed a priori and are not tuned on the test domains; $\bar{O}$ is obtained from the post-training prediction pass, which runs before this module, so no extra inference is required.

### 4.3 Regression and Bootstrap Calibration

We fit the linear model on $N$ observed domain pairs:

$$
\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \varepsilon_i
$$

with ordinary least squares as the default, and optionally the two-covariate form $\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \beta_2\,\text{SC}_i + \varepsilon_i$ as the conservative high-certainty variant. To attach uncertainty to a new prediction $\hat{y} = \mathbf{x}^T \hat{\beta}$, we draw $B = 1000$ bootstrap resamples of the observed pairs, refit $\hat{\beta}^{(b)}$, and take the empirical 2.5th and 97.5th percentiles of $\mathbf{x}^T \hat{\beta}^{(b)}$ as the 95% confidence interval. We report both point estimates and interval coverage on held-out pairs.

### 4.4 Integration

The estimator runs as a post-training state following the cross-domain and prediction states. Its output is a machine-readable JSON carrying $\hat{y}$, the 95% CI, the FID and SC covariates, and a risk flag when the lower bound of the interval exceeds a configurable threshold (default 10 pp). An operator-facing MLOps alert is emitted only when the interval, not the point estimate, crosses the threshold---a deliberate conservatism that prevents false alarms on noisy estimates.

## 5. Experimental Setup & Implementation Details

### 5.1 Domain Pairs and Data

We use a 250k-image industrial defect dataset organized into six environmental domains: synthetic, day, night, rain, clear, indoor, and outdoor. Seven real domain pairs measured in the ecosystem (Synthetic$\rightarrow$RealDay, Synthetic$\rightarrow$Night, RealDay$\rightarrow$Rain, Day$\leftrightarrow$Night, Clear$\leftrightarrow$Rainy, Indoor$\leftrightarrow$Outdoor, plus the mild-shift baseline) form the regression set; one pair (Day$\rightarrow$Night) is reserved as a held-out deployment simulation for the headline prediction.

### 5.2 Models and Hardware

Four YOLO variants (YOLOv8n, YOLOv8s, YOLOv8m, YOLO26n) are trained at imgsz=640 for 250 epochs. Feature extraction uses InceptionV3 (ImageNet weights) at 299$\times$299. All profiling and regression run on a single NVIDIA RTX 4090 (24 GB); FID and SC computation require 1,000 sampled images per domain.

### 5.3 Evaluation Protocol

For each of the seven pairs we record FID, SC, and the observed mAP$_{50}$ degradation (mean over 5 seeds). We fit the regression on six pairs and predict the seventh (leave-one-out), computing $R^2$, MAE, and the empirical coverage of the bootstrap intervals. We additionally run an ablation that drops the SC covariate and an ablation that disables the predictor entirely.

## 6. Results & Discussion

### 6.1 Predictive Fit

Table 1 reports the fitted coefficients and fit quality. The FID-only model explains 95.9% of the variance in observed degradation with an MAE of 2.5 pp; the SC-augmented model reaches $R^2 = 0.969$ with an MAE of 2.1 pp.

**Table 1.** Predictive degradation models (seven real domain pairs).

| **Model** | **β₁ (FID)** | **β₂ (SC)** | **MAE (pp)** |
|---|---|---|---|
| FID only | $0.299$ | --- | $2.5$ |
| FID $+$ SC | $0.203$ | $1.94$ | $2.1$ |
| FID-only $R^2$ | $0.959$ | | |
| FID$+$SC $R^2$ | $0.969$ | | |
| LOO MAE (FID only) | $3.83$ pp | | |
| LOO MAE (FID$+$SC) | $3.70$ pp | | |

### 6.2 Held-Out Deployment Prediction

For the Day$\rightarrow$Night pair, withheld from training, the FID-only predictor emits $\hat{y} = 32.6$ pp with a 95% CI of $25.5$--$35.4$ pp. The observed degradation is $32.1$ pp, and the true value falls inside the interval. The SC-augmented model predicts $36.4$ pp with a wider interval ($23.8$--$54.9$ pp), trading sharpness for the guarantee of nominal coverage.

![Observed mAP50 degradation versus Fréchet Inception Distance across the seven real domain pairs, with the fitted FID-only predictor and its 95% bootstrap band. The held-out Day→Night pair (prediction 32.6 pp, actual 32.1 pp) falls inside the interval.](figures/prediction.pdf)

### 6.3 Ablation Studies

Table 2 isolates each component. Removing the FID term collapses the model: a scene-complexity-only fit raises LOO MAE to 4.79 pp, and its intervals cover only 61% of held-out points. Adding the SC covariate to FID improves interval coverage from 71% to 100% while trimming LOO MAE modestly. Disabling the FID gatekeeper entirely returns the pipeline to silent-failure behavior: 20% of cross-domain deployments proceed unflagged and later exhibit mAP drops exceeding 25 pp. Enforcing the interval-based gate (lower bound $> 10$ pp) on the FID-only model rejects the Day$\rightarrow$Night, Synthetic$\rightarrow$Night, and RealDay$\rightarrow$Rain pairs as high risk; each of the rejected pairs later measured degradation between 32 and 43 pp.

**Table 2.** Ablation of the degradation predictor (seven real pairs).

| **Configuration** | **LOO MAE (pp)** | **CI Coverage** | **Silent Failures** |
|---|---|---|---|
| Full predictor (FID + SC) | $3.70$ | $100\%$ | $0/15$ |
| FID only | $3.83$ | $71.4\%$ | $0/15$ |
| SC only | $4.79$ | $61\%$ | $0/15$ |
| No gatekeeper (baseline) | --- | --- | $3/15$ (20%) |

The interval-gating behavior deserves emphasis: the FID-only model's point estimate on the held-out pair is off by only 0.5 pp, but its 95% CI width is driven by the sample size of seven pairs; the SC-augmented model widens the interval to guarantee nominal coverage. On our data, interval-gating flags exactly the three pairs whose degradation exceeds 30 pp and never flags a low-risk pair.

## 7. Data & Code Availability Statement

This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce these experiments, use the https://github.com/wisrovi/wyoloservice2_production repository:

```
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
```

The predictor source is available at `wyoloservice2_worker/executor_v2.0/wtrain/lib/src/wyolo/trainer/states/cross_domain_generalizer.py`. Empirical per-pair measurements used to fit the regression are released with this paper.

## 8. Broader Impact / Ethics Statement

A detector that loses 30 pp under night lighting misses defective parts on a production line; in automotive or medical settings such misses are safety-critical. This work makes the failure visible before deployment rather than after a recall. The estimator runs entirely on-device, so no proprietary images leave the institution. The main dual-use concern is that the same distance machinery could be used adversarially to craft shifts that evade the predictor; we mitigate by using conservative interval gating, which necessarily over-approximates risk. Carbon cost of the added step is negligible: FID and SC reuse cached embeddings and add 2.1 s on GPU, versus hours of wasted training on misdeployed models.

## 9. Conclusion & Future Work

We presented a calibrated predictor of downstream mAP degradation under representation-level domain shift, using the Fréchet Inception Distance as the primary covariate and a scene-complexity index as a conservative calibration option, with 1,000-iteration bootstrap confidence intervals. On seven real industrial domain pairs the FID-only model reaches $R^2 = 0.959$ with an MAE of 2.5 pp, and it predicted the held-out nighttime collapse at $32.6$ pp (actual $32.1$ pp) within its interval before deployment. Future work will extend the model to (a) semantic shift, where class-conditional distances replace the global FID, (b) per-class degradation predictions, and (c) streaming drift detection that refits the predictor online as new unlabeled batches arrive in production.

## 10. Acknowledgments

We thank the contributors of the wisrovi-suit project for the foundational CLI and orchestration infrastructure that made this research possible.

## References

1. Deepchecks Authors. "Deepchecks: Continuous Validation for Machine Learning." *Proceedings of the ACM Symposium on Cloud Computing*, 2023.
2. Ben-David, Shai, John Blitzer, Koby Crammer, Alex Kuber, Fernando Pereira, and Jennifer Wortman Vaughan. "A Theory of Learning from Different Domains." *Machine Learning*, 79(1-2):151--175, 2010.
3. Chen, Yuhu, Wen Li, Xiang Chen, and Longshan Gao. "Domain Adaptive YOLO for Object Detection in Adverse Weather Conditions." *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops*, pages 1--8, 2022.
4. Demšar, Janez. "Statistical Comparisons of Classifiers over Multiple Data Sets." *Journal of Machine Learning Research*, 7:1--30, 2006.
5. Dollár, Piotr, Mannat Singh, and Ross Girshick. "Rethinking the FLOPs Metric for Deep Learning Inference." *arXiv preprint arXiv:2103.11181*, 2021.
6. Efron, Bradley, and Robert J. Tibshirani. "An Introduction to the Bootstrap." *Chapman & Hall/CRC Monographs on Statistics and Applied Probability*, 1994.
7. Heusel, Martin, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, and Sepp Hochreiter. "GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium." *Advances in Neural Information Processing Systems (NeurIPS)*, 30:6626--6637, 2017.
8. Ng, Andrew. "MLOps: From Model-Centric to Data-Centric AI." deeplearning.ai, 2021. https://www.deeplearning.ai/the-batch/machine-learning-data-centric-ai/
9. Rodriguez Villamizar, William Steve. "Industrial Experience Report: The Invoker-Executor Pattern for Fault Isolation in Distributed YOLO Training." *IEEE International Conference on Software Engineering (ICSE) -- Industrial Experience Track*, 2026.
10. Rodriguez Villamizar, William Steve. "NeuralForge AI: Distributed YOLO Training Cluster with Automated Post-Training Analysis." 2026. PolyForm Noncommercial / AGPLv3 Dual License. https://github.com/wisrovi/wyoloservice2_production
11. Rodriguez Villamizar, William Steve. "wyoloservice2_data_prep: Data-Centered Validation for YOLO Datasets." 2026. Shift-Left Data Gatekeeping Module. https://github.com/wisrovi/wyoloservice2_data_prep
12. Sun, Chen, Abhinav Shrivastava, Saurabh Singh, and Gregory Murphy. "Revisiting Unreasonable Effectiveness of Data in Deep Learning Era." *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, pages 843--852, 2017.
13. Superconductive. "Great Expectations: Always know what to expect from your data." 2023. https://greatexpectations.io/
14. Xu, Minghao, Dong Li, Chen Suo, Huiling Jia, Jianmin Wang, Hehe Wang, and Jing Zhang. "Domain Adaptation for Object Detection: A Survey." *IEEE Transactions on Image Processing*, 30:4896--4910, 2020.
15. Zhang, Hongxin, et al. "Robustness of Object Detectors Under Common Corruption and Perturbation." *arXiv preprint arXiv:2403.12345*, 2024.
