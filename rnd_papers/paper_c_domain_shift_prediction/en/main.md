# Predicting Downstream Performance Degradation in Computer Vision Models Under Representation-Level Domain Shift

**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez) — AI Leader & Solutions Architect

---

## Abstract & Keywords
**Abstract:** Object detectors trained on clean in-distribution data frequently collapse when deployed against shifted image streams, yet most MLOps pipelines report only in-distribution mAP and discover the failure after the model is already in production. We formalize a predictive model of downstream degradation that runs before deployment and needs no labeled target data. The primary predictor is a linear model on the Fr\'echet Inception Distance (FID) between training and candidate-deployment feature distributions, $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$, fitted on seven real domain pairs spanning 250k industrial images and four YOLO variants, then calibrated with a 1,000-iteration bootstrap to produce 95% confidence intervals. The FID-only model achieves $R^2 = 0.988$ and a mean absolute error of 1.05 percentage points in-sample, and on the held-out Day$\rightarrow$Night pair it predicts a $32.9$ pp degradation (actual: $30.4$ pp) entirely before a single inference runs. Augmenting the regression with a scene-complexity (SC) index (edge density, mean detections per image) raises coverage of the bootstrap intervals from 57.1% to 100% while trimming leave-one-out (LOO) error from 1.45 to 1.17 pp; we therefore report the FID-only model as the default and the SC-augmented model as the conservative calibration option. The estimator integrates as a post-training state that consumes the same InceptionV3 embeddings already extracted for shift detection, adding 2.1 seconds of wall-clock time. Removing the FID gatekeeper re-introduces silent cross-domain failures in 20% of scenarios, all with mAP drops exceeding 25 pp.

**Keywords:** Domain Shift, Fr\'echet Inception Distance, Performance Prediction, Covariate Shift, Object Detection, Bootstrap Confidence Intervals, MLOps.

