#!/usr/bin/env python3

# cspell: words

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
    parser.add_argument("--cov_report", help="Lcov report file.")
    parser.add_argument("--libs", help="The list of lib crates `cargo-modules` docs to build separated by comma.")
    parser.add_argument("--bins", help="The list of binaries `cargo-modules` docs to build.")
    args = parser.parse_args()

    results = cli.Results("Rust builds")

    # Build the code.
    results.add(cli.run("cargo build --release --workspace --locked", name="Build all code in the workspace"))
    # # Check the code passes all clippy lint checks.
    # results.add(cli.run("cargo lint", name="Clippy Lints in the workspace check"))
    # Check we can generate all the documentation.
    results.add(cli.run("cargo docs", name="Documentation can be generated OK check"))
    # Check if all documentation tests pass.
    results.add(cli.run("cargo testdocs", name="Documentation tests all pass check"))
    # Check if any benchmarks defined run (We don;t validate the results.)
    results.add(cli.run("cargo bench --all-targets", name="Benchmarks all run to completion check"))

    # Run unit tests and generates test and coverage report artifacts
    res = cli.run("cargo llvm-cov clean --workspace", name="Remove artifacts that may affect the coverage results")
    results.add(res)
    if res.ok():
        res = cli.run("cargo llvm-cov nextest --release --bins --lib --workspace --locked -P ci",
            name="Run unit tests and display test result and test coverage")
        if not res.ok():
            print("[yellow]You can locally run tests by running: [/yellow] \n [red bold]cargo testunit[/red bold]")
        results.add(res)

    # Save coverage report to file if it is provided
    if res.ok() and args.cov_report != "":
        res = cli.run(f"cargo llvm-cov report --release --output-path {args.cov_report}",
            name=f"Generate lcov report to {args.cov_report}")
        results.add(res)

    # Generate dependency graphs
    results.add(cli.run("cargo depgraph --workspace-only --dedup-transitive-deps > target/doc/workspace.dot",
            name="Workspace dependency graphs generation"))
    results.add(cli.run("cargo depgraph --dedup-transitive-deps > target/doc/full.dot",
            name="Full dependency graphs generation"))
    results.add(cli.run("cargo depgraph --all-deps --dedup-transitive-deps > target/doc/all.dot",
            name="All dependency graphs generation"))

    for lib in filter(lambda lib: lib != "", args.libs.split(", ")):
        results.add(cli.run('NO_COLOR=1 ' \
                'cargo modules generate tree --orphans --types --traits --tests --all-features ' \
                f'--package "{lib}" --lib > "target/doc/{lib}.lib.modules.tree"',

                name=f"Generate Module Trees for {lib}")
                )

        results.add(cli.run('NO_COLOR=1 ' \
                'cargo modules generate graph --all-features --modules ' \
                f'--package "{lib}" --lib > "target/doc/{lib}.lib.modules.dot"',

                name=f"Generate Module Graphs for {lib}")
                )

    for bin in filter(lambda bin: bin != "", args.bins.split(", ")):
        package, bin = bin.split('/')
        results.add(cli.run('NO_COLOR=1 ' \
                'cargo modules generate tree --orphans --types --traits --tests --all-features ' \
                f'--package "{package}" --bin "{bin}" > "target/doc/{package}.{bin}.bin.modules.tree"',

                name=f"Generate Module Trees for {package}/{bin}")
                )

        results.add(cli.run('NO_COLOR=1 ' \
                'cargo modules generate graph --all-features --modules ' \
                f'--package "{package}" --bin "{bin}" > "target/doc/{package}.{bin}.bin.modules.dot"',

                name=f"Generate Module Graphs for {package}/{bin}")
                )

    results.print()
    if not results.ok():
        exit(1)

if __name__ == "__main__":
    main()