"""Doc Macros Init."""

from typing import Any

from .include import inc_file


def define_env(env: Any) -> None:  # noqa: ANN401
    """Hooks for defining variables, macros and filters."""

    @env.macro
    def include_file(filename: str, start_line: int = 0, end_line: int | None = None, indent: int | None = None) -> str:
        return inc_file(env, filename, start_line, end_line, indent)