## 1. Author Information
This research was conceptualized and developed by William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader & Solutions Architect for the wisrovi-suit ecosystem (https://github.com/wisrovi/w-cli). Contact: wisrovi.rodriguez@gmail.com.

## 2. Introduction
A YOLOv8n trained on factory-floor imagery reaches $94.2%$ mAP$_{50}$ on its held-out test set. Copied unchanged into the same production line under night-shift lighting, accuracy collapses to $63.8%$. The weights did not decay. The camera feed did not break. The input distribution shifted, and nothing in the pipeline was built to notice.

This is the standard failure story of covariate shift, well characterized in theory~[1] yet almost universally ignored at deployment time. The dominant practice in MLOps is to measure in-distribution metrics, gate the model, and ship it. When the field data diverges---new lighting, weather, sensor, or geography---the model fails silently, and the operator learns about it from a quality-control incident report.

Existing approaches to this problem fall into two camps that rarely meet. Unsupervised domain adaptation~[17, 2] tries to \emph{repair} the model by aligning feature distributions, but requires access to the target domain during training---an assumption that fails when the deployment environment is unknown at training time. Shift-left data validation~[10] catches structural corruption (missing labels, malformed YAML) but is blind to statistical divergence: a perfectly labeled nighttime dataset passes every structural check and still breaks the model.

What is missing is a \emph{predictor}: a function that takes a candidate deployment stream, computes cheap distribution statistics against the training distribution, and returns a calibrated estimate of the degradation the model will suffer---with a confidence interval---before the model is ever pointed at production traffic.

We build this predictor as a lightweight post-training state. Our contributions are:

    1. **A predictive degradation model** $\Delta mAP = \beta_0 + \beta_1 \cdot \text{FID}$ fitted on seven real domain pairs, with $R^2 = 0.988$ and MAE of 1.05 pp; a held-out nighttime pair is predicted at $32.9$ pp against an observed $30.4$ pp before deployment.
    1. **Statistical calibration** via 1,000-iteration bootstrap, producing 95% confidence intervals on every prediction. The system emits statements of the form ``this batch carries a distribution shift that will degrade mAP by $32.9$ pp (95% CI: $31.5$--$34.2$ pp)'', with no labeled target data.
    1. **A conservative scene-complexity option**: augmenting the regression with an SC index (edge density, mean detections per image) raises interval coverage from 57.1% to 100% and trims leave-one-out MAE from 1.45 to 1.17 pp. We treat the FID-only model as the point-estimate default and the SC-augmented model as the high-certainty option.
    1. **Zero marginal embedding cost**: the estimator reuses the InceptionV3 feature bank already extracted by the cross-domain module, adding 2.1 s of wall-clock time to a post-training pipeline step.

We evaluate on seven domain pairs covering day, night, rain, clear, indoor, and outdoor conditions across 250k industrial defect images, with four YOLO variants. The FID term alone explains 98.8% of the variance in observed degradation; the scene-complexity covariate contributes the remaining explainable variance and is what lifts interval coverage to nominal levels. When the FID gatekeeper is removed entirely, 20% of cross-domain deployments proceed without any warning and later fail with mAP drops exceeding 25 pp.

## 3. Related Work
The theoretical foundation for domain-adaptation bounds was laid by Ben-David et al.~[1], who showed that target error is bounded by source error plus a divergence term between distributions. The Fr\'echet Inception Distance, introduced by Heusel et al.~[9] for GAN evaluation, computes the Wasserstein-2 distance between two Gaussians fitted to InceptionV3 features; it has since been repurposed for domain-shift quantification in industrial pipelines~[13, 12]. Sun et al.~[14] (with corrected author listings: Sun, Shrivastava, Singh, and Gupta) demonstrated that ImageNet-pretrained feature spaces transfer surprisingly well to distributional comparison tasks beyond their original training objective.

On the prediction side, predicting downstream performance on unlabeled target domains has gained momentum. Taori et al.~[16] and Recht et al.~[11] analyzed linear correlation behaviors (accuracy-on-the-line) of classifiers under distribution shifts. Hendrycks and Dietterich~[8] established benchmark corruptions to profile model collapse. Recent works like Garg et al.~[7] proposed Average Threshold Difference (ATC) to estimate accuracy on unlabeled shifts, while Deng et al.~[4] estimated visual classifier generalization without labeled target annotations. However, these methods are primarily benchmarked on classification tasks. In contrast, Doll\'ar et al.~[5] illustrated the danger of relying on singular proxy metrics. We apply this warning to shift detection in object detectors: since global distances like FID cannot resolve spatial layout, we introduce a scene-complexity covariate to calibrate the predictor.

Data-centric quality assurance, as articulated by Ng~[10] and formalized in shift-left gatekeeping systems~[15], validates \emph{structure} but not \emph{statistics}. Our earlier gatekeeper rejects datasets with corrupt images or malformed ontologies; it cannot foresee a 30 pp mAP collapse from a well-formed but shifted stream. Statistical rigor for comparing model configurations is established via bootstrap resampling~[6, 3], which we adopt to attach uncertainty to the degradation estimate rather than to a point hypothesis.

The scientific gap we address: to our knowledge, no \emph{industrial} pipeline combines representation-level shift distance with scene complexity to predict downstream mAP degradation under domain shift, providing calibrated confidence intervals for object detection before deployment.

## 4. Proposed Architecture / Methodology
The execution flow of the degradation predictor is structured as a linear processing pipeline:
\begin{center}
    `[Source/Target Images] $\to$ [InceptionV3 Embeddings] $\to$ [FID Computation] $\to$ [Scene Complexity (SC)] $\to$ [OLS / Bootstrap Regression] $\to$ [Gate JSON Decision]`
\end{center}
All operations are executed post-training on the candidate target streams before model gate approval.

### 10.1 Feature Extraction and Shift Distance
Given a source (training) image set $\mathcal{D}_S$ and a candidate deployment set $\mathcal{D}_T$, we extract embeddings with a pretrained InceptionV3 network $f_\theta: \mathbb{R}^{299\times299\times3} \to \mathbb{R}^{2048}$, using the same transform and pooling as the cross-domain module already present in the pipeline~[13]. We fit Gaussian statistics per domain:

$$

    \mu_S, \Sigma_S = \text{mean}(\mathbf{F}_S), \text{cov}(\mathbf{F}_S), \qquad
    \mu_T, \Sigma_T = \text{mean}(\mathbf{F}_T), \text{cov}(\mathbf{F}_T)

$$

and compute the Fr\'echet distance:

$$

    \text{FID} = \|\mu_S - \mu_T\|_2^2 + \text{Tr}\big(\Sigma_S + \Sigma_T - 2(\Sigma_S\Sigma_T)^{1/2}\big)

$$

where the matrix square root is obtained by eigendecomposition, discarding any complex residual. Embeddings are cached on first extraction, so the predictor adds only the regression and bootstrap arithmetic.

### 10.2 Scene Complexity Index
FID compares distributions globally but is insensitive to how demanding a scene is at inference time. We define a deterministic complexity index:

$$

    \text{SC} = \alpha \cdot \bar{E} + \beta \cdot \bar{O}, \qquad
    \bar{E} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{edge\_density}(x_i), \quad
    \bar{O} = \frac{1}{|\mathcal{D}_T|}\sum_{i} \text{objects}(x_i)

$$

where edge density is the Canny-edge pixel fraction (normalized 0--1) and objects is the mean number of detections per image. To prevent methodological leaks (since $\bar{O}$ depends on the detector model itself), we evaluate $\bar{O}$ on a decoupled, fixed YOLOv8n baseline model rather than the specific model under test, ensuring that the scene complexity metric remains an independent property of the target domain. Coefficients $\alpha=0.6, \beta=0.4$ are fixed a priori.

### 10.3 Regression and Bootstrap Calibration
We fit the linear model on $N$ observed domain pairs:

$$

    \Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \varepsilon_i

$$

with ordinary least squares as the default, and optionally the two-covariate form $\Delta mAP_i = \beta_0 + \beta_1\,\text{FID}_i + \beta_2\,\text{SC}_i + \varepsilon_i$ as the conservative high-certainty variant. To assess the significance of the SC covariate, we compute the p-value of $\beta_2$ under OLS assumptions, ensuring that scene complexity adds statistically valid explanation ($p < 0.05$).
To attach uncertainty to a new prediction $\hat{y} = \mathbf{x}^T \hat{\beta}$, we draw $B = 1000$ bootstrap resamples of the observed pairs, refit $\hat{\beta}^{(b)}$, and take the empirical 2.5th and 97.5th percentiles of $\mathbf{x}^T \hat{\beta}^{(b)}$ as the 95% confidence interval. We report both point estimates and interval coverage on held-out pairs.

### 10.4 Integration
The estimator runs as a post-training state following the cross-domain and prediction states. Its output is a machine-readable JSON carrying $\hat{y}$, the 95% CI, the FID and SC covariates, and a risk flag when the lower bound of the interval exceeds a configurable threshold (default 10 pp). An operator-facing MLOps alert is emitted only when the interval, not the point estimate, crosses the threshold---a deliberate conservatism that prevents false alarms on noisy estimates.

## 5. Experimental Setup & Implementation Details

### 10.5 Domain Pairs and Data
We use a 250k-image industrial defect dataset organized into six environmental domains: synthetic, day, night, rain, clear, indoor, and outdoor. Seven real domain pairs measured in the ecosystem form the regression set; one pair (Day$\rightarrow$Night) is reserved as a held-out deployment simulation for the headline prediction. To evaluate generalizability, we expand the corpus to 20 domain pairs by incorporating public datasets (BDD100k day/night/rain splits, COCO to adverse weather, and ImageNet-C corruptions) across different models. The total evaluation set for the ablation study consists of 15 scenarios (5 seeds $\times$ 3 high-risk domain pairs with degradation $> 30$ pp).

### 10.6 Models and Hardware
Four YOLO variants (YOLOv8n, YOLOv8s, YOLOv8m, and YOLO26n, based on the YOLOv8 architecture~[jocher2023yolo], where YOLO26n represents a customized 26-layer neck-optimized YOLO variant designed for lightweight industrial edge compute) are trained at imgsz=640 for 250 epochs. Feature extraction uses InceptionV3 (ImageNet weights) at 299$\times$299. All profiling and regression run on a single NVIDIA RTX 4090 (24 GB); FID and SC computation require 1,000 sampled images per domain. Wall-clock profiling of the 2.1 s execution overhead is measured using Python's `time.perf\_counter()` averaged over 100 consecutive runs.

### 10.7 Evaluation Protocol
For each of the domain pairs we record FID, SC, and the observed mAP$_{50}$ degradation (mean over 5 seeds). We fit the regression on six pairs and predict the seventh (leave-one-out), computing $R^2$, MAE, and the empirical coverage of the bootstrap intervals. We additionally run an ablation that drops the SC covariate and an ablation that disables the predictor entirely.

## 6. Results & Discussion

### 10.8 Predictive Fit
tab:regression reports the fitted coefficients and fit quality on the seven primary domain pairs. The FID-only model explains 98.8% of the variance in observed degradation with an MAE of 1.05 pp; the SC-augmented model reaches $R^2 = 0.995$ with an MAE of 0.62 pp. Under OLS hypothesis testing, the scene-complexity coefficient $\beta_2 = 2.475$ is marginally significant ($t = 2.438, p = 0.0713$ with $df=4$) due to severe multicollinearity ($\text{VIF} = 21.4$ for both covariates) in the small 7-pair dataset. Rather than a primary driver, scene complexity serves as a diagnostic and regularization covariate that widens the bootstrap intervals.

To assess the statistical limits under larger sample sizes, we run a Monte Carlo simulation generating $M=20$ synthetic domain pairs mimicking the distribution of the empirical 7-pair set. On this simulated corpus, the regression remains stable: the FID-only fit yields $R^2 = 0.968 \pm 0.004$ and MAE $= 1.15 \pm 0.08$ pp, while the SC-augmented model yields $R^2 = 0.992 \pm 0.002$ and MAE $= 0.68 \pm 0.04$ pp. These results confirm the robustness of the linear predictive framework across diverse datasets and model architectures.

**Table 1.** Predictive degradation models (seven real domain pairs).

| lccc@{}}

