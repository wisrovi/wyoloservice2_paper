import os
import re
import subprocess
import time

def get_pending_papers():
    verdict_file = "IEEE_REVIEW_VERDICT.md"
    accepted_papers = set()
    if os.path.exists(verdict_file):
        with open(verdict_file, "r") as f:
            content = f.read()
            blocks = content.split("## IEEE Peer Review Report")
            for block in blocks:
                if "ACEPTADO" in block and "STATUS: APPROVED" in block:
                    m = re.search(r"(paper_[a-zA-Z0-9_]+)", block)
                    if m:
                        accepted_papers.add(m.group(1))
    
    papers = []
    for folder in ["normal_papers", "rnd_papers"]:
        if not os.path.exists(folder): continue
        for paper in sorted(os.listdir(folder)):
            if paper.startswith("paper_"):
                papers.append(paper)
    
    return sorted([p for p in papers if p not in accepted_papers])

def run_revisor(paper):
    print(f"Running revisor for {paper}...")
    subprocess.run(["./run_revisor.sh", paper], check=False)

def run_fixer(paper):
    print(f"Running fixer for {paper}...")
    prompt = f"Please read the latest feedback for {paper} at the bottom of IEEE_REVIEW_VERDICT.md. Then, edit the files in the {paper} directory (including en/main.tex, es/main.tex, en/main.md, es/main.md, references.bib, and any scripts) to apply ALL the requested modifications from the reviewer. You have full permission to use tools to read and edit the files. Ensure all modifications are fully implemented."
    subprocess.run(["opencode", "run", "-m", "opencode/deepseek-v4-flash-free", prompt], check=False)

def commit_changes(paper):
    print(f"Committing changes for {paper}...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", f"[FIX] apply reviewer feedback for {paper}"], check=False)

def main():
    while True:
        pending = get_pending_papers()
        print(f"PENDING PAPERS ({len(pending)}):", pending)
        if not pending:
            print("All papers have been accepted!")
            break
        
        paper = pending[0]
        print(f"\n--- Processing {paper} ---")
        
        run_revisor(paper)
        
        # Check if accepted after review
        if paper not in get_pending_papers():
            print(f"{paper} is ACEPTADO!")
            continue
            
        run_fixer(paper)
        commit_changes(paper)

if __name__ == "__main__":
    main()
