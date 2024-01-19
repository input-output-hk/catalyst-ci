# cspell: words colordiff

# Checks if two files that should exist DO, and are equal.
# used to enforce consistency between local config files and the expected config locked in CI.

import python.exec_manager as exec_manager
import tomllib
import time


def colordiff_check(
    vendor_file_path: str, provided_file_path: str
) -> exec_manager.Result:
    return exec_manager.cli_run(
        f"colordiff -Nau {provided_file_path} {vendor_file_path}",
        name=f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
    )


def toml_diff_strict_check(vendor_file_path: str, provided_file_path: str):
    with open(vendor_file_path, "rb") as vendor_file, open(
        provided_file_path, "rb"
    ) as provided_file:
        def procedure() -> exec_manager.ProcedureResult:
            vendor_obj = tomllib.load(vendor_file)
            provided_obj = tomllib.load(provided_file)

            diff1 = __compare_dicts__(vendor_obj, provided_obj)
            out = __print_diff__(diff1, vendor_file_path, provided_file_path)
            diff2 = __compare_dicts__(provided_obj, vendor_obj)
            out += __print_diff__(diff2, provided_file_path, vendor_file_path, False)
            rc = 1 if diff1 or diff2 else 0

            return exec_manager.ProcedureResult(
                rc,
                f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
                out,
            )

        return exec_manager.procedure_run(
            procedure,
            f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
        )

def toml_diff_non_strict_check(vendor_file_path: str, provided_file_path: str):
    with open(vendor_file_path, "rb") as vendor_file, open(
        provided_file_path, "rb"
    ) as provided_file:
        def procedure() -> exec_manager.ProcedureResult:
            vendor_obj = tomllib.load(vendor_file)
            provided_obj = tomllib.load(provided_file)

            diff = __compare_dicts__(vendor_obj, provided_obj)
            out = __print_diff__(diff, vendor_file_path, provided_file_path)
            rc = 1 if diff else 0

            return exec_manager.ProcedureResult(
                rc,
                f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
                out,
            )

        return exec_manager.procedure_run(
            procedure,
            f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
        )



def __compare_dicts__(expected, provided):
    """
    Compare two dictionaries recursively and return the differences.
    It is not a strict comparison,
    it checks is the `provided` contains the same values from the `expected`,
    so `provided` could have an extra one which are not present in `expected`.
    """
    diff = {}
    if not isinstance(expected, dict) or not isinstance(provided, dict):
        if expected != provided:
            return expected, provided
        else:
            return diff
    else:
        for key in expected:
            if key not in provided:
                diff[key] = expected[key]
            else:
                res = __compare_dicts__(expected[key], provided[key])
                if res != {}:
                    diff[key] = res
    return diff


def __print_diff__(
    diff: dict,
    name1: str,
    name2: str,
    flag: bool = True,
    ident: str = "",
    path: str = "",
):
    """
    Generate a string representation of the differences in a dictionary.
    Parameters:
        diff (dict): The dictionary containing the differences.
        flag (bool, optional): The flag indicating whether the differences are added or removed. Defaults to True.
    Returns:
        str: The string representation of the differences.
    """
    if path == "":
        path += "\n------"
        path += f"\n\033[93m{name1}"

    str_diff = ""
    if not isinstance(diff, dict):
        if isinstance(diff, tuple):
            if isinstance(diff[0], dict):
                str_diff += __print_diff__(
                    diff[0], name1, name2, flag, ident + " ", path
                )
            else:
                str_diff += f"{path}\n"
                if flag:
                    str_diff += f"\033[91m-{ident} {diff[0]}"
                else:
                    str_diff += f"\033[92m+{ident} {diff[0]}"

            str_diff += f"\n\033[93m{name2}"
            if flag:
                str_diff += f"\n\033[92m+{ident} {diff[1]}"
            else:
                str_diff += f"\n\033[91m-{ident} {diff[1]}"

        else:
            str_diff += f"{path}\n"
            if flag:
                str_diff += f"\033[91m-{ident} {diff}\n"
            else:
                str_diff += f"\033[92m+{ident} {diff}\n"
    else:
        for key in diff:
            if flag:
                path += f"\n\033[91m{ident}  {key}"
            else:
                path += f"\n\033[92m{ident}  {key}"
            str_diff += __print_diff__(diff[key], name1, name2, flag, ident + " ", path)

    return str_diff
