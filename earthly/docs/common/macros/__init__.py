"""Doc Macros Init."""

from mkdocs_macros.plugin import MacrosPlugin

from .include import inc_file


def define_env(env: MacrosPlugin) -> None:
    """Hooks for defining variables, macros and filters."""

    @env.macro # pyright: ignore[reportUnknownMemberType]
    def include_file(filename: str, *, start_line: int = 0, end_line: int | None = None, indent: int = 0) -> str:  # pyright: ignore[reportUnusedFunction]
        return inc_file(env, filename, start_line=start_line, end_line=end_line, indent=indent)
