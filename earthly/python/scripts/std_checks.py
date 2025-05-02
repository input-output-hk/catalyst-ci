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


def check_poetry_lock(*, stand_alone: bool) -> bool:
    """Check Poetry Lock."""
    # Check if 'poetry.lock' exists in the project root.
    if not Path("poetry.lock").is_file():
        if stand_alone:
            print("poetry.lock check passed.")
            return True

        print("Error: poetry.lock not found.")
        return False
    if stand_alone:
        print("Error: poetry.lock found in stand alone module.")
        return False

    print("poetry.lock check passed.")
    return True


def check_lint_with_ruff() -> bool:
    """Check Lint with Ruff."""
    # Check Python code linting issues using 'ruff'.
    result = subprocess.run(["ruff", "check", "."], capture_output=True, check=False)  # noqa: S603, S607
    if result.returncode != 0:
        print("Code linting issues found.")
        print(result.stdout.decode())
        return False
    print("Code linting check passed.")
    return True


def check_code_format_with_ruff() -> bool:
    """Check Code Format with Ruff."""
    # Check Python code formatting and linting issues using 'ruff'.
    result = subprocess.run(["ruff", "format", "--check", "."], capture_output=True, check=False)  # noqa: S603, S607
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


def check_no_third_party_imports() -> bool:
    """Check No Third Party Imports."""
    # Check No third party imports have been used
    result = subprocess.run(["third-party-imports", "."], capture_output=True, check=False)  # noqa: S603, S607
    output = result.stdout.decode()

    if result.returncode != 0 or not zero_third_party_packages_found(output):
        print("Checking third party imports failed.")
        print(output)
        return False
    print("Checking third party imports passed.")
    return True


def main(*, stand_alone: bool) -> None:
    """Python Standard Checks."""
    if stand_alone:
        print("Checking Standalone Python files (No third party imports or poetry project)")
    checks_passed = True
    # Perform checks

    # These are true on python programs that require third party libraries, false otherwise
    checks_passed &= check_pyproject_toml(stand_alone=stand_alone)
    checks_passed &= check_poetry_lock(stand_alone=stand_alone)

    # Always done
    checks_passed &= check_lint_with_ruff()
    checks_passed &= check_code_format_with_ruff()

    # Only done if the code should be able to run without third part libraries
    if stand_alone:
        checks_passed &= check_no_third_party_imports()

    if not checks_passed:
        sys.exit(1)


if __name__ == "__main__":
    print(f"Current Working Directory: {Path.cwd()}")
    main(stand_alone="--stand-alone" in sys.argv[1:])
