#!/usr/bin/env python3
"""Rust Standard Build."""

# cspell: words lcov depgraph readelf sysroot

import argparse
import os
import sys
from pathlib import Path

import rich
from python import exec_manager
from python.utils import fix_quoted_earthly_args


# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.


def cargo_build(flags: str, *, verbose: bool = False) -> exec_manager.Result:
    """Cargo Build."""
    return exec_manager.cli_run(
        "cargo build " + "--release " + f"{flags} ",
        name="Build all code in the workspace",
        verbose=verbose,
    )


def cargo_lint(flags: str, *, verbose: bool = False) -> exec_manager.Result:
    """Cargo Lint."""
    return exec_manager.cli_run(
        "cargo lint --release " + f"{flags}",
        name="Clippy Lints in the workspace check",
        verbose=verbose,
    )


def cargo_doctest(flags: str, *, verbose: bool = False) -> exec_manager.Result:
    """Cargo Doctest."""
    return exec_manager.cli_run(
        "cargo testdocs " + f"{flags} ",
        name="Documentation tests all pass check",
        verbose=verbose,
    )


def cargo_nextest(flags: str, *, verbose: bool = False) -> exec_manager.Result:
    """Cargo Nextest."""
    return exec_manager.cli_run(
        "cargo testunit " + f"{flags} ",
        name="Self contained Unit tests all pass check",
        verbose=verbose,
    )


def cargo_llvm_cov(flags: str, cov_report: str, *, verbose: bool = False) -> list[exec_manager.Result]:
    """Cargo LLVM Cov."""
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
            "cargo llvm-cov report --lcov " + f"{flags} " + "--release " + f"--output-path {cov_report} ",
            name=f"Generate lcov report to {cov_report}",
            verbose=verbose,
        )
        results.append(res)

    return results


def cargo_bench(flags: str, *, verbose: bool = False) -> exec_manager.Result:
    """Cargo Bench."""
    return exec_manager.cli_run(
        f"cargo bench --all-targets --no-fail-fast {flags} ",
        name="Benchmarks all run to completion check",
        verbose=verbose,
    )


def cargo_doc(*, verbose: bool = False) -> exec_manager.Result:
    """Cargo Doc."""
    # Add RUSTDOCFLAGS to the inherited environment so we can build an index page with nightly.
    env = os.environ
    env["RUSTDOCFLAGS"] = "-Z unstable-options --enable-index-page"
    return exec_manager.cli_run("cargo +nightly docs", name="Documentation build", verbose=verbose)


def cargo_depgraph(runner: exec_manager.ParallelRunner, *, verbose: bool = False) -> None:
    """Cargo Depgraph."""
    runner.run(
        exec_manager.cli_run,
        "cargo depgraph " + "--workspace-only " + "--dedup-transitive-deps " + "> target/doc/workspace.dot ",
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
        "cargo depgraph " + "--all-deps " + "--dedup-transitive-deps " + "> target/doc/all.dot ",
        name="All dependency graphs generation",
        verbose=verbose,
    )


COMMON_CARGO_MODULES_ORPHANS = "NO_COLOR=1 " + "cargo modules orphans --all-features " + "--deny --cfg-test "
COMMON_CARGO_MODULES_STRUCTURE = "NO_COLOR=1 " + "cargo modules structure --no-fns --all-features "
COMMON_CARGO_MODULES_DEPENDENCIES = (
    "NO_COLOR=1 "
    "cargo modules dependencies --all-features "
    "--no-externs --no-fns --no-sysroot --no-traits --no-types --no-uses "
)


def cargo_modules_lib(
    runner: exec_manager.ParallelRunner,
    lib: str,
    *,
    docs: bool = True,
    verbose: bool = False,
) -> None:
    """Check if we have any Orphans."""
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
            COMMON_CARGO_MODULES_STRUCTURE + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.tree' ",
            name=f"Generate Module Trees for {lib}",
            verbose=verbose,
        )
        # Generate graph
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_DEPENDENCIES + f"--package '{lib}' --lib > 'target/doc/{lib}.lib.modules.dot' ",
            name=f"Generate Module Graphs for {lib}",
            verbose=verbose,
        )


def cargo_modules_bin(
    runner: exec_manager.ParallelRunner,
    package: str,
    bin_file: str,
    *,
    docs: bool = True,
    verbose: bool = False,
) -> None:
    """Check if we have any Orphans."""
    runner.run(
        exec_manager.cli_run,
        COMMON_CARGO_MODULES_ORPHANS + f"--package '{package}' --bin '{bin_file}'",
        name=f"Checking Orphans for {package}/{bin_file}",
        verbose=verbose,
    )

    if docs:
        # Generate tree
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_STRUCTURE
            + f"--package '{package}' --bin '{bin_file}' > 'target/doc/{package}.{bin_file}.bin.modules.tree' ",
            name=f"Generate Module Trees for {package}/{bin_file}",
            verbose=verbose,
        )
        # Generate graph
        runner.run(
            exec_manager.cli_run,
            COMMON_CARGO_MODULES_DEPENDENCIES
            + f"--package '{package}' --bin '{bin_file}' > 'target/doc/{package}.{bin_file}.bin.modules.dot' ",
            name=f"Generate Module Graphs for {package}/{bin_file}",
            verbose=verbose,
        )


