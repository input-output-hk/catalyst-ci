#!/usr/bin/env python3

# cspell: words lcov testdocs nextest testunit depgraph testcov readelf

import python.cli as cli
import argparse
import rich

# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.

def cargo_build(results: cli.Results, flags: str):
    results.add(cli.run("cargo build "
                        + f"{flags} "
                        + "--release ",
                    name="Build all code in the workspace"))

def cargo_clippy(results: cli.Results):
    results.add(cli.run("cargo lint ",
                    name="Clippy Lints in the workspace check"))

def cargo_doctest(results: cli.Results, flags: str):
    results.add(cli.run("cargo testdocs "
                        + f"{flags} ",
                    name="Documentation tests all pass check"))

def cargo_nextest(results: cli.Results, flags: str):
    results.add(cli.run("cargo testunit "
                        + f"{flags} ",
                    name="Self contained Unit tests all pass check"))

def cargo_llvm_cov(results: cli.Results, flags: str, cov_report: str):
    # Remove artifacts that may affect the coverage results
    res = cli.run("cargo llvm-cov clean",
                name="Remove artifacts that may affect the coverage results")
    results.add(res)
    # Run unit tests and generates test and coverage report artifacts
    if res.ok():
        res = cli.run("cargo testcov "
                    + f"{flags} ",
                name="Self contained Unit tests and collect coverage")
        results.add(res)
    # Save coverage report to file if it is provided
    if res.ok():
        res = cli.run("cargo llvm-cov report "
                    + f"{flags} "
                    + "--release "
                    + f"--output-path {cov_report} ",
                name=f"Generate lcov report to {cov_report}")
        results.add(res)

def cargo_bench(results: cli.Results, flags: str):
    results.add(cli.run("cargo bench "
                        + f"{flags} "
                        + "--all-targets ",
                    name="Benchmarks all run to completion check"))

def cargo_doc(results: cli.Results):
    results.add(cli.run("cargo +nightly docs ",
            name="Documentation build"))

def cargo_depgraph(results: cli.Results):
    results.add(cli.run("cargo depgraph "
                        + "--workspace-only "
                        + "--dedup-transitive-deps "
                        + "> target/doc/workspace.dot ",
                name="Workspace dependency graphs generation"))
    results.add(cli.run("cargo depgraph "
                        + "--dedup-transitive-deps "
                        + "> target/doc/full.dot ",
                name="Full dependency graphs generation"))
    results.add(cli.run("cargo depgraph "
                        + "--all-deps "
                        + "--dedup-transitive-deps "
                        + "> target/doc/all.dot ",
                name="All dependency graphs generation"))

def cargo_modules_lib(results: cli.Results, lib: str):
    # Generate tree
    results.add(cli.run("NO_COLOR=1 "
                        + "cargo modules generate tree --orphans --types --traits --tests --all-features "
                        + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.tree' ",
                    name=f"Generate Module Trees for {lib}"))
    # Generate graph
    results.add(cli.run("NO_COLOR=1 "
                        + "cargo modules generate graph --all-features --modules "
                        + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.dot' ",
                    name=f"Generate Module Graphs for {lib}"))

def cargo_modules_bin(results: cli.Results, package: str, bin: str):
    # Generate tree
    results.add(cli.run("NO_COLOR=1 "
                        + "cargo modules generate tree --orphans --types --traits --tests --all-features "
                        + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.tree' ",
                    name=f"Generate Module Trees for {package}/{bin}"))
    # Generate graph
    results.add(cli.run("NO_COLOR=1 "
                        + "cargo modules generate graph --all-features --modules "
                        + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.dot' ",
                    name=f"Generate Module Graphs for {package}/{bin}"))

# ALL executables MUST have `--help` as an option.
def help_check(results: cli.Results, bin: str):
    results.add(cli.run(f"target/release/{bin} --help",
                    name=f"Executable '{bin}' MUST have `--help` as an option."))

def ldd(results: cli.Results, bin: str):
    results.add(cli.run(f"ldd target/release/{bin}",
                    name=f"ldd for '{bin}'",
                    verbose=True))

def readelf(results: cli.Results, bin: str):
    results.add(cli.run(f"readelf -p .comment target/release/{bin}",
                    name=f"readelf for '{bin}'",
                    verbose=True))

def strip(results: cli.Results, bin: str):
    results.add(cli.run(f"strip -v target/release/{bin}",
                    name=f"strip for '{bin}'",
                    verbose=True))

def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Rust build processing."
    )
    parser.add_argument("--build_flags", default="", help="Additional command-line flags that can be passed to the `cargo build` command.")
    parser.add_argument("--doctest_flags", default="", help="Additional command-line flags that can be passed to the `cargo testdocs` command.")
    parser.add_argument("--test_flags", default="", help="Additional command-line flags that can be passed to the `cargo testunit` command.")
    parser.add_argument("--bench_flags", default="", help="Additional command-line flags that can be passed to the `cargo bench` command.")
    parser.add_argument("--with_test", action='store_true', help="Flag to indicate whether to run tests (including unit tests and doc tests).")
    parser.add_argument("--cov_report", default="", help="The output coverage report file path. If omitted, coverage will not be run.")
    parser.add_argument("--with_bench", action='store_true', help="Flag to indicate whether to run benchmarks.")
    parser.add_argument("--libs", default="", help="The list of lib crates `cargo-modules` docs to build separated by comma.")
    parser.add_argument("--bins", default="", help="The list of binaries `cargo-modules` docs to build and made a smoke tests on them.")
    args = parser.parse_args()

    libs = filter(lambda lib: lib != "", args.libs.split(", "))
    bins = list(filter(lambda bin: bin != "", args.bins.split(", ")))

    results = cli.Results("Rust build")
    # Build the code.
    cargo_build(results, args.build_flags)
    # Check the code passes all clippy lint checks.
    cargo_clippy(results)
    # Check if all Self contained tests pass (Test that need no external resources).
    if args.with_test:
        # Check if all documentation tests pass.
        cargo_doctest(results, args.doctest_flags)
        if args.cov_report == "":
            # Without coverage report
            cargo_nextest(results, args.test_flags)
        else:
            # With coverage report
            cargo_llvm_cov(results, args.test_flags, args.cov_report)

    # Check if any benchmarks defined run (We don't validate the results.)
    if args.with_bench:
        cargo_bench(results, args.bench_flags)

    # Generate all the documentation.
    cargo_doc(results)
    # Generate dependency graphs
    cargo_depgraph(results)

    for lib in libs:
        cargo_modules_lib(results, lib)

    for bin in bins:
        package, bin_name = bin.split('/')
        cargo_modules_bin(results, package, bin_name)

    results.print()
    if not results.ok():
        exit(1)

    # Check if the build executable, isn't a busted mess.
    results = cli.Results("Smoke test")

    for bin in bins:
        _, bin_name = bin.split('/')
        help_check(results, bin_name)
        ldd(results, bin_name)
        readelf(results, bin_name)
        strip(results, bin_name)

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()