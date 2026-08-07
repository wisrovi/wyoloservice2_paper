.PHONY: all clean compile

all:
	@echo "Use 'make compile DIR=<path_to_paper_lang_folder>' to compile a specific paper."
	@echo "Example: make compile DIR=rnd_papers/paper_1_agentic_mlops/en"

compile:
	@if [ -z "$(DIR)" ]; then echo "Error: DIR is not set. Usage: make compile DIR=rnd_papers/paper_1_agentic_mlops/en"; exit 1; fi
	@echo "Compiling $(DIR)/main.tex using Docker (texlive)..."
	@docker run --rm -v "$(PWD)/$(DIR):/workdir" -w /workdir texlive/texlive:latest sh -c "pdflatex -interaction=nonstopmode main.tex && bibtex main || true && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex"
	@echo "Compilation finished for $(DIR)/main.pdf"

clean:
	find . -type f -name '*.aux' -delete
	find . -type f -name '*.log' -delete
	find . -type f -name '*.out' -delete
	find . -type f -name '*.toc' -delete
	find . -type f -name '*.bbl' -delete
	find . -type f -name '*.blg' -delete
	find . -type f -name '*.fls' -delete
	find . -type f -name '*.fdb_latexmk' -delete
	find . -type f -name '*.synctex.gz' -delete
	@echo "Cleaned all LaTeX temporary files."
