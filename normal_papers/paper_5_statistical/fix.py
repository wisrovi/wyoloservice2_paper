import os
import subprocess
import re

def tex_to_md(filepath):
    if not os.path.exists(filepath): return
    md_filepath = filepath.replace(".tex", ".md")
    # Using pandoc if available, otherwise just copy
    try:
        subprocess.run(["pandoc", filepath, "-o", md_filepath], check=True)
    except:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(content)

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
    base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_5_statistical"
    for lang in ["en", "es"]:
        target_dir = os.path.join(base_dir, lang)
        if os.path.exists(target_dir):
            print(f"Compiling in {target_dir}...")
            compile_latex(target_dir)
