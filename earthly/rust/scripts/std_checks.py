#!/usr/bin/env python3

# cspell: words depgraph fmtchk fmtfix colordiff stdcfgs rustfmt stdcfgs nextest

import python.exec_manager as exec_manager
import python.vendor_files_check as vendor_files_check
import argparse
import rich
from rich import print
import os

# This script is run inside the `check` stage for rust projects to perform all
# high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `build`.
# Individual targets can add extra `check` steps, but these checks must always
# pass.

# This is set up so that ALL checks are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `check`
# to pass without needing to iterate excessively.


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Rust high level non-compilation checks processing."
    )

    results = exec_manager.Results("Rust checks")

    # Check if the rust src is properly formatted.
    res = exec_manager.cli_run("cargo +nightly fmtchk ", name="Rust Code Format Check")
    results.add(res)
    if not res.ok():
        print(
            "[yellow]You can locally fix format errors by running: [/yellow] \n [red bold]cargo +nightly fmtfix [/red bold]"
        )

    # Check config files.
    results.add(
        vendor_files_check.toml_diff_strict_check(
            f"{os.environ.get('CARGO_HOME')}/config.toml", ".cargo/config.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_non_strict_check(
            "/stdcfgs/rust-toolchain.toml", "rust-toolchain.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_non_strict_check(
            "/stdcfgs/rustfmt.toml", "rustfmt.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_non_strict_check(
            "/stdcfgs/nextest.toml", ".config/nextest.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_non_strict_check(
            "/stdcfgs/clippy.toml", "clippy.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_non_strict_check("/stdcfgs/deny.toml", "deny.toml")
    )

    # Check if we have unused dependencies declared in our Cargo.toml files.
    results.add(exec_manager.cli_run("cargo machete", name="Unused Dependencies Check"))
    # Check if we have any supply chain issues with dependencies.
    results.add(
        exec_manager.cli_run("cargo deny check", name="Supply Chain Issues Check")
    )

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
