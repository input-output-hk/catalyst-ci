#!/usr/bin/env python3

import python.exec_manager as exec_manager
import python.vendor_files_check as vendor_files_check
import argparse
import rich
from rich import print
import os

# This script is run inside the `check` stage for postgres database setup
# to perform all high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `build`.
# Individual targets can add extra `check` steps, but these checks must always
# pass.

# This is set up so that ALL checks are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `check`
# to pass without needing to iterate excessively.


def sqlfluff(results: exec_manager.Results, path: str):
    results.add(
        exec_manager.cli_run(
            " ".join(["sqlfluff lint", "-vv", path]),
            name=f"Checking SQLFluff linter against files from: {path}",
        )
    )


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(description="Postgres checks processing.")

    results = exec_manager.Results("Postgres checks")

    results.add(
        vendor_files_check.colordiff_check(
            "/sql/.sqlfluff",
            ".sqlfluff",
        )
    )

    sqlfluff(results, "/sql")
    sqlfluff(results, ".")

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