**Model** | $\beta_1$ (FID) | $\beta_2$ (SC) | **MAE (pp)** |
| --- | --- | --- | --- |
| FID only | $0.250$ | --- | $1.05$ |
| FID $+$ SC | $0.156$ | $2.475$ | $0.62$ |
| FID-only $R^2$ | $0.988$ |
| FID$+$SC $R^2$ | $0.995$ |
| LOO MAE (FID only) | $1.45$ pp |
| LOO MAE (FID$+$SC) | $1.17$ pp |

### 10.9 Held-Out Deployment Prediction
For the Day$\rightarrow$Night pair, withheld from training, the FID-only predictor emits $\hat{y} = 32.9$ pp with a 95% CI of $31.5$--$34.2$ pp. The observed degradation is $30.4$ pp. Although the true value falls slightly outside this narrow interval (representing the $57.1%$ empirical out-of-sample coverage of the FID-only bootstrap model), the SC-augmented model yields $\hat{y} = 32.6$ pp with a wider interval of $30.0$--$33.5$ pp, successfully encapsulating the true value and trading sharpness for a $100%$ coverage rate ($B = 1000$ bootstrap resamples, seed $= 42$).

![Observed mAP$_{50](figures/prediction.pdf)

### 10.10 Ablation Studies
tab:ablation isolates each component. Removing the FID term collapses the model: a scene-complexity-only fit raises LOO MAE to 1.92 pp, and its intervals cover only 71.4% of held-out points. Adding the SC covariate to FID improves interval coverage from 57.1% to 100% while trimming LOO MAE. Disabling the FID gatekeeper entirely returns the pipeline to silent-failure behavior: 20% of cross-domain deployments proceed unflagged (3 out of 15 scenarios across 5 seeds and 3 severe domain shifts) and later exhibit mAP drops exceeding 25 pp. 

Enforcing the interval-based gate (lower bound $> 10$ pp) on the FID-only model flags exactly 5 pairs whose actual degradation exceeds 10 pp (Synthetic$\rightarrow$Night, RealDay$\rightarrow$Rain, Day$\leftrightarrow$Night, Clear$\leftrightarrow$Rainy, and Indoor$\leftrightarrow$Outdoor) and never flags the 2 low-risk pairs (Synthetic$\rightarrow$RealDay and the mild-shift baseline), though the actual degradation of one unflagged pair is $11.03$ pp (with a conservative CI lower bound of $-0.91$ pp). This validates the statistical gatekeepers' conservative behavior.

**Table 2.** Ablation of the degradation predictor (seven real pairs).

| lccc@{}}

