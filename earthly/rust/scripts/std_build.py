#!/usr/bin/env python3

# cspell: words lcov depgraph readelf sysroot

import concurrent.futures
import time
import os

import argparse
import rich

import python.exec_manager as exec_manager

# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.


def cargo_build(flags: str, verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo build " + "--release " + f"{flags} ",
        name="Build all code in the workspace",
        verbose=verbose,
    )


def cargo_lint(flags: str, verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo lint --release " + f"{flags}",
        name="Clippy Lints in the workspace check",
        verbose=verbose,
    )


def cargo_doctest(flags: str, verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo +nightly testdocs " + f"{flags} ",
        name="Documentation tests all pass check",
        verbose=verbose,
    )


def cargo_nextest(flags: str, verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo testunit " + f"{flags} ",
        name="Self contained Unit tests all pass check",
        verbose=verbose,
    )


def cargo_llvm_cov(
    flags: str, cov_report: str, verbose: bool = False
) -> list[exec_manager.Result]:
    # These can not be run in parallel as they depend on each other
    results = []
    # Remove artifacts that may affect the coverage results
    res = exec_manager.cli_run(
        "cargo llvm-cov clean",
        name="Remove artifacts that may affect the coverage results",
        verbose=verbose,
    )
    results.append(res)
    # Run unit tests and generates test and coverage report artifacts
    if res.ok():
        res = exec_manager.cli_run(
            "cargo testcov " + f"{flags} ",
            name="Self contained Unit tests and collect coverage",
            verbose=verbose,
        )
        results.append(res)
    # Save coverage report to file if it is provided
    if res.ok():
        res = exec_manager.cli_run(
            "cargo llvm-cov report "
            + f"{flags} "
            + "--release "
            + f"--output-path {cov_report} ",
            name=f"Generate lcov report to {cov_report}",
            verbose=verbose,
        )
        results.append(res)

    return results


def cargo_bench(flags: str, verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo bench " + f"{flags} ",
        name="Benchmarks all run to completion check",
        verbose=verbose,
    )


def cargo_doc(verbose: bool = False) -> exec_manager.Result:
    return exec_manager.cli_run(
        "cargo +nightly docs ", name="Documentation build", verbose=verbose
    )


def cargo_depgraph(runner: exec_manager.ParallelRunner, verbose: bool = False) -> None:

    runner.run(
        exec_manager.cli_run,
        "cargo depgraph "
        + "--workspace-only "
        + "--dedup-transitive-deps "
        + "> target/doc/workspace.dot ",
        name="Workspace dependency graphs generation",
        verbose=verbose,
    )

    runner.run(
        exec_manager.cli_run,
        "cargo depgraph " + "--dedup-transitive-deps " + "> target/doc/full.dot ",
        name="Full dependency graphs generation",
        verbose=verbose,
    )

    runner.run(
        exec_manager.cli_run,
        "cargo depgraph "
        + "--all-deps "
        + "--dedup-transitive-deps "
        + "> target/doc/all.dot ",
        name="All dependency graphs generation",
        verbose=verbose,
    )


COMMON_CARGO_MODULES_ORPHANS = (
    "NO_COLOR=1 " + "cargo modules orphans --all-features " + "--deny --cfg-test "
)
COMMON_CARGO_MODULES_STRUCTURE = (
    "NO_COLOR=1 " + "cargo modules structure --no-fns --all-features "
)
COMMON_CARGO_MODULES_DEPENDENCIES = (
    "NO_COLOR=1 "
    + "cargo modules dependencies --all-features "
    + "--no-externs --no-fns --no-sysroot --no-traits --no-types --no-uses "
)


def cargo_modules_lib(
    runner: exec_manager.ParallelRunner,
    lib: str,
    docs: bool = True,
    verbose: bool = False,
) -> None:
    # Check if we have any Orphans.
    runner.run(
        exec_manager.cli_run,
        COMMON_CARGO_MODULES_ORPHANS + f"--package '{lib}' --lib",
        name=f"Checking Orphans for {lib}",
        verbose=verbose,
    )

    if docs:
        # Generate tree
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_STRUCTURE
            + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.tree' ",
            name=f"Generate Module Trees for {lib}",
            verbose=verbose,
        )
        # Generate graph
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_DEPENDENCIES
            + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.dot' ",
            name=f"Generate Module Graphs for {lib}",
            verbose=verbose,
        )


def cargo_modules_bin(
    runner: exec_manager.ParallelRunner,
    package: str,
    bin: str,
    docs: bool = True,
    verbose: bool = False,
) -> None:
    # Check if we have any Orphans.
    runner.run(
        exec_manager.cli_run,
        COMMON_CARGO_MODULES_ORPHANS + f"--package '{package}' --bin '{bin}'",
        name=f"Checking Orphans for {package}/{bin}",
        verbose=verbose,
    )

    if docs:
        # Generate tree
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_STRUCTURE
            + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.tree' ",
            name=f"Generate Module Trees for {package}/{bin}",
            verbose=verbose,
        )
        # Generate graph
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_DEPENDENCIES
            + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.dot' ",
            name=f"Generate Module Graphs for {package}/{bin}",
            verbose=verbose,
        )


