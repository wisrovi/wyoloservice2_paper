import os
import subprocess
import re

def tex_to_md(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = re.sub(r"\\documentclass.*?\n", "", content)
    content = re.sub(r"\\usepackage.*?\n", "", content)
    content = re.sub(r"\\title\{(.*?)\\.*?\}", r"# \1", content, flags=re.DOTALL)
    content = re.sub(r"\\title\{(.*?)\}", r"# \1", content, flags=re.DOTALL)
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
    content = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{enumerate\}", "", content)
    content = re.sub(r"\\end\{enumerate\}", "", content)
    content = re.sub(r"\\begin\{itemize\}", "", content)
    content = re.sub(r"\\end\{itemize\}", "", content)
    content = re.sub(r"\\item", "-", content)
    content = re.sub(r"\\bibliographystyle.*?\n", "", content)
    content = re.sub(r"\\bibliography.*?\n", "", content)
    content = re.sub(r"\\end\{document\}", "", content)
    content = re.sub(r"\\IEEEauthorblockN\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\IEEEauthorblockA\{(.*?)\}", r"\1", content, flags=re.DOTALL)
    content = re.sub(r"\\thanks\{.*?\}", "", content)
    content = re.sub(r"\\def\\BibTeX.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"\n{3,}", "\n\n", content)
    
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
    base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_3_robustness"
    for lang in ["en", "es"]:
        target_dir = os.path.join(base_dir, lang)
        if os.path.exists(target_dir):
            print(f"Compiling in {target_dir}...")
            compile_latex(target_dir)
