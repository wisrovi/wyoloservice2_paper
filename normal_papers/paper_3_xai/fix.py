import os
import subprocess
import re

def tex_to_md(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = re.sub(r"\\documentclass.*?\n", "", content)
    content = re.sub(r"\\IEEEoverridecommandlockouts.*?\n", "", content)
    content = re.sub(r"\\raggedbottom.*?\n", "", content)
    content = re.sub(r"\\usepackage.*?\n", "", content)
    content = re.sub(r"\\title\{(.*?)\\.*?\}", r"# \1", content, flags=re.DOTALL)
    content = re.sub(r"\\author\{(.*?)\}", r"**Author:** \1", content, flags=re.DOTALL)
    content = re.sub(r"\\date\{.*?\}", "", content)
    content = re.sub(r"\\begin\{document\}", "", content)
    content = re.sub(r"\\maketitle", "", content)
    content = re.sub(r"\\section\*?\{(.*?)\}", r"## \1", content)
    content = re.sub(r"\\subsection\{(.*?)\}", r"### \1", content)
    content = re.sub(r"\\textbf\{(.*?)\}", r"**\1**", content)
    content = re.sub(r"\\textit\{(.*?)\}", r"*\1*", content)
    content = re.sub(r"\\texttt\{(.*?)\}", r"`\1`", content)
    content = re.sub(r"\\url\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\cite\{.*?\}", "", content)
    content = re.sub(r"\\ref\{.*?\}", "", content)
    content = re.sub(r"\\Cref\{.*?\}", "", content)
    content = re.sub(r"\\begin\{abstract\}", "## Abstract\n", content)
    content = re.sub(r"\\end\{abstract\}", "", content)
    content = re.sub(r"\\begin\{IEEEkeywords\}", "**Keywords:** ", content)
    content = re.sub(r"\\end\{IEEEkeywords\}", "", content)
    
    # Figure handling
    def repl_fig(m):
        fig_text = m.group(0)
        img_match = re.search(r"\\includegraphics.*?\{(.*?)\}", fig_text)
        cap_match = re.search(r"\\caption\{(.*?)\}", fig_text)
        img_path = img_match.group(1).replace('../', '') if img_match else ""
        caption = cap_match.group(1) if cap_match else ""
        return f"\n![{caption}]({img_path})\n\n*{caption}*\n"
    content = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", repl_fig, content, flags=re.DOTALL)
    
    # Table handling (simple convert for this paper)
    def repl_table(m):
        tbl_text = m.group(0)
        cap_match = re.search(r"\\caption\{(.*?)\}", tbl_text)
        caption = cap_match.group(1) if cap_match else ""
        return f"\n**Table: {caption}**\n\n| Component Configuration | Mean Simulated AUC (N=500) |\n|---|---|\n| Baseline (Random Noise) | 0.500 |\n| Grad-CAM Deletion Only | 0.181 |\n| Grad-CAM Insertion Only | 0.850 |\n| Eigen-CAM Insertion | 0.901 |\n\n"
    content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", repl_table, content, flags=re.DOTALL)

    content = re.sub(r"\\begin\{enumerate\}", "", content)
    content = re.sub(r"\\end\{enumerate\}", "", content)
    content = re.sub(r"\\item", "-", content)
    content = re.sub(r"\\bibliographystyle.*?\n", "", content)
    content = re.sub(r"\\bibliography.*?\n", "", content)
    content = re.sub(r"\\end\{document\}", "", content)
    content = re.sub(r"\\IEEEauthorblockN\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\IEEEauthorblockA\{(.*?)\}", r"\1", content, flags=re.DOTALL)
    content = re.sub(r"\\thanks\{.*?\}", "", content)
    content = re.sub(r"\\&", "&", content)
    content = re.sub(r"\}", "", content)  # catch stray braces
    content = re.sub(r"\\sim", "~", content)
    content = re.sub(r"\\,", " ", content)
    content = re.sub(r"\\{'a}", "á", content)
    content = re.sub(r"\\{'e}", "é", content)
    content = re.sub(r"\\{'i}", "í", content)
    content = re.sub(r"\\{'o}", "ó", content)
    content = re.sub(r"\\{'u}", "ú", content)
    content = re.sub(r"``", '"', content)
    content = re.sub(r"''", '"', content)
    content = re.sub(r"\\\\", "\n", content)
    content = re.sub(r"\$p < 0.0001\$", "p < 0.0001", content)
    content = re.sub(r"\$p=0.0020\$", "p = 0.0020", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    
    bbl_filepath = filepath.replace(".tex", ".bbl")
    if os.path.exists(bbl_filepath):
        with open(bbl_filepath, "r", encoding="utf-8") as bf:
            bbl_content = bf.read()
        refs = []
        for match in re.finditer(r"\\bibitem\{.*?\}(.*?)(?=\\bibitem|\Z)", bbl_content, re.DOTALL):
            ref_text = match.group(1).replace("\n", " ").strip()
            ref_text = re.sub(r"\\newblock", "", ref_text)
            ref_text = re.sub(r"\\emph\{(.*?)\}", r"*\1*", ref_text)
            ref_text = re.sub(r"\\url\{(.*?)\}", r"\1", ref_text)
            ref_text = re.sub(r"\\end\{thebibliography\}", "", ref_text)
            ref_text = re.sub(r"\\hskip.*?\\relax", " ", ref_text)
            ref_text = ref_text.replace(" }", "")
            refs.append(f"- {ref_text.strip()}")
        if refs:
            content += "\n\n## References\n" + "\n".join(refs)

    md_filepath = filepath.replace(".tex", ".md")
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

def compile_latex(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    subprocess.run(["bibtex", "main"])
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"])
    tex_to_md("main.tex")
    os.chdir(cwd)

if __name__ == "__main__":
    base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_3_xai"
    for lang in ["en", "es"]:
        target_dir = os.path.join(base_dir, lang)
        if os.path.exists(target_dir):
            print(f"Compiling in {target_dir}...")
            compile_latex(target_dir)
