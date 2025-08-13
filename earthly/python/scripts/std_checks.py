#!/usr/bin/env python3
"""Python Standard Checks."""

import subprocess
import sys
from pathlib import Path


def check_pyproject_toml(*, stand_alone: bool) -> bool:
    """Check if 'pyproject.toml' exists in the project root."""
    if not Path("pyproject.toml").is_file():
        if stand_alone:
            print("pyproject.toml check passed.")
            return True

        print("Error: pyproject.toml not found.")
        return False
    if stand_alone:
        print("Error: pyproject.toml found in standalone python module.")
        return False

    print("pyproject.toml check passed.")
    return True


def check_uv_lock(*, stand_alone: bool) -> bool:
    """Check UV Lock."""
    # Check if 'uv.lock' exists in the project root.
    if not Path("uv.lock").is_file():
        if stand_alone:
            print("uv.lock check passed.")
            return True

        print("Error: uv.lock not found.")
        return False
    if stand_alone:
        print("Error: uv.lock found in stand alone module.")
        return False

    print("uv.lock check passed.")
    return True


def check_lint_with_ruff() -> bool:
    """Check Lint with Ruff."""
    # Check Python code linting issues using 'ruff'.
    result = subprocess.run(["ruff", "check", "."], capture_output=True, check=False)  # noqa: S607
    if result.returncode != 0:
        print("Code linting issues found.")
        print(result.stdout.decode())
        return False
    print("Code linting check passed.")
    return True


def check_lint_with_pyright() -> bool:
    """Check Lint with Pyright."""
    # Check Python code linting issues using 'pyright'.
    result = subprocess.run(["ruff", "check", "."], capture_output=True, check=False)  # noqa: S607
    if result.returncode != 0:
        print("Code linting issues found.")
        print(result.stdout.decode())
        return False
    print("Code linting check passed.")
    return True


def check_code_format_with_ruff() -> bool:
    """Check Code Format with Ruff."""
    # Check Python code formatting and linting issues using 'ruff'.
    result = subprocess.run(["ruff", "format", "--check", "."], capture_output=True, check=False)  # noqa: S607
    if result.returncode != 0:
        print("Code formatting issues found.")
        print(result.stdout.decode())
        return False
    print("Code formatting check passed.")
    return True


def zero_third_party_packages_found(output: str) -> bool:
    """Zero Third Party Packages Found."""
    lines = output.split("\n")  # Split the multiline string into individual lines

    if len(lines) < 2:  # noqa: PLR2004
        return False  # The second line doesn't exist
    return lines[1].startswith("Found '0' third-party package imports")


def main(*, stand_alone: bool) -> None:
    """Python Standard Checks."""
    if stand_alone:
        print("Checking Standalone Python files (No third party imports or poetry project)")
    checks_passed = True
    # Perform checks

    # These are true on python programs that require third party libraries, false otherwise
    checks_passed &= check_pyproject_toml(stand_alone=stand_alone)
    checks_passed &= check_uv_lock(stand_alone=stand_alone)

    # Always done
    checks_passed &= check_lint_with_ruff()
    checks_passed &= check_code_format_with_ruff()

    if not checks_passed:
        sys.exit(1)


if __name__ == "__main__":
    print(f"Current Working Directory: {Path.cwd()}")
    main(stand_alone="--stand-alone" in sys.argv[1:])
