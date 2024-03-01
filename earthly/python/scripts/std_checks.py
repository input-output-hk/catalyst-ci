#!/usr/bin/env python3

import os
import subprocess
import sys

def check_pyproject_toml():
    # Check if 'pyproject.toml' exists in the project root.
    if not os.path.isfile('pyproject.toml'):
        print("Error: pyproject.toml not found.")
        return False
    else:
        print("pyproject.toml check passed.")
        return True
    
def check_poetry_lock():
    # Check if 'poetry.lock' exists in the project root.
    if not os.path.isfile('poetry.lock'):
        print("Error: poetry.lock not found.")
        return False
    else:
        print("poetry.lock check passed.")
        return True

def check_code_format_with_ruff():
    # Check Python code formatting and linting issues using 'ruff'.
    result = subprocess.run(['ruff', 'check', '.'], capture_output=True)
    if result.returncode != 0:
        print("Code formatting and linting issues found.")
        print(result.stdout.decode())
        return False
    else:
        print("Code formatting and linting check passed.")
        return True

def main():
    checks_passed = True
    # Perform checks
    checks_passed &= check_pyproject_toml()
    checks_passed &= check_poetry_lock()
    checks_passed &= check_code_format_with_ruff()

    if not checks_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
