#!/usr/bin/env python3

# cspell: words lcov testdocs nextest testunit depgraph

import python.cli as cli
import argparse
import rich

# This script is run inside the `build` stage.
# Runs all documenation build process.

def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Rust docs build processing."
    )
    parser.add_argument("--libs", default="", help="The list of lib crates `cargo-modules` docs to build separated by comma.")
    parser.add_argument("--bins", default="", help="The list of binaries `cargo-modules` docs to build.")
    args = parser.parse_args()

    results = cli.Results("Rust docs build")

    # Check we can generate all the documentation.
    results.add(cli.run(f"cargo +nightly docs", name="Documentation build"))

    # Generate dependency graphs
    results.add(cli.run(f"cargo depgraph --workspace-only --dedup-transitive-deps > target/doc/workspace.dot",
            name="Workspace dependency graphs generation"))
    results.add(cli.run(f"cargo depgraph --dedup-transitive-deps > target/doc/full.dot",
            name="Full dependency graphs generation"))
    results.add(cli.run(f"cargo depgraph --all-deps --dedup-transitive-deps > target/doc/all.dot",
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