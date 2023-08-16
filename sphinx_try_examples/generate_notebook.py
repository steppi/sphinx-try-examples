import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell
import re


def generate_notebook(input_lines):
    nb = nbf.v4.new_notebook()

    code_lines = []
    md_lines = []
    output_line = None

    for line in input_lines:
        line = line.strip()
        if line.startswith('>>>'):
            # This line is code
            # If there is any pending markdown text, add it to the notebook
            if md_lines:
                md_text = '\n'.join(md_lines)
                # Map rst latex directive to $ so latex renders in notebook.
                md_text = re.sub(r':math:`(?P<latex>.*?)`', r'$\g<latex>$', md_text)
                nb.cells.append(new_markdown_cell(md_text))
                md_lines = []  # Reset markdown lines
            # Add this line to the code
            code_lines.append(line[4:])  # Remove '>>> ' prefix
        elif line.strip() == '' and code_lines:
            # This line is blank, so it is the end of a code cell
            # If there is any pending code, add it to the notebook
            code_text = '\n'.join(code_lines)
            cell = new_code_cell(code_text)
            if output_line is not None:
                cell.outputs.append(nbf.v4.new_output(output_type="execute_result", 
                                                       data={"text/plain": output_line}))
                output_line = None
            nb.cells.append(cell)
            code_lines = []  # Reset code lines
        elif code_lines:
            # This line is the output of the previous code cell
            output_line = line
        else:
            # This line is markdown
            md_lines.append(line)

    # If there is any pending markdown or code, add it to the notebook
    if md_lines:
        md_text = '\n'.join(md_lines)
        # Map rst latex directive to $ so latex renders in notebook.
        md_text = re.sub(r':math:`(?P<latex>.*?)`', r'$\g<latex>$', md_text)
        nb.cells.append(new_markdown_cell(md_text))
    if code_lines:
        code_text = '\n'.join(code_lines)
        cell = new_code_cell(code_text)
        if output_line is not None:
            cell.outputs.append(nbf.v4.new_output(output_type="execute_result", 
                                                   data={"text/plain": output_line}))
        nb.cells.append(cell)
    return nb
