#!/usr/bin/env python3

# cspell: words lcov testdocs nextest testunit depgraph

import python.cli as cli
import argparse
import rich

# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.

def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Rust build processing."
    )
    parser.add_argument("--target", default="", help="Pass rust --target flag (cargo --target flag).")
    parser.add_argument("--cov_report", default="", help="The output coverage report file path.")
    parser.add_argument("--with_bench", default="false", help="Running benchmarks")
    args = parser.parse_args()

    results = cli.Results("Rust build")

    target_flag = ""
    if args.target != "":
        target_flag += f" --target={args.target} "

    # Build the code.
    results.add(cli.run("cargo build " \
                        f"{target_flag} " \
                        "--release ",
                    name="Build all code in the workspace"))
    # Check the code passes all clippy lint checks.
    results.add(cli.run("cargo lint",
                    name="Clippy Lints in the workspace check"))
    # Check if all documentation tests pass.
    results.add(cli.run("cargo +nightly testdocs ",
                    name="Documentation tests all pass check"))

    # Check if all Self contained tests pass (Test that need no external resources).
    if args.cov_report == "":
        results.add(cli.run("cargo testunit" \
                            f"{target_flag} ",
                        name="Self contained Unit tests all pass check"))
    
    # Save coverage report to file if it is provided
    else:
        # Remove artifacts that may affect the coverage results
        res = cli.run("cargo llvm-cov clean",
                name="Remove artifacts that may affect the coverage results")
        results.add(res)
        # Run unit tests and generates test and coverage report artifacts
        if res.ok():
            res = cli.run("cargo llvm-cov nextest " \
                        f"{target_flag} " \
                        "--release " \
                        "--bins " \
                        "--lib " \
                        "-P ci ",
                    name="Self contained Unit tests and collect coverage")
            if not res.ok():
                print(f"[yellow]You can locally run tests by running: [/yellow] \n [red bold]cargo testunit {target_flag}[/red bold]")
            results.add(res)
    
        # Save coverage report to file if it is provided
        if res.ok():
            res = cli.run("cargo llvm-cov report " \
                        f"{target_flag} " \
                        "--release " \
                        f"--output-path {args.cov_report} ",
                    name=f"Generate lcov report to {args.cov_report}")
            results.add(res)

    # Check if any benchmarks defined run (We don;t validate the results.)
    if args.with_bench == "true":
        results.add(cli.run(f"cargo bench --all-targets {target_flag}",
                name="Benchmarks all run to completion check"))

    results.print()
    if not results.ok():
        exit(1)

if __name__ == "__main__":
    main()