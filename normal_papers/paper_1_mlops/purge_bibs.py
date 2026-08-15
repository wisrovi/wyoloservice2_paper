import os
import re

def purge_bib(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove the 3 unused refs
    content = re.sub(r'@inproceedings\{moritz2018ray,.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'@article\{hansen2016cma,.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'@inproceedings\{falkner2018bohb,.*?\}', '', content, flags=re.DOTALL)
    
    with open(filepath, 'w') as f:
        f.write(content)

purge_bib('en/references.bib')
purge_bib('es/references.bib')
