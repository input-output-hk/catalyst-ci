#!/usr/bin/env python3
"""Wasm Standard Build."""
# cspell: words lcov depgraph readelf sysroot bindgen autodrop mexec

import argparse
import os
import sys

import rich
from python import exec_manager

# This script is run inside the `build` stage.

BINDINGS_SRC = "bindings_src"


def wit_bindgen_c(results: exec_manager.Results, wit_path: str) -> None:
    """Wit Bindgen C."""
    results.add(
        exec_manager.cli_run(
            " ".join(
                [
                    "wit-bindgen c",
                    "--autodrop-borrows yes",
                    f"--out-dir {BINDINGS_SRC}",
                    wit_path,
                ],
            ),
            name="Generate bindings C code.",
            verbose=True,
        ),
    )


def clang_wasm_compile(results: exec_manager.Results, c_files: str) -> None:
    """Get file names from the BINDINGS_SRC except *.h files."""
    bindings_src = " ".join([BINDINGS_SRC + "/" + f for f in os.listdir(BINDINGS_SRC) if not f.endswith(".h")])  # noqa: PTH208
    results.add(
        exec_manager.cli_run(
            "/opt/wasi-sdk/bin/clang"
            " --sysroot=/opt/wasi-sdk/share/wasi-sysroot"
            f" {bindings_src} {c_files}"
            " -Oz -o out.wasm -mexec-model=reactor --target=wasm32-wasi",
            name="Compile C code to wasm module",
            verbose=True,
        ),
    )


def wasm_tools_gen_component(results: exec_manager.Results, out: str) -> None:
    """Wasm Tools Gen Component."""
    results.add(
        exec_manager.cli_run(
            "wasm-tools validate out.wasm",
            name="Validate wasm module",
            verbose=True,
        ),
    )
    results.add(
        exec_manager.cli_run(
            "wasm-tools component new out.wasm -o " + f"{out}",
            name="Generate WASM component",
            verbose=True,
        ),
    )


def main() -> None:
    """WASM Standard Build script."""
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(description="WASM C build processing.")
    parser.add_argument(
        "--wit_path",
        default="wit",
        help="Path to the .wit files.",
    )
    parser.add_argument(
        "--c_files",
        help="Source C files to compile.",
    )
    parser.add_argument(
        "--out",
        help="Output WASM component file.",
    )
    args = parser.parse_args()

    results = exec_manager.Results("WASM C build")

    wit_bindgen_c(results, args.wit_path)
    clang_wasm_compile(results, args.c_files)
    wasm_tools_gen_component(results, args.out)

    results.print()
    if not results.ok():
        sys.exit(1)


if __name__ == "__main__":
    main()