# ALL executables MUST have `--help` as an option.
def help_check(results: exec_manager.Results, bin_file: str, *, verbose: bool = False) -> None:
    """Help Check."""
    results.add(
        exec_manager.cli_run(
            f"target/release/{bin_file} --help",
            name=f"Executable '{bin_file}' MUST have `--help` as an option.",
            verbose=verbose,
        ),
    )


def ldd(results: exec_manager.Results, bin_file: str) -> None:
    """Ldd."""
    results.add(exec_manager.cli_run(f"ldd target/release/{bin_file}", name=f"ldd for '{bin_file}'", verbose=True))


def readelf(results: exec_manager.Results, bin_file: str) -> None:
    """Readelf."""
    results.add(
        exec_manager.cli_run(
            f"readelf -p .comment target/release/{bin_file}",
            name=f"readelf for '{bin_file}'",
            verbose=True,
        ),
    )


def strip(results: exec_manager.Results, bin_file: str) -> None:
    """Strip."""
    results.add(
        exec_manager.cli_run(f"strip -v target/release/{bin_file}", name=f"strip for '{bin_file}'", verbose=True),
    )


def main() -> None:  # noqa: C901, PLR0915
    """Rust Standard Build."""
    # Force color output in CI
    rich.reconfigure(color_system="256")

    # Fix arguments because of munging that can happen because of the rust builder +EXECUTE function
    fix_quoted_earthly_args()

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

    libs = filter(lambda lib: lib.strip() and len(lib.strip()) > 0, args.libs.split(","))
    bins = list(filter(lambda bin_file: bin_file.strip() and len(bin_file.strip()) > 0, args.bins.split(",")))

    with exec_manager.ParallelRunner("Rust build") as runner:
        # Build the code.
        runner.run(cargo_build, args.build_flags, verbose=args.verbose)

        # Check the code passes all clippy lint checks.
        runner.run(cargo_lint, args.lint_flags, verbose=args.verbose)

        # Check if all Self contained tests pass (Test that need no external resources).
        # But NOT doc tests, as these are not replacements for unit tests.
        if not args.disable_tests:
            if args.cov_report == "":
                # Without coverage report
                runner.run(cargo_nextest, args.test_flags, verbose=args.verbose)
            else:
                # With coverage report
                runner.run(cargo_llvm_cov, args.test_flags, args.cov_report, verbose=args.verbose)
                # pass

        if not args.disable_benches:
            runner.run(cargo_bench, args.bench_flags, verbose=args.verbose)

        # Generate all the documentation. Ensure the path docs make in exists first.
        # We need this even if we aren't making docs.
        if not args.disable_docs:
            # Make sure docs path exists before making any docs.
            Path("target/doc").mkdir(parents=True, exist_ok=True)
            # Generate rust docs.
            runner.run(cargo_doc, verbose=args.verbose)
            # Generate dependency graphs
            cargo_depgraph(runner, verbose=args.verbose)

        # These do generate documentation artifacts, but are NOT blocked by docs generation because they
        # ALSO check for orphaned dependencies.  Which is required for all targets.
        for lib in libs:
            cargo_modules_lib(runner, lib, docs=not args.disable_docs, verbose=args.verbose)
        for bin_file in bins:
            package, bin_name = bin_file.split("/")
            cargo_modules_bin(runner, package, bin_name, docs=not args.disable_docs, verbose=args.verbose)

        results = runner.get_results()

    # Check if all Self contained doc tests pass (Test that need no external resources).
    # Can not be run in parallel with the normal builds as it becomes flaky and randomly fails.
    # NOTE: DocTests are ONLY run to prove they are valid, they are NOT unit tests, and never
    # currently contribute to code coverage.
    if not args.disable_tests:
        # Check if all documentation tests pass.
        results.add(cargo_doctest(args.doctest_flags, verbose=args.verbose))

    results.print()
    if not results.ok():
        sys.exit(1)

    # Check if the build executable, isn't a busted mess.
    results = exec_manager.Results("Smoke test")

    for bin_file in bins:
        _, bin_name = bin_file.split("/")
        help_check(results, bin_name, verbose=args.verbose)
        ldd(results, bin_name)
        readelf(results, bin_name)

    results.print()
    if not results.ok():
        sys.exit(1)


if __name__ == "__main__":
    main()
