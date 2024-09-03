import os
import re
import sys
from pathlib import Path


class Table:
    """Represents a single table object, typically for a single CQL file."""

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.name = ""
        self.desc = ""
        self.fields: list[Field] = []
        self.pk: list[str] = []

    def to_d2_format(self) -> str:
        # format tooltip
        f_tooltip_lines: list[str] = []
        if self.desc:
            f_tooltip_lines.append(f"-- {self.desc}\n")

        # format fields
        f_field_lines: list[str] = []
        for field in self.fields:
            if field.is_only_comment():
                f_tooltip_lines.append(f"-- {field.comment}")
                continue

            constraint_keys: list[str] = []

            if field.name in self.pk:
                constraint_keys.append("K")

            f_field_lines.append(field.to_d2_format(constraint_keys))
            f_tooltip_lines.append(f"{field.name} -- {field.comment}")

        return "\n".join(
            [
                self.name + ": {",
                "\tshape: sql_table",
                "\ttooltip: |md",
                "\n".join([f"\t\t{li}" for li in f_tooltip_lines]),
                "\t|",
                "",
                "\n".join(f_field_lines),
                "}",
            ]
        )


class Field:
    """Represents a field inside a table."""

    def __init__(self) -> None:
        self.name = ""
        self.type = ""
        self.comment = ""

    def is_only_comment(self):
        return self.name == "" or self.type == ""

    def to_d2_format(self, constraint_keys: str) -> str:
        f_constraints = (
            " {constraint: [" + "; ".join(constraint_keys) + "]}"
            if len(constraint_keys)
            else ""
        )

        return "\t" + self.name + f": {self.type}" + f_constraints


def parse_src(src_dir: str) -> list[Table]:
    """Reads the target directory and parses all the CQL files."""

    if not os.path.isdir(src_dir):
        raise Exception(f"'{src_dir}' is not a directory.")

    return [
        parse_file(os.path.join(src_dir, f))
        for f in os.listdir(src_dir)
        if os.path.isfile(os.path.join(src_dir, f)) and f.endswith(".cql")
    ]


def parse_file(file_path: str) -> Table:
    """Reads a CQL file and parses the file."""

    table = Table(extract_filename_without_ext(file_path))

    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            if line.strip() == "":
                continue

            # table description
            if table.name == "" and line.startswith("--"):
                table.desc += (
                    table.desc
                    + ("" if table.desc == "" else " ")
                    + line[2:].strip()
                )
            # table name
            elif table.name == "" and "CREATE TABLE" in line:
                tokens = [x for x in re.split(r"\s+", line) if x]
                table.name = tokens[-2]
            # table fields
            elif table.name != "" and not line.startswith(")"):
                tokens = re.split(r"\s+", line.strip())

                if len(tokens) == 0:
                    continue

                if tokens[0] == "PRIMARY":
                    matches = re.findall(r"\((.*?)\)", line.strip())
                    indexed_names = re.split(r",\s*", matches[0])

                    table.pk = indexed_names
                else:
                    field = Field()

                    # get field name and type
                    comment_idx: None | int = None
                    for i, token in enumerate(tokens):
                        if token == "--":
                            comment_idx = i
                            break
                        elif i == 0:
                            field.name = token
                        elif i == 1:
                            field.type = token.replace(",", "")

                    # join comments
                    comment_tokens: list[str] = []
                    if comment_idx is not None:
                        comment_tokens = tokens[(comment_idx + 1) :]

                    field.comment = " ".join(comment_tokens)

                    # add to table
                    table.fields.append(field)

    return table


def extract_filename_without_ext(path: str) -> str:
    base_name = os.path.basename(path)
    file_name, _ = os.path.splitext(base_name)
    return file_name


def write_to_file(dir_path: str, file_name: str, content: str):
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    with open(f"{dir_path}/{file_name}.d2", "w") as file:
        file.write(content)


def main():
    if len(sys.argv) != 3:
        raise Exception("Requires <src-dir> and <out-dir> to execute.")

    [_, src_dir, out_dir] = sys.argv

    abs_src_dir = os.path.abspath(src_dir)
    abs_out_dir = os.path.abspath(out_dir)

    tables = parse_src(abs_src_dir)

    for table in tables:
        write_to_file(abs_out_dir, table.file_name, table.to_d2_format())


if __name__ == "__main__":
    main()
