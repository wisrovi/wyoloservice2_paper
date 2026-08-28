import re
import os

def tex_to_md(tex_file, md_file):
    with open(tex_file, 'r') as f:
        content = f.read()

    # Get body (between \begin{document} and \end{document})
    match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
    if match:
        content = match.group(1)
    
    # Strip some LaTeX tags
    content = re.sub(r'\\section\{(.*?)\}', r'## \1', content)
    content = re.sub(r'\\subsection\{(.*?)\}', r'### \1', content)
    content = re.sub(r'\\textbf\{(.*?)\}', r'**\1**', content)
    content = re.sub(r'\\textit\{(.*?)\}', r'*\1*', content)
    content = re.sub(r'\\cite\{(.*?)\}', r'[\1]', content)
    content = re.sub(r'\\Cref\{(.*?)\}', r'\1', content)
    content = re.sub(r'\\url\{(.*?)\}', r'<\1>', content)
    content = re.sub(r'\\texttt\{(.*?)\}', r'`\1`', content)
    
    # Tables and Figures
    content = re.sub(r'\\begin\{table\}.*?\\end\{table\}', r'> Table goes here', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', r'> Figure goes here\n![Architecture](figures/architecture.pdf)', content, flags=re.DOTALL)
    
    # Title and author
    content = re.sub(r'\\title\{(.*?)\}', r'# \1\n', content)
    content = re.sub(r'\\author\{.*?\}', r'**Author:** William Steve Rodriguez Villamizar', content, flags=re.DOTALL)
    content = re.sub(r'\\maketitle', r'', content)
    
    # Abstract
    content = re.sub(r'\\begin\{abstract\}', r'**Abstract:** ', content)
    content = re.sub(r'\\end\{abstract\}', r'', content)
    content = re.sub(r'\\begin\{IEEEkeywords\}', r'**Keywords:** ', content)
    content = re.sub(r'\\end\{IEEEkeywords\}', r'', content)
    
    # Others
    content = re.sub(r'\\IEEEauthorblockN\{.*?\}', r'', content)
    content = re.sub(r'\\IEEEauthorblockA\{.*?\}', r'', content)
    content = re.sub(r'\\begin\{enumerate\}', r'', content)
    content = re.sub(r'\\end\{enumerate\}', r'', content)
    content = re.sub(r'\\item', r'-', content)
    content = re.sub(r'\\bibliographystyle\{.*?\}', r'', content)
    content = re.sub(r'\\bibliography\{.*?\}', r'', content)
    content = re.sub(r'\\$', r'', content)
    content = re.sub(r'\$', r'', content)
    content = re.sub(r'\\%', r'%', content)
    
    # Clean up empty lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(md_file, 'w') as f:
        f.write(content.strip())

script_dir = os.path.dirname(os.path.abspath(__file__))
tex_to_md(os.path.join(script_dir, 'en/main.tex'), os.path.join(script_dir, 'en/main.md'))
tex_to_md(os.path.join(script_dir, 'es/main.tex'), os.path.join(script_dir, 'es/main.md'))

