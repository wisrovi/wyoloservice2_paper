import os
import subprocess

def compile_latex(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], stdout=subprocess.DEVNULL)
    subprocess.run(["bibtex", "main"], stdout=subprocess.DEVNULL)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], stdout=subprocess.DEVNULL)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], stdout=subprocess.DEVNULL)
    os.chdir(cwd)

if __name__ == "__main__":
    base_dir = "/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_5_statistical"
    for lang in ["en", "es"]:
        target_dir = os.path.join(base_dir, lang)
        if os.path.exists(target_dir):
            print(f"Compiling in {target_dir}...")
            compile_latex(target_dir)
