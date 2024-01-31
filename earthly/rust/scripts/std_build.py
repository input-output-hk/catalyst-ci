#!/usr/bin/env python3

# cspell: words lcov depgraph readelf

import python.exec_manager as exec_manager
import argparse
import rich

# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.


def cargo_build(results: exec_manager.Results, flags: str):
    results.add(
        exec_manager.cli_run(
            "cargo build " + "--release " + f"{flags} ",
            name="Build all code in the workspace",
        )
    )


def cargo_lint(results: exec_manager.Results, flags: str):
    results.add(
        exec_manager.cli_run(
            "cargo lint " + f"{flags}", name="Clippy Lints in the workspace check"
        )
    )


def cargo_doctest(results: exec_manager.Results, flags: str):
    results.add(
        exec_manager.cli_run(
            "cargo +nightly testdocs " + f"{flags} ",
            name="Documentation tests all pass check",
        )
    )


def cargo_nextest(results: exec_manager.Results, flags: str):
    results.add(
        exec_manager.cli_run(
            "cargo testunit " + f"{flags} ",
            name="Self contained Unit tests all pass check",
        )
    )


def cargo_llvm_cov(results: exec_manager.Results, flags: str, cov_report: str):
    # Remove artifacts that may affect the coverage results
    res = exec_manager.cli_run(
        "cargo llvm-cov clean",
        name="Remove artifacts that may affect the coverage results",
    )
    results.add(res)
    # Run unit tests and generates test and coverage report artifacts
    if res.ok():
        res = exec_manager.cli_run(
            "cargo testcov " + f"{flags} ",
            name="Self contained Unit tests and collect coverage",
        )
        results.add(res)
    # Save coverage report to file if it is provided
    if res.ok():
        res = exec_manager.cli_run(
            "cargo llvm-cov report "
            + f"{flags} "
            + "--release "
            + f"--output-path {cov_report} ",
            name=f"Generate lcov report to {cov_report}",
        )
        results.add(res)


def cargo_bench(results: exec_manager.Results, flags: str):
    results.add(
        exec_manager.cli_run(
            "cargo bench " + f"{flags} ",
            name="Benchmarks all run to completion check",
        )
    )


def cargo_doc(results: exec_manager.Results):
    results.add(
        exec_manager.cli_run("cargo +nightly docs ", name="Documentation build")
    )


def cargo_depgraph(results: exec_manager.Results):
    results.add(
        exec_manager.cli_run(
            "cargo depgraph "
            + "--workspace-only "
            + "--dedup-transitive-deps "
            + "> target/doc/workspace.dot ",
            name="Workspace dependency graphs generation",
        )
    )
    results.add(
        exec_manager.cli_run(
            "cargo depgraph " + "--dedup-transitive-deps " + "> target/doc/full.dot ",
            name="Full dependency graphs generation",
        )
    )
    results.add(
        exec_manager.cli_run(
            "cargo depgraph "
            + "--all-deps "
            + "--dedup-transitive-deps "
            + "> target/doc/all.dot ",
            name="All dependency graphs generation",
        )
    )

COMMON_CARGO_MODULES_ORPHANS = (
    "NO_COLOR=1 "
    + "cargo modules orphans --all-features "
    + "--deny --cfg-test "
)
COMMON_CARGO_MODULES_STRUCTURE = (
    "NO_COLOR=1 "
    + "cargo modules structure --no-fns --all-features "
)
COMMON_CARGO_MODULES_DEPENDENCIES = (
    "NO_COLOR=1 "
    + "cargo modules dependencies --all-features "
    + "--no-externs --no-fns --no-sysroot --no-traits --no-types --no-uses "
)

def cargo_modules_lib(results: exec_manager.Results, lib: str):
    # Check if we have any Orphans.
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_ORPHANS
            + f"--package '{lib}' --lib",
            name=f"Checking Orphans for {lib}",            
        )
    )
    
    # Generate tree
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_STRUCTURE
            + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.tree' ",
            name=f"Generate Module Trees for {lib}",
        )
    )
    # Generate graph
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_DEPENDENCIES
            + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.dot' ",
            name=f"Generate Module Graphs for {lib}",
        )
    )


def cargo_modules_bin(results: exec_manager.Results, package: str, bin: str):
    # Check if we have any Orphans.
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_ORPHANS
            + f"--package '{package}' --bin '{bin}'",
            name=f"Checking Orphans for {package}/{bin}",            
        )
    )

    # Generate tree
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_STRUCTURE
            + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.tree' ",
            name=f"Generate Module Trees for {package}/{bin}",
        )
    )
    # Generate graph
    results.add(
        exec_manager.cli_run(
            COMMON_CARGO_MODULES_DEPENDENCIES
            + f"--package '{package}' --bin '{bin}' > 'target/doc/{package}.{bin}.bin.modules.dot' ",
            name=f"Generate Module Graphs for {package}/{bin}",
        )
    )


# ALL executables MUST have `--help` as an option.
def help_check(results: exec_manager.Results, bin: str):
    results.add(
        exec_manager.cli_run(
            f"target/release/{bin} --help",
            name=f"Executable '{bin}' MUST have `--help` as an option.",
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


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(description="Rust build processing.")
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

    libs = filter(lambda lib: lib != "", args.libs.split(", "))
    bins = list(filter(lambda bin: bin != "", args.bins.split(", ")))

    results = exec_manager.Results("Rust build")
    # Build the code.
    cargo_build(results, args.build_flags)
    # Check the code passes all clippy lint checks.
    cargo_lint(results, args.lint_flags)
    # Check if all Self contained tests pass (Test that need no external resources).
    if not args.disable_tests:
        # Check if all documentation tests pass.
        cargo_doctest(results, args.doctest_flags)
        if args.cov_report == "":
            # Without coverage report
            cargo_nextest(results, args.test_flags)
        else:
            # With coverage report
            cargo_llvm_cov(results, args.test_flags, args.cov_report)

    # Check if any benchmarks defined run (We don't validate the results.)
    if not args.disable_benches:
        cargo_bench(results, args.bench_flags)

    # Generate all the documentation.
    if not args.disable_docs:
        # Generate rust docs.
        cargo_doc(results)
        # Generate dependency graphs
        cargo_depgraph(results)

        for lib in libs:
            cargo_modules_lib(results, lib)
        for bin in bins:
            package, bin_name = bin.split("/")
            cargo_modules_bin(results, package, bin_name)

    results.print()
    if not results.ok():
        exit(1)

    # Check if the build executable, isn't a busted mess.
    results = exec_manager.Results("Smoke test")

    for bin in bins:
        _, bin_name = bin.split("/")
        help_check(results, bin_name)
        ldd(results, bin_name)
        readelf(results, bin_name)
        strip(results, bin_name)

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
