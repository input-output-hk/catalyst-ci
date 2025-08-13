#!/usr/bin/env -S uv run

import json
import sys
from pathlib import Path
from typing import Any
from sh import pyright  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]
from rich.markup import escape
from rich import print
import sh

IGNORE_DIRS = {".venv", "env", "build"}  # add any folder names you want to ignore


def find_lowest_py_dirs(root: Path) -> list[Path]:
    """
    Returns a list of directories under `root` that contain .py files,
    but none of their subdirectories contain .py files.
    """
    root = root.resolve()
    lowest_dirs: list[Path] = []

    def has_py_files(p: Path):
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            return False
        return any(f.suffix == ".py" for f in p.iterdir() if f.is_file())

    def recurse(dir_path: Path) -> None:
        # Check if any subdirectory has python files
        if has_py_files(dir_path):
            lowest_dirs.append(dir_path)
            return

        for child in dir_path.iterdir():
            if child.is_dir():
                recurse(child)

    recurse(root)
    return lowest_dirs


def display_errors(errors: dict[str, Any]) -> None:
    """Display Pyright Errors."""
    all_errors = errors["generalDiagnostics"]
    file_errors: dict[str, list[dict[str, Any]]] = {}

    # Group all errors by file.
    for error in all_errors:
        file = error["file"]
        if file not in file_errors:
            file_errors[file] = []
        file_errors[file].append(error)

    for file, error_list in file_errors.items():
        print(f"[bold]{file}[/]")
        for error in error_list:
            message = error["message"].replace("\n", ".")
            print(f"    [yellow]{error['range']['start']['line']:>3}[/yellow]:", end="")
            print(f"[yellow]{error['range']['start']['character']:<3}[/yellow]: ", end="")
            print(f"[red]{message}[/red] ", end="")
            print(f"[magenta]({error['rule']})[/magenta] ")


def check_with_pyright(target_dir: Path) -> bool:
    print(f"[blue]Checking Python code with pyright at: [bold]{escape(str(target_dir))}[/] : ", end="")

    if (target_dir / ".skip_pyright").exists():
        print(":yellow_circle: [yellow]Skipped[/]")
        return True

    msg: str | None = ""
    error: dict[str, Any] | None = None

    try:
        # run pyright with cwd set to the target directory
        output = str(pyright(["--outputjson", "."], _cwd=str(target_dir)))  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
        data = json.loads(output)
        print(f":heavy_check_mark: (Files: {data['summary']['filesAnalyzed']})")
        return True
    except sh.ErrorReturnCode as e:
        msg = f"[red]Pyright exited with an error (code {e.exit_code}):[/]"  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        error = json.loads(e.stdout.decode())  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportAttributeAccessIssue]
    except FileNotFoundError:
        pass
        msg = "[red]Error:[/] pyright is not installed. See: https://microsoft.github.io/pyright/#/installation"
        pass
    except Exception as e:
        msg = f"[red]Error:[/] Error running pyright: {e}."

    print(":cross_mark:")
    print(msg)
    if error is not None:
        display_errors(error)
    return False


def main(root_dir: str):
    root = Path(root_dir).resolve()
    if not root.is_dir():
        print(f"[red]Error:[/] '{escape(str(root))}' is not a directory.")
        sys.exit(1)

    print(f"[cyan]Searching for directories containing Python files under[/] [bold]{escape(str(root))}[/] ...")

    target_dirs = find_lowest_py_dirs(root)
    if len(target_dirs) == 0:
        print("[yellow]No directory with Python files found.[/]")
        # Not an error
        sys.exit(0)

    print(target_dirs)

    count = 0
    for target in target_dirs:
        if not check_with_pyright(target):
            count = count + 1

    if count > 0:
        print(f"[red]Pyright Lint checked Failed on {count} directories.[/]")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"[red]Usage:[/] {escape(sys.argv[0])} <root-directory>")
        sys.exit(1)
    main(sys.argv[1])
