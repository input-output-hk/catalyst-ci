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
            this_file = Path(env.page.file.src_dir) / env.page.file.src_dir
            this_dir = this_file.parent
            relative_filename = this_dir / filename
        else:
            project_dir = Path(env.project_dir)
            relative_filename = project_dir / filename

        # Make sure file being referenced is not relative anymore.
        full_filename = relative_filename.resolve()

        # Get the lines we are including.
        lines = full_filename.read_text().splitlines()
        line_range = lines[start_line:end_line]
        text = f"\n{' ' * indent}".join(line_range).rstrip()
        return re.sub(r"\n$", "", text, count=1)
    except Exception as exc:  # noqa: BLE001
        return f"{filename} error: {exc}"
