"""Include Contents of one file in another file."""

import re
from pathlib import Path


def inc_file(
    env: any,
    filename: str,
    *,
    start_line: int = 0,
    end_line: int | None = None,
    indent: int = 0,
) -> str:
    """Include a file, optionally indicating start_line and end_line (start counting from 0).

    filename =
        If the filename begins with a '.' then
          the file is relative to the file containing the `include`
        Otherwise the path is relative to
          the top directory of the documentation project.
    start_line = The first line to include (0 = Start of file).
    end_line = The last line to include (None = End of file)
    indent = number of spaces to indent every line but the first.
    """
    try:
        if filename.startswith("."):
            this_file = Path(env.page.file.src_dir) / env.page.file.src_uri
            this_dir = this_file.parent
            relative_filename = this_dir / filename
        else:
            this_file = "Absolute"
            this_dir = "Not Calculated"
            project_dir = Path(env.project_dir)
            relative_filename = project_dir / filename

        # Make sure file being referenced is not relative anymore.
        full_filename = relative_filename.resolve()

        # Get the lines we are including.
        lines = full_filename.read_text().splitlines()
        line_range = lines[start_line:end_line]
        text = f"\n{' ' * indent}".join(line_range).rstrip()
    except Exception as exc:  # noqa: BLE001
        text = f"{filename} error: {exc}"

    # Debug Values
    # text += f"\n{' ' * indent}filename = {filename}"  # noqa: ERA001
    # text += f"\n{' ' * indent}this_file = {this_file}"  # noqa: ERA001
    # text += f"\n{' ' * indent}this_dir = {this_dir}"  # noqa: ERA001
    # text += f"\n{' ' * indent}relative_file = {relative_filename}"  # noqa: ERA001
    # text += f"\n{' ' * indent}full_filename = {full_filename}"  # noqa: ERA001
    return re.sub(r"\n$", "", text, count=1)
