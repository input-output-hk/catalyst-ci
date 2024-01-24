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
class DiffResult:
    """
    Represents the difference between two dictionaries.
    """

    diff: dict

    def has_diff(self) -> bool:
        return bool(self.diff)

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

        def impl(
            diff: dict,
            obj_name_to_add: str,
            obj_name_to_remove: str,
            ident: str = "",
            path: str = "",
        ) -> str:
            def add_color(val: str, color: str) -> str:
                if color == "red":
                    return f"\033[91m{val}\033[0m"
                if color == "green":
                    return f"\033[92m{val}\033[0m"
                if color == "yellow":
                    return f"\033[93m{val}\033[0m"
                return val

            result = ""
            if isinstance(diff, DiffEntry):
                color = "green" if diff.add_or_remove_flag else "red"
                minus_or_plus = "+" if diff.add_or_remove_flag else "-"
                obj_name = (
                    obj_name_to_add if diff.add_or_remove_flag else obj_name_to_remove
                )

                result += "\n------\n"
                result += add_color(obj_name, "yellow")
                result += f"{path}\n"
                result += add_color(f"{minus_or_plus}{ident} {diff.val}", color)

            if isinstance(diff, dict):
                for key in diff:
                    result += impl(
                        diff[key],
                        obj_name_to_add,
                        obj_name_to_remove,
                        ident + " ",
                        path + "\n" + f"{ident}  {key}",
                    )

            if isinstance(diff, tuple):
                for val in diff:
                    result += impl(
                        val, obj_name_to_add, obj_name_to_remove, ident, path
                    )

            return result

        return impl(self.diff, obj_name_to_add, obj_name_to_remove)


@dataclass
class Diff:
    """
    Calculates the difference between two dictionaries.
    """

    a: dict
    b: dict
    strict: bool

    def get_diff(self) -> DiffResult:
        if self.strict:
            return self._strict_diff_()
        else:
            return self._inclusion_diff_()

    def _inclusion_diff_(self, reverse: bool = False) -> DiffResult:
        """
        Calculates an inclusion diff between the 'a' and 'b' dicts in a recursive manner.
        Checks that 'a' has an inclusion of 'b'.
        Args:
            reverse (bool): An inclusion diff calculation flag.
                If 'True' evaluates that 'a' as an inclusion of 'b'.
                If 'False' evaluates that 'b' as an inclusion of 'a'.
        """

        def impl(expected: dict, provided: dict) -> dict:
            diff = {}
            for key in expected:
                if key not in provided:
                    diff[key] = DiffEntry(expected[key], True)
                elif not isinstance(expected[key], dict):
                    if expected[key] != provided[key]:
                        diff[key] = (
                            DiffEntry(expected[key], True),
                            DiffEntry(provided[key], False),
                        )
                else:
                    res = impl(expected[key], provided[key])
                    if res != {}:
                        diff[key] = res
            return diff

        diff = impl(self.a, self.b) if not reverse else impl(self.a, self.b)
        return DiffResult(diff)

    def _strict_diff_(self) -> DiffResult:
        """
        Calculate the strict diff between  the expected and provided inputs.
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
        incl_diff_1 = self._inclusion_diff_()
        incl_diff_2 = self._inclusion_diff_(True)
        incl_diff_1.diff.update(incl_diff_2.diff)

        return incl_diff_1
