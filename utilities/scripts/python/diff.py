from dataclasses import dataclass
from typing import Dict


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


@dataclass
class Diff:
    """
    Represents the difference between two dictionaries.
    """
    diff: dict

    def __init__(self, expected: dict, provided: dict, strict: bool):
        if strict:
            self.diff = _strict_diff_(expected, provided)
        else:
            self.diff = _inclusion_diff_(expected, provided)

    def has_diff(self) -> bool:
        return True if self.diff else False

    def to_ascii_colored_string(
        self,
        obj_name_to_add: str,
        obj_name_to_remove: str,
    ) -> str:
        """
        Generates an ascii colored string representation of the diff.

        Args:
            obj_name_to_add (str): The name of the object to add.
            obj_name_to_remove (str): The name of the object to remove.
        """

        def _impl_(
            diff: dict,
            obj_name_to_add: str,
            obj_name_to_remove: str,
            ident: str = "",
            path: str = "",
        ) -> str:
            result = ""
            if isinstance(diff, DiffEntry):
                color = "green" if diff.add_or_remove_flag else "red"
                minus_or_plus = "+" if diff.add_or_remove_flag else "-"
                obj_name = (
                    obj_name_to_add if diff.add_or_remove_flag else obj_name_to_remove
                )

                result += "\n------\n"
                result += _add_color_(obj_name, "yellow")
                result += f"{path}\n"
                result += _add_color_(f"{minus_or_plus}{ident} {diff.val}", color)

            if isinstance(diff, dict):
                for key in diff:
                    result += _impl_(
                        diff[key],
                        obj_name_to_add,
                        obj_name_to_remove,
                        ident + " ",
                        path + "\n" + f"{ident}  {key}",
                    )

            if isinstance(diff, list):
                for val in diff:
                    result += _impl_(
                        val, obj_name_to_add, obj_name_to_remove, ident, path
                    )

            return result

        return _impl_(self.diff, obj_name_to_add, obj_name_to_remove)


def _inclusion_diff_(expected: dict, provided: dict) -> dict:
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
                res = _inclusion_diff_(expected[key], provided[key])
                if res != {}:
                    diff[key] = res
    return diff


def _strict_diff_(expected: dict, provided: dict) -> dict:
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
    # Also it is important to update a result from the second inclusion diff result
    # Because it's result has a "reverse" add_or_remove_flag meaning
    incl1 = _inclusion_diff_(expected, provided)
    incl2 = _inclusion_diff_(provided, expected)
    change_flags(incl2)
    incl1.update(incl2)
    return incl1


def _add_color_(val: str, color: str) -> str:
    if color == "red":
        return f"\033[91m{val}\033[0m"
    if color == "green":
        return f"\033[92m{val}\033[0m"
    if color == "yellow":
        return f"\033[93m{val}\033[0m"
    return val
