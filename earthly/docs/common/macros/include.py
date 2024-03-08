import os
import textwrap
import re

def inc_file(env, filename, start_line=0, end_line=None, indent=None):
    """
    Include a file, optionally indicating start_line and end_line
    (start counting from 0)
    The path is relative to the top directory of the documentation
    project.
    indent = number of spaces to indent every line but the first.
    """
    
    try:
        full_filename = os.path.join(env.project_dir, filename)

        with open(full_filename, "r") as f:
            lines = f.readlines()
        line_range = lines[start_line:end_line]
        text = "".join(line_range)
        # print(text)
        if indent is None:
            indent = ""
        else:
            indent = " " * indent
        text = textwrap.indent(text, indent)
        text = text[len(indent):] # First line should not be indented at all.
        text = re.sub(r'\n$', '', text, count=1)
        # print(text)
        return text
    except Exception as exc:
        return f"{filename} error: {exc}"
