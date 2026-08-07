# Rules for wyoloservice2_paper

## Dual Format Requirement (Strict Rule)
- All papers in this repository MUST be authored and maintained in two identical formats simultaneously:
  1. **Markdown (`.md`)**: A readable markdown version for quick GitHub/web preview.
  2. **LaTeX (`.tex`)**: The formal academic LaTeX source file.
- Additionally, every time the LaTeX file is updated, it MUST be compiled to generate the corresponding **`.pdf`** output file. The generated PDF must also be tracked in the repository.
- The content between the `.md` and `.tex` files must always be kept strictly identical.

## Scientific Paper Structure (Camera-Ready Quality)
All papers must adhere to a 4 to 8 page limit (double-column IEEE format preferred) and MUST strictly contain the following sections in order:
1. **Abstract & Keywords**: Problem, solution, results, and 5-7 keywords.
2. **Author Information**: Must include "William Steve Rodriguez Villamizar (wisrovi rodriguez)", "AI Leader & Solutions Architect", "eCaptureDtech, Badajoz, Extremadura, Spain", and contact/ORCID.
3. **Introduction**: Context, Problem Statement, and Key Contributions.
4. **Related Work**: State of the art analysis and the scientific gap our approach solves.
5. **Proposed Architecture / Methodology**: Core system explanation with rendered Mermaid diagrams, formulas, or logical flows.
6. **Experimental Setup & Implementation Details**: Hardware environment, tools, and testing methodology.
7. **Results & Discussion**: Quantitative (tables/charts) and qualitative (reports) analysis of the outcomes.
8. **Data & Code Availability Statement**: Link to GitHub repos and clarification of Dual Licensing (PolyForm / AGPLv3).
9. **Broader Impact / Ethics Statement**: Carbon footprint reduction (efficiency), safety (Shift-Left), and dual-use concerns.
10. **Conclusion & Future Work**.
11. **Acknowledgments**: Thanking eCaptureDtech and funding bodies.
12. **References**: Formatted in IEEE/APA style.
13. **Appendices (Optional)**: For long YAML configurations or heavy code snippets that would clutter the main text.

## Language and Synchronization Rules (Strict Rule)
- **README Files**: All `README.md` files across this repository MUST be written in perfect English.
- **Multi-Language Papers**: Each paper MUST exist in both Spanish and English versions.
- **Folder Structure**: Inside each paper's directory, there MUST be specific subfolders for each language (e.g., `es/` for Spanish and `en/` for English). The Dual Format Requirement (Markdown + LaTeX + PDF) applies within each language folder.
- **Mandatory Synchronization**: It is strictly mandatory that if a paper is updated in one language, its exact translation/counterpart in the other language must be synchronized simultaneously. They cannot fall out of sync.

## Advanced Formatting & Academic Standards
- **Bibliography**: Hardcoded references in the `.tex` files are strictly forbidden. A `references.bib` (BibTeX) file MUST be used to manage all citations automatically.
- **Assets & Figures**: Every paper language folder must contain a `figures/` directory to store images, rendered Mermaid diagrams, and plots. Do not clutter the root folder of the paper.
- **Academic Tone**: The writing must maintain a formal, objective, third-person or first-person plural ("We propose", "We evaluate") academic voice. Do not use colloquialisms or English contractions (e.g., use "do not" instead of "don't").
- **Standardized Naming**: The primary LaTeX file must always be named `main.tex` and its compiled output `main.pdf`.

## Anti-AI Detection / Natural Academic Voice (Strict Rule)
To prevent the papers from sounding robotic or being flagged by AI detectors, all text generation MUST adhere to the following stylistic guidelines:
1. **Zero AI Buzzwords**: NEVER use cliché AI terms such as: "delve into", "tapestry", "realm", "navigate the complexities", "paramount", "transformative", or excessive use of "furthermore/moreover/additionally".
2. **High Burstiness (Perplexity)**: Sentence lengths must vary significantly. Mix very short, punchy statements with longer, technical explanations. Avoid uniform sentence structures.
3. **Active Voice & Pragmatism**: Be direct. Use active voice ("We isolated the cluster" instead of "The cluster was isolated"). Avoid philosophical introductions; get straight to the technical problem and solution.
4. **Data-Driven, Not Adjective-Driven**: Do not use flowery adjectives ("impressive speedup", "highly efficient"). Instead, use raw facts and numbers ("reduced latency by 43%", "dropped memory usage from 28GB to 16GB").
5. **Real-World Imperfections**: Embrace real-world engineering constraints and mention actual pain points faced during the development at eCaptureDtech (e.g., "OOM errors crashing the daemon"). This adds human authenticity.