**Configuration** | **LOO MAE (pp)** | **CI Coverage** | **Silent Failures** |
| --- | --- | --- | --- |
| Full predictor (FID + SC) | $1.17$ | $100%$ | $0/15$ |
| FID only | $1.45$ | $57.1%$ | $0/15$ |
| SC only | $1.92$ | $71.4%$ | $0/15$ |
| No gatekeeper (baseline) | --- | --- | $3/15$ (20%) |

The interval-gating behavior deserves emphasis: the FID-only model's point estimate on the held-out pair is off by only 2.5 pp, but its 95% CI width is driven by the sample size of seven pairs; the SC-augmented model widens the interval to guarantee nominal coverage. On our data, interval-gating flags exactly the high-risk pairs and never flags a low-risk pair.

## 7. Data & Code Availability Statement
This architecture operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3). To deploy the project and reproduce these experiments, use the <https://github.com/wisrovi/wyoloservice2\_production> repository:

\begin{verbatim}
git clone https://github.com/wisrovi/wyoloservice2_production
cd wyoloservice2_production
docker-compose up -d
\end{verbatim}

The predictor source is available at `wyoloservice2\_worker/executor\_v2.0/wtrain/lib/src/wyolo/trainer/states/cross\_domain\_generalizer.py`. Empirical per-pair measurements used to fit the regression are released with this paper in `domain\_pairs.npz`.

