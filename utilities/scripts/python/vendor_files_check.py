# Checks if two files that should exist DO, and are equal.
# used to enforce consistency between local config files and the expected config locked in CI.

import python.exec_manager as exec_manager
import tomllib
from python.diff import Diff


def colordiff_check(
    vendor_file_path: str, provided_file_path: str
) -> exec_manager.Result:
    return exec_manager.cli_run(
        f"colordiff -Nau {provided_file_path} {vendor_file_path}",
        name=f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
    )


def toml_diff_check(
    vendor_file_path: str,
    provided_file_path: str,
    strict: bool = True,
    log: bool = True,
) -> exec_manager.Result:
    command_name = (
        f"{'' if strict else 'Non '}Strict Checking"
        + f" if Provided File {provided_file_path} == Vendored File {vendor_file_path}"
    )
    with open(vendor_file_path, "rb") as vendor_file, open(
        provided_file_path, "rb"
    ) as provided_file:

        def procedure() -> exec_manager.ProcedureResult:
            vendor_obj = tomllib.load(vendor_file)
            provided_obj = tomllib.load(provided_file)

            diff = Diff(vendor_obj, provided_obj, strict).get_diff()

            return exec_manager.ProcedureResult(
                1 if diff.has_diff() else 0,
                command_name,
                diff.to_ascii_colored_string(vendor_file_path, provided_file_path),
            )

        return exec_manager.procedure_run(
            procedure,
            command_name,
            log=log,
        )
