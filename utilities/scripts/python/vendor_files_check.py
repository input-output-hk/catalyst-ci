# cspell: words colordiff

# Checks if two files that should exist DO, and are equal.
# used to enforce consistency between local config files and the expected config locked in CI.

import python.exec_manager as exec_manager
import tomllib
import time
from dataclasses import dataclass


def colordiff_check(
    vendor_file_path: str, provided_file_path: str
) -> exec_manager.Result:
    return exec_manager.cli_run(
        f"colordiff -Nau {provided_file_path} {vendor_file_path}",
        name=f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}",
    )


def toml_diff_check(
    vendor_file_path: str, provided_file_path: str, strict: bool = True
):
    comand_name = (
        f"{'Strict' if strict else 'Non Strict'} Checking"
        + f"if Provided File {provided_file_path} == Vendored File {vendor_file_path}"
    )
    with open(vendor_file_path, "rb") as vendor_file, open(
        provided_file_path, "rb"
    ) as provided_file:

        def procedure() -> exec_manager.ProcedureResult:
            vendor_obj = tomllib.load(vendor_file)
            provided_obj = tomllib.load(provided_file)

            diff = (
                __strict_diff__(vendor_obj, provided_obj)
                if strict
                else __inclusion_diff__(vendor_obj, provided_obj)
            )
            out = __str_diff__(diff, vendor_file_path, provided_file_path)
            rc = 1 if diff else 0

            return exec_manager.ProcedureResult(
                rc,
                comand_name,
                out,
            )

        return exec_manager.procedure_run(
            procedure,
            comand_name,
        )


@dataclass
class DiffEntry:
    """
    A data class representing an entry in a difference collection.
    Attributes:
    val: any
        The value of the entry.
    add_or_remove_flag: bool
        A flag indicating whether the entry should be removed (False) or added (True).
    """

    val: any
    add_or_remove_flag: bool


def __inclusion_diff__(expected, provided):
    """
    Calculate an inclusion diff between the expected and provided inputs in a recursive manner.

    Args:
        expected: The expected input.
        provided: The provided input.

    Returns:
        A dictionary representing the difference between the expected and provided inputs.
    """
    diff = {}
    if not isinstance(expected, dict):
        if expected != provided:
            return [DiffEntry(expected, True), DiffEntry(provided, False)]
    else:
        for key in expected:
            if key not in provided:
                diff[key] = DiffEntry(expected[key], True)
            else:
                res = __inclusion_diff__(expected[key], provided[key])
                if res != {}:
                    diff[key] = res
    return diff


def __strict_diff__(expected, provided):
    """
    Calculate the strict diff between  the expected and provided inputs.

    Args:
        expected: The expected input for the comparison.
        provided: The actual input for the comparison.

    Returns:
        dict: A dictionary representing the strict difference between the expected
        and provided inputs.
    """

    def change_flags(diff):
        if isinstance(diff, DiffEntry):
            diff.add_or_remove_flag = not diff.add_or_remove_flag
        if isinstance(diff, list):
            for val in diff:
                change_flags(val)
        if isinstance(diff, dict):
            for key in diff:
                change_flags(diff[key])

    # Finds two inclusion diffs and concatenate the results
    # Also it is important to update a result from the second inclussion diff result
    # Because it's result has a "reverse" add_or_remove_flag meaning
    incl1 = __inclusion_diff__(expected, provided)
    incl2 = __inclusion_diff__(provided, expected)
    change_flags(incl2)
    incl1.update(incl2)
    return incl1


def __add_color__(val: str, color: str):
    if color == "red":
        return f"\033[91m{val}\033[0m"
    if color == "green":
        return f"\033[92m{val}\033[0m"
    if color == "yellow":
        return f"\033[93m{val}\033[0m"
    return val


def __str_diff__(
    diff: dict,
    obj_name_to_add: str,
    obj_name_to_remove: str,
    ident: str = "",
    path: str = "",
):
    """
    Generates a string representation of the diff.

    Args:
        diff (dict): The dictionary representing the diff.
        obj_name_to_add (str): The name of the object to add.
        obj_name_to_remove (str): The name of the object to remove.
    Returns:
        str: The string representation of the differences.
    """
    str_diff = ""
    if isinstance(diff, DiffEntry):
        color = "green" if diff.add_or_remove_flag else "red"
        minus_or_plus = "+" if diff.add_or_remove_flag else "-"
        obj_name = obj_name_to_add if diff.add_or_remove_flag else obj_name_to_remove

        str_diff += "\n------\n"
        str_diff += __add_color__(obj_name, "yellow")
        str_diff += f"{path}\n"
        str_diff += __add_color__(f"{minus_or_plus}{ident} {diff.val}", color)

    if isinstance(diff, dict):
        for key in diff:
            str_diff += __str_diff__(
                diff[key],
                obj_name_to_add,
                obj_name_to_remove,
                ident + " ",
                path + "\n" + f"{ident}  {key}",
            )

    if isinstance(diff, list):
        for val in diff:
            str_diff += __str_diff__(
                val, obj_name_to_add, obj_name_to_remove, ident, path
            )

    return str_diff
