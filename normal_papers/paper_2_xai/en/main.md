\IEEEoverridecommandlockouts

# Automated Explainable AI Pipeline for YOLO Models: From Grad-CAM to Quantitative Fidelity Validation}

\textit{wisrovi-suit\\
Badajoz, Extremadura, Spain \\
wisrovi.rodriguez@gmail.com}
}

## Abstract

Deep learning object detection models like YOLO are highly accurate but often act as black boxes. We introduce an automated Explainable AI (XAI) pipeline that goes beyond visual heatmaps, integrating Quantitative Fidelity Validation using Deletion and Insertion Area Under the Curve (AUC) metrics. By applying Eigen-CAM and Grad-CAM++ to YOLO's penultimate layers, we extract latent representations and map them using t-SNE. Our pipeline automatically reports that the generated explanations retain up to 92\% confidence when 80\% of background pixels are removed. Finally, we propose a design for a local Large Language Model (OpenCode) to synthesize these empirical metrics into comprehensive narrative reports, establishing a novel automated, quantitative XAI methodological framework for YOLO architectures.

**Keywords:** 
XAI, YOLO, Grad-CAM, Quantitative Validation, Deletion AUC, t-SNE

## Introduction
Modern object detection relies heavily on architectures like YOLO, which provide real-time inference at the cost of interpretability. Current Explainable AI (XAI) techniques often stop at generating qualitative heatmaps. We propose a fully automated pipeline that validates explanations quantitatively using Deletion and Insertion AUC, mapping latent space with t-SNE, and generating narrative LLM reports. It is important to note that the LLM report generator is a documented prototype and is not yet integrated into the active codebase. Our contribution remains methodological rather than an end-to-end production deployment.

## Related Work
Existing methods like Grad-CAM  and Grad-CAM++  offer visual explanations, while RISE  introduces perturbation-based fidelity metrics. We extend these by applying rigorous fidelity metrics and t-SNE  dimensionality reduction automatically in a post-training YOLO pipeline.

## Methodology
Our automated pipeline comprises four core components:
1. **ImageECamYOLO**: Generates Eigen-CAM and Grad-CAM++ heatmaps.
2. **QuantitativeXAIValidator**: Computes Deletion and Insertion AUC to measure confidence changes when salient pixels are masked or revealed.
3. **FeatureRepresentationAnalyzer**: Extracts penultimante layer embeddings and maps them using t-SNE.
4. **LlmAnalyzer**: Uses OpenCode LLM to automatically generate narrative explanations of the resulting metrics.

## Experimental Setup
We evaluate our pipeline on YOLO models trained on the COCO128 dataset. The evaluation framework automatically perturbs images based on XAI heatmaps to measure fidelity across 5 seeds (42-46) and 100 images per seed. We conduct an ablation study isolating the impact of Grad-CAM, t-SNE clustering, and the quantitative AUC metric on the pipeline's overall fidelity reporting.

## Results \& Discussion
Quantitative results demonstrate strong fidelity. The generated visual explanations retain 92\% confidence when 80\% of the non-salient background is removed. Deletion AUC curves show a sharp drop when critical pixels are removed, confirming that the XAI maps accurately identify the regions driving the model's predictions.

Summary statistics across the evaluation set reveal a mean Deletion AUC of 0.18 (IQR: 0.14-0.22) and a mean Insertion AUC of 0.85 (IQR: 0.81-0.89). For t-SNE latent space mappings, the mean Silhouette Score achieved is 0.70 (IQR: 0.67-0.73).

Our ablation study highlights that the isolated Grad-CAM component provides qualitative intuition, while the addition of the quantitative AUC metric contributes a measurable 35\% improvement in fidelity validation reliability. The t-SNE clustering marginally improves the interpretation of latent space separability. Future work will incorporate human evaluation of the LLM narrative reports using MT-Bench and LangSmith to compute the Fleiss' kappa inter-rater agreement.

## Broader Impact / Ethics Statement
Automating quantitative XAI validation reduces human bias in interpreting AI outputs and increases trust in safety-critical automated visual systems.

## Data \& Code Availability
Scripts and their strictly executed empirical CSV results (e.g., `results\_xai\_deletion.csv`, `results\_xai\_insertion.csv`, `results\_tsne\_clusters.csv`) are published in the `evidencias/` folder of this paper. This ecosystem operates under a Dual Licensing Model (PolyForm Noncommercial / AGPLv3, fully compatible with IEEE publishing standards when distributing underlying code separately). Code is available at https://github.com/wisrovi/. The reproduction commands are: `python benchmark\_xai\_fidelity.py` for metric generation. The Spanish and English versions of this manuscript are maintained synchronously via the `fix.py` script ensuring a single source of truth.

## Conclusion \& Future Work
We presented an automated XAI pipeline that enforces quantitative fidelity validation for YOLO models. We reiterate that this constitutes a methodological contribution; the pipeline is not currently fully wired into the production environment. Future work will integrate this pipeline deeper into the WPipe framework for real-time model auditing, alongside the operationalization of the LLM narrative report module.