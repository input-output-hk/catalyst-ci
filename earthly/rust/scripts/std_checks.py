#!/usr/bin/env python3

# cspell: words stdcfgs

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
    rust_toolchain_enabled=False
    
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Rust high level non-compilation checks processing."
    )

    results = exec_manager.Results("Rust checks")

    # Check config files.
    # Looking for 'Cargo.toml' files
    for root, _, files in os.walk("./"):
        for file_name in files:
            if file_name == "Cargo.toml":
                cargo_toml_path = f"{root}/{file_name}"
                # it should fits one of the template
                res1 = vendor_files_check.toml_diff_check(
                    "/stdcfgs/cargo_manifest/workspace.toml",
                    cargo_toml_path,
                    strict=False,
                    log=False,
                )
                res2 = vendor_files_check.toml_diff_check(
                    "/stdcfgs/cargo_manifest/workspace_inherit.toml",
                    cargo_toml_path,
                    strict=False,
                    log=False,
                )
                res3 = vendor_files_check.toml_diff_check(
                    "/stdcfgs/cargo_manifest/project.toml",
                    cargo_toml_path,
                    strict=False,
                    log=False,
                )
                if not res1.ok() and not res2.ok() and not res3.ok():
                    res1.print(verbose_errors=True)
                    res2.print(verbose_errors=True)
                    res3.print(verbose_errors=True)
                    results.add(res1)
                    results.add(res2)
                    results.add(res3)

    results.add(
        vendor_files_check.toml_diff_check(
            f"/stdcfgs/cargo_config.toml", ".cargo/config.toml"
        )
    )
    if rust_toolchain_enabled:
        results.add(
            vendor_files_check.toml_diff_check(
                "/stdcfgs/rust-toolchain.toml",
                "rust-toolchain.toml",
                strict=False,
            )
        )
    results.add(
        vendor_files_check.toml_diff_check("/stdcfgs/rustfmt.toml", "rustfmt.toml")
    )
    results.add(
        vendor_files_check.toml_diff_check(
            "/stdcfgs/nextest.toml", ".config/nextest.toml"
        )
    )
    results.add(
        vendor_files_check.toml_diff_check("/stdcfgs/clippy.toml", "clippy.toml")
    )
    results.add(vendor_files_check.toml_diff_check("/stdcfgs/deny.toml", "deny.toml"))

    # Check if the rust src is properly formatted.
    res = exec_manager.cli_run("cargo +nightly fmtchk ", name="Rust Code Format Check")
    results.add(res)
    if not res.ok():
        print(
            "[yellow]You can locally fix format errors by running: [/yellow] \n [red bold]cargo +nightly fmtfix [/red bold]"
        )

    # Check if we have unused dependencies declared in our Cargo.toml files.
    results.add(exec_manager.cli_run("cargo machete", name="Unused Dependencies Check"))
    # Check if we have any supply chain issues with dependencies.
    results.add(
        exec_manager.cli_run("cargo deny check --exclude-dev", name="Supply Chain Issues Check")
    )

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
