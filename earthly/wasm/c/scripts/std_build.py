#!/usr/bin/env python3

# cspell: words lcov depgraph readelf sysroot

import python.exec_manager as exec_manager
import argparse
import rich

# This script is run inside the `build` stage.
# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.


def wit_bindgen_c(results: exec_manager.Results, wit_path: str):
    results.add(
        exec_manager.cli_run(
            "wit-bindgen c --autodrop-borrows yes " + f"{wit_path} ",
            name="",
        )
    )


def clang_wasm_compile(results: exec_manager.Results, c_files: str):
    results.add(
        exec_manager.cli_run(
            "clang demo.c demo_component_type.o "
            + f"{c_files}"
            + " -o out.wasm -mexec-model=reactor --target=wasm32-wasi",
            name="Build all code in the workspace",
        )
    )


def wasm_tools_gen_component(results: exec_manager.Results, out: str):
    results.add(
        exec_manager.cli_run(
            "wasm-tools validate out.wasm",
            name="Validate wasm module",
        )
    )
    results.add(
        exec_manager.cli_run(
            "wasm-tools component new out.wasm -o " + f"{out}",
            name="Generate WASM component",
        )
    )


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(description="WASM C build processing.")
    parser.add_argument(
        "--wit_path",
        default="wit",
        help=".",
    )
    parser.add_argument(
        "--c_files",
        help=".",
    )
    parser.add_argument(
        "--out",
        help=".",
    )
    args = parser.parse_args()

    results = exec_manager.Results("WASM C build")

    wit_bindgen_c(results, args.wit_path)
    clang_wasm_compile(results, args.c_files)
    wasm_tools_gen_component(results, args.out)

    results.print()
    if not results.ok():
        exit(1)


if __name__ == "__main__":
    main()
