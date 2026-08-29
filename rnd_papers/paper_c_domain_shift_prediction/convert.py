import re
import os

def tex_to_md(tex_file, md_file, bbl_file):
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Parse Title and Author from the preamble
    title_match = re.search(r'\\title\{(.*?)\}', content, re.DOTALL)
    author_match = re.search(r'\\author\{(.*?)\}', content, re.DOTALL)
    
    title_str = ""
    if title_match:
        title = title_match.group(1).replace('\n', ' ').strip()
        title_str = f"# {title}\n\n"
        
    author_str = ""
    if author_match:
        author_text = author_match.group(1).strip()
        # Clean LaTeX lines
        author_lines = [line.strip() for line in author_text.split('\\\\') if line.strip()]
        if len(author_lines) >= 2:
            author_str = f"**Author:** {author_lines[0]} — {author_lines[1]}\n\n"
        else:
            author_str = f"**Author:** {author_lines[0]}\n\n"
        # Unescape LaTeX &
        author_str = author_str.replace('\\&', '&')
        author_str = author_str.replace('\\_', '_')

    # 2. Get body (between \begin{document} and \end{document})
    match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
    if match:
        body_content = match.group(1)
    else:
        body_content = content

    # Remove maketitle
    body_content = re.sub(r'\\maketitle', '', body_content)

    # 3. Parse BBL if exists to map citations to numbers
    citation_keys = []
    bbl_references_block = ""
    if os.path.exists(bbl_file):
        with open(bbl_file, 'r', encoding='utf-8') as f:
            bbl_content = f.read()
        
        # Find all bibitems
        # \bibitem{key} text
        bib_items = re.findall(r'\\bibitem\{(.*?)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})', bbl_content, re.DOTALL)
        if not bib_items:
            # Try single or last item
            bib_items = re.findall(r'\\bibitem\{(.*?)\}(.*)', bbl_content, re.DOTALL)
            
        ref_list = []
        for key, ref_text in bib_items:
            key = key.strip()
            citation_keys.append(key)
            
            ref_text = ref_text.strip()
            # Clean latex tags inside the reference text
            ref_text = re.sub(r'\\newblock', '', ref_text)
            ref_text = re.sub(r'\\em\s+(.*?)(?=\s*\}|\s*\\|\s*$)', r'*\1*', ref_text)
            ref_text = re.sub(r'\{\\em\s+(.*?)\}', r'*\1*', ref_text)
            ref_text = re.sub(r'\\url\{(.*?)\}', r'\1', ref_text)
            ref_text = re.sub(r'\\href\{(.*?)\}\{(.*?)\}', r'[\2](\1)', ref_text)
            ref_text = re.sub(r'\\cite\{(.*?)\}', r'[\1]', ref_text)
            ref_text = re.sub(r'\\&', '&', ref_text)
            ref_text = re.sub(r'\\_', '_', ref_text)
            ref_text = re.sub(r'\{|\}', '', ref_text)
            ref_text = re.sub(r'\s+', ' ', ref_text).strip()
            ref_list.append(ref_text)
            
        if ref_list:
            bbl_references_block = "## References\n\n" + "\n".join(f"{i}. {ref}" for i, ref in enumerate(ref_list, 1))

    # 4. Map citations
    def replace_cite(m):
        keys_in_cite = [k.strip() for k in m.group(1).split(',')]
        mapped = []
        for k in keys_in_cite:
            if k in citation_keys:
                mapped.append(str(citation_keys.index(k) + 1))
            else:
                mapped.append(k)
        return "[" + ", ".join(mapped) + "]"
    
    body_content = re.sub(r'\\cite\{(.*?)\}', replace_cite, body_content)

    # 5. Number and convert sections
    section_counter = 0
    def replace_section(m):
        nonlocal section_counter
        sec_title = m.group(1).strip()
        if "Abstract" in sec_title or "Resumen" in sec_title:
            return f"## {sec_title}"
        section_counter += 1
        return f"## {section_counter}. {sec_title}"

    body_content = re.sub(r'\\section\*?\{(.*?)\}', replace_section, body_content)

    # Convert subsections (with numbers dynamically based on current section_counter)
    subsection_counter = 0
    last_section = 0
    def replace_subsection(m):
        nonlocal subsection_counter, last_section
        if last_section != section_counter:
            subsection_counter = 0
            last_section = section_counter
        subsection_counter += 1
        sub_title = m.group(1).strip()
        return f"### {section_counter}.{subsection_counter} {sub_title}"

    body_content = re.sub(r'\\subsection\*?\{(.*?)\}', replace_subsection, body_content)

    # 6. Basic formatting tags
    body_content = re.sub(r'\\textbf\{(.*?)\}', r'**\1**', body_content)
    body_content = re.sub(r'\\textit\{(.*?)\}', r'*\1*', body_content)
    body_content = re.sub(r'\\Cref\{(.*?)\}', r'\1', body_content)
    body_content = re.sub(r'\\url\{(.*?)\}', r'<\1>', body_content)
    body_content = re.sub(r'\\texttt\{(.*?)\}', r'`\1`', body_content)

    # 7. Convert math equations
    body_content = re.sub(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', r'\n$$\n\1\n$$\n', body_content, flags=re.DOTALL)

    # 8. Tables conversion
    table_counter = 0
    def convert_table(m):
        nonlocal table_counter
        table_counter += 1
        text = m.group(0)
        
        # Caption
        cap_match = re.search(r'\\caption\{(.*?)\}', text)
        caption = cap_match.group(1) if cap_match else ""
        
        # Tabular rows
        rows_match = re.search(r'\\begin\{tabular\}\{.*?\}\s*(.*?)\\end\{tabular\}', text, re.DOTALL)
        if not rows_match:
            return text
        
        tabular = rows_match.group(1)
        lines = tabular.split('\\\\')
        md_lines = []
        is_header = True
        for line in lines:
            line = line.strip()
            line = re.sub(r'\\toprule|\\midrule|\\bottomrule', '', line).strip()
            if not line:
                continue
            cols = [re.sub(r'\\multicolumn\{.*?\}\{.*?\}\{(.*?)\}', r'\1', c.strip()) for c in line.split('&')]
            cols = [c.replace('\\$', '$').strip() for c in cols]
            # Replace LaTeX bold/italic inside table cell
            cols = [re.sub(r'\\textbf\{(.*?)\}', r'**\1**', c) for c in cols]
            cols = [re.sub(r'\\textit\{(.*?)\}', r'*\1*', c) for c in cols]
            
            md_lines.append("| " + " | ".join(cols) + " |")
            if is_header:
                md_lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
                is_header = False
                
        table_md = "\n".join(md_lines)
        # Fix double column or other tabular latex tags
        table_md = table_md.replace('\\midrule', '')
        
        # Determine table label prefix based on language
        label_prefix = "**Table" if "Predictive" in caption or "Ablation" in caption or "en" in tex_file else "**Tabla"
        
        if caption:
            return f"\n{label_prefix} {table_counter}.** {caption}\n\n{table_md}\n"
        return f"\n{table_md}\n"

    body_content = re.sub(r'\\begin\{table\}.*?\\end\{table\}', convert_table, body_content, flags=re.DOTALL)

    # 9. Figures conversion
    def convert_figure(m):
        text = m.group(0)
        cap_match = re.search(r'\\caption\{(.*?)\}', text)
        caption = cap_match.group(1) if cap_match else "Figure"
        
        fig_match = re.search(r'\\graphicx\[.*?\]\{(.*?)\}', text)
        if not fig_match:
            fig_match = re.search(r'\\includegraphics\[.*?\]\{(.*?)\}', text)
            
        fig_path = fig_match.group(1) if fig_match else "figures/prediction.pdf"
        return f"\n![{caption}]({fig_path})\n"

    body_content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', convert_figure, body_content, flags=re.DOTALL)

    # 10. Abstract / Keywords block formatting
    # Replace \textbf{Abstract:} with bold title and newlines
    body_content = re.sub(r'\\textbf\{Abstract:\}\s*(.*?)(?=\n\n|\\textbf\{Keywords:\})', r'\1', body_content, flags=re.DOTALL)
    body_content = re.sub(r'\\textbf\{Resumen:\}\s*(.*?)(?=\n\n|\\textbf\{Palabras Clave:\})', r'\1', body_content, flags=re.DOTALL)
    
    # 11. Cleanup enumerates
    body_content = re.sub(r'\\begin\{enumerate\}', '', body_content)
    body_content = re.sub(r'\\end\{enumerate\}', '', body_content)
    body_content = re.sub(r'\\item\s+', r'1. ', body_content) # let markdown engine auto-number them or use 1.

    # 12. Cleanup remaining LaTeX commands
    body_content = re.sub(r'\\bibliographystyle\{.*?\}', '', body_content)
    body_content = re.sub(r'\\bibliography\{.*?\}', '', body_content)
    body_content = re.sub(r'\\%', '%', body_content)
    body_content = re.sub(r'\\&', '&', body_content)
    
    # Combine title, author, line rule, and body
    divider = "---\n\n"
    final_content = f"{title_str}{author_str}{divider}{body_content.strip()}"

    # If bbl has references, append them (only if "References" / "Referencias" is not already in text)
    if bbl_references_block:
        # Remove any existing \bibliography or References placeholder text
        final_content = re.sub(r'##\s*(?:References|Referencias).*', '', final_content, flags=re.DOTALL)
        final_content = final_content.strip() + "\n\n" + bbl_references_block

    # Clean multiple empty lines
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + "\n")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Since .bbl files are generated inside the compilation directories (which are en/ and es/)
    # let's look for them there.
    tex_to_md(
        os.path.join(script_dir, 'en/main.tex'),
        os.path.join(script_dir, 'en/main.md'),
        os.path.join(script_dir, 'en/main.bbl')
    )
    tex_to_md(
        os.path.join(script_dir, 'es/main.tex'),
        os.path.join(script_dir, 'es/main.md'),
        os.path.join(script_dir, 'es/main.bbl')
    )