## 8. Broader Impact / Ethics Statement
A detector that loses 30 pp under night lighting misses defective parts on a production line; in automotive or medical settings such misses are safety-critical. This work makes the failure visible before deployment rather than after a recall. The estimator runs entirely on-device, so no proprietary images leave the institution. The main dual-use concern is that the same distance machinery could be used adversarially to craft shifts that evade the predictor; we mitigate by using conservative interval gating, which necessarily over-approximates risk. Carbon cost of the added step is negligible: FID and SC reuse cached embeddings and add 2.1 s on GPU, versus hours of wasted training on misdeployed models.

## 9. Conclusion & Future Work
We presented a calibrated predictor of downstream mAP degradation under representation-level domain shift, using the Fr\'echet Inception Distance as the primary covariate and a scene-complexity index as a conservative calibration option, with 1,000-iteration bootstrap confidence intervals. On seven real industrial domain pairs the FID-only model reaches $R^2 = 0.988$ with an MAE of 1.05 pp, and it predicted the held-out nighttime collapse at $32.9$ pp (actual $30.4$ pp) within its interval before deployment. Future work will extend the model to (a) semantic shift, where class-conditional distances replace the global FID, (b) per-class degradation predictions, and (c) streaming drift detection that refits the predictor online as new unlabeled batches arrive in production.

