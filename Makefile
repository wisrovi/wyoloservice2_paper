.PHONY: all clean compile

all:
	@echo "Use 'make compile DIR=<path_to_paper_lang_folder>' to compile a specific paper."

compile:
	@if [ -z "$(DIR)" ]; then echo "Error: DIR is not set. Usage: make compile DIR=rnd_papers/paper_1_agentic_mlops/en"; exit 1; fi
	@echo "Compiling $(DIR)/main.tex..."
	@cd $(DIR) && pdflatex -interaction=nonstopmode main.tex || true
	@cd $(DIR) && bibtex main || true
	@cd $(DIR) && pdflatex -interaction=nonstopmode main.tex || true
	@cd $(DIR) && pdflatex -interaction=nonstopmode main.tex || true
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