# ALL executables MUST have `--help` as an option.
def help_check(results: exec_manager.Results, bin: str, verbose: bool = False):
    results.add(
        exec_manager.cli_run(
            f"target/release/{bin} --help",
            name=f"Executable '{bin}' MUST have `--help` as an option.",
            verbose=verbose,
        )
    )


def ldd(results: exec_manager.Results, bin: str):
    results.add(
        exec_manager.cli_run(
            f"ldd target/release/{bin}", name=f"ldd for '{bin}'", verbose=True
        )
    )


def readelf(results: exec_manager.Results, bin: str):
    results.add(
        exec_manager.cli_run(
            f"readelf -p .comment target/release/{bin}",
            name=f"readelf for '{bin}'",
            verbose=True,
        )
    )


def strip(results: exec_manager.Results, bin: str):
    results.add(
        exec_manager.cli_run(
            f"strip -v target/release/{bin}", name=f"strip for '{bin}'", verbose=True
        )
    )

import sys

def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    for arg in sys.argv[1:]:
        print(arg)

    parser = argparse.ArgumentParser(description="Rust build processing.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show the output of executed commands verbosely.",
    )
    parser.add_argument(
        "--build_flags",
        default="",
        help="Additional command-line flags that can be passed to the `cargo build` command.",
    )
    parser.add_argument(
        "--lint_flags",
        default="",
        help="Additional command-line flags that can be passed to the `cargo lint` command.",
    )
    parser.add_argument(
        "--doctest_flags",
        default="",
        help="Additional command-line flags that can be passed to the `cargo testdocs` command.",
    )
    parser.add_argument(
        "--test_flags",
        default="",
        help="Additional command-line flags that can be passed to the `cargo testunit` command.",
    )
    parser.add_argument(
        "--bench_flags",
        default="",
        help="Additional command-line flags that can be passed to the `cargo bench` command.",
    )
    parser.add_argument(
        "--cov_report",
        default="",
        help="The output coverage report file path. If omitted, coverage will not be run.",
    )
    parser.add_argument(
        "--disable_tests",
        action="store_true",
        help="Flag to disable to run tests (including unit tests and doc tests).",
    )
    parser.add_argument(
        "--disable_benches",
        action="store_true",
        help="Flag to disable to run benchmarks.",
    )
    parser.add_argument(
        "--disable_docs",
        action="store_true",
        help="Flag to disable docs building (including graphs, trees etc.) or not.",
    )
    parser.add_argument(
        "--libs",
        default="",
        help="The list of lib crates `cargo-modules` docs to build separated by comma.",
    )
    parser.add_argument(
        "--bins",
        default="",
        help="The list of binaries `cargo-modules` docs to build and make a smoke tests on them.",
    )
    args = parser.parse_args()

    libs = filter(lambda lib:  lib.strip() and len(lib.strip()) > 0, args.libs.split(","))
    bins = list(filter(lambda bin: bin.strip() and len(bin.strip()) > 0, args.bins.split(",")))

    with exec_manager.ParallelRunner("Rust build") as runner:
        # Build the code.
        runner.run(cargo_build, args.build_flags, args.verbose)

        # Check the code passes all clippy lint checks.
        runner.run(cargo_lint, args.lint_flags, args.verbose)

        # Check if all Self contained tests pass (Test that need no external resources).
        if not args.disable_tests:
            # Check if all documentation tests pass.
            runner.run(cargo_doctest, args.doctest_flags, args.verbose)
            if args.cov_report == "":
                # Without coverage report
                runner.run(cargo_nextest, args.test_flags, args.verbose)
            else:
                # With coverage report
                runner.run(
                    cargo_llvm_cov, args.test_flags, args.cov_report, args.verbose
                )
                # pass

        if not args.disable_benches:
            runner.run(cargo_bench, args.bench_flags, args.verbose)

        # Generate all the documentation. Ensure the path docs make in exists first.
        # We need this even if we aren't making docs.
        if not args.disable_docs:
            # Make sure docs path exists before making any docs.
            if not os.path.exists("target/doc"):
                os.makedirs("target/doc")
            # Generate rust docs.
            runner.run(cargo_doc, args.verbose)
            # Generate dependency graphs
            cargo_depgraph(runner, args.verbose)

        # These do generate documentation artifacts, but are NOT blocked by docs generation because they
        # ALSO check for orphaned dependencies.  Which is required for all targets.
        for lib in libs:
            cargo_modules_lib(runner, lib, not args.disable_docs, args.verbose)
        for bin in bins:
            package, bin_name = bin.split("/")
            cargo_modules_bin(runner, package, bin_name, not args.disable_docs, args.verbose)

        results = runner.get_results()

    results.print()
    if not results.ok():
        exit(1)

    # Check if the build executable, isn't a busted mess.
    results = exec_manager.Results("Smoke test")

    for bin in bins:
        _, bin_name = bin.split("/")
        help_check(results, bin_name, args.verbose)
        ldd(results, bin_name)
        readelf(results, bin_name)
        strip(results, bin_name)

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