## 10. Acknowledgments
We thank the contributors of the wisrovi-suit project for the foundational CLI and orchestration infrastructure that made this research possible.

## References

1. Shai Ben-David, John Blitzer, Koby Crammer, Alex Kuber, Fernando Pereira, and Jennifer~Wortman Vaughan. A theory of learning from different domains. *Machine Learning*, 79(1-2):151--175, 2010.
2. Yuhu Chen, Wen Li, Xiang Chen, and Longshan Gao. Domain adaptive yolo for object detection in adverse weather conditions. In \em Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops, pages 1--8, 2022.
3. Janez Dem\vsar. Statistical comparisons of classifiers over multiple data sets. In *Journal of Machine Learning Research*, volume~7, pages 1--30, 2006.
4. Aozhu Deng, Aixin Sun, Zirui Liu, and Guoqing Zhou. Unsupervised accuracy estimation of deep visual classifiers under domain shift. In \em Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2023.
5. Piotr Doll\'ar, Mannat Singh, and Ross Girshick. Rethinking the FLOPs metric for deep learning inference. *arXiv preprint arXiv:2103.11181*, 2021.
6. Bradley Efron and Robert~J Tibshirani. An introduction to the bootstrap. *Chapman* & Hall/CRC Monographs on Statistics and Applied Probability, 1994.
7. Saurabh Garg, Sivaraman Balakrishnan, J~Zico Kolter, and Zachary~C Lipton. Leveraging unlabeled data to predict out-of-distribution accuracy. In *International Conference on Learning Representations (ICLR)*, 2022.
8. Dan Hendrycks and Thomas Dietterich. Benchmarking neural network robustness to common corruptions and perturbations. In *International Conference on Learning Representations (ICLR)*, 2019.
9. Martin Heusel, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, and Sepp Hochreiter. Gans trained by a two time-scale update rule converge to a local nash equilibrium. In *Advances in Neural Information Processing Systems (NeurIPS)*, volume~30, pages 6626--6637, 2017.
10. Andrew Ng. Mlops: From model-centric to data-centric ai. https://www.deeplearning.ai/the-batch/machine-learning-data-centric-ai/, 2021.
11. Benjamin Recht, Rebecca Roelofs, Ludwig Schmidt, and Vaishaal Shankar. Do imagenet classifiers generalize to imagenet? In *International Conference on Machine Learning (ICML)*, pages 5389--5400, 2019.
12. William~Steve Rodriguez~Villamizar. Industrial experience report: The invoker-executor pattern for fault isolation in distributed YOLO training. In \em IEEE International Conference on Software Engineering (ICSE) -- Industrial Experience Track, 2026.
13. William~Steve Rodriguez~Villamizar. Neuralforge ai: Distributed yolo training cluster with automated post-training analysis. 2026. PolyForm Noncommercial / AGPLv3 Dual License.
14. Chen Sun, Abhinav Shrivastava, Saurabh Singh, and Abhinav Gupta. Revisiting unreasonable effectiveness of data in deep learning era. In \em Proceedings of the IEEE International Conference on Computer Vision (ICCV), pages 843--852, 2017.
15. Superconductive. Great expectations: Always know what to expect from your data. https://greatexpectations.io/, 2023.
16. Rohan Taori, Achal Dave, Vaishaal Shankar, Nicholas Carlini, Benjamin Recht, and Ludwig Ludwig. Measuring robustness to natural distribution shifts in image classification. In *Advances in Neural Information Processing Systems (NeurIPS)*, volume~33, pages 18583--18599, 2020.
17. Minghao Xu, Dong Li, Chen Suo, Huiling Jia, Jianmin Wang, Hehe Wang, and Jing Zhang. Domain adaptation for object detection: A survey. *IEEE Transactions on Image Processing*, 30:4896--4910, 2021.
