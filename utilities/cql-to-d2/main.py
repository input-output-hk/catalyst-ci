import os
import re
import sys
from pathlib import Path
from enum import Enum


RE_PARENS = r"\((.*?)\)"
RE_GERERIC = r"<(.*)>"
RE_COMMAS = r",\s*"
RE_SPACES = r"\s+"

DataContainerType = Enum("DataContainerType", ["NONE", "LIST", "MAP", "SET", "TUPLE", "UDT"])

class Table:
    """Represents a single table object, typically for a single CQL file."""

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.name = ""
        self.desc = ""
        self.fields: list[Field] = []
        self.clustering_keys: list[str] = []
        self.asc_keys: list[str] = []
        self.desc_keys: list[str] = []

    def alter_clustering_order(self, col_name: str, desc: bool):
        if desc and col_name in self.asc_keys:
            self.asc_keys.remove(col_name)
            self.desc_keys.append(col_name)
        if not desc and col_name in self.desc_keys:
            self.desc_keys.remove(col_name)
            self.asc_keys.append(col_name)

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

            if field.name in self.clustering_keys:
                constraint_keys.append("K")
            if field.name in self.asc_keys:
                constraint_keys.append("P↑")
            if field.name in self.desc_keys:
                constraint_keys.append("P↓")

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
        self.types: list[str] = []
        self.container_type = DataContainerType.NONE
        self.comment = ""
        self.is_static = False
        self.is_counter = False

    def is_only_comment(self):
        return self.name == "" or (len(self.types) == 0 and self.is_counter == False)

    def to_d2_format(self, constraint_keys: list[str]) -> str:
        if self.is_static:
            constraint_keys.append("S")
        if self.is_counter:
            constraint_keys.append("++")
            self.types.append("bigint")

        f_constraints = (
            " {constraint: [" + "; ".join(constraint_keys) + "]}"
            if len(constraint_keys)
            else ""
        )

        f_name = self.name
        if self.container_type == DataContainerType.LIST:
            f_name = f"[{self.name}]"
        if self.container_type == DataContainerType.SET:
            f_name = "{" + self.name + "}"
        if self.container_type == DataContainerType.MAP:
            f_name = f"<{self.name}>"
        if self.container_type == DataContainerType.TUPLE:
            f_name = f"({self.name})"
        if self.container_type == DataContainerType.UDT:
            f_name = f"*{self.name}*"

        return f"\t{f_name}: {', '.join(self.types)}" + f_constraints

def str_to_container_type(s: str) -> DataContainerType:
    try:
        return DataContainerType[s.upper()]
    except KeyError:
        return DataContainerType.NONE


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
                tokens = [x for x in re.split(RE_SPACES, line) if x]
                table.name = tokens[-2]
            # table body
            elif table.name != "" and not line.startswith(")"):
                tokens = re.split(RE_SPACES, line.strip())

                if len(tokens) == 0:
                    continue

                # primary definition line
                if tokens[0] == "PRIMARY":
                    pk_str = re.findall(RE_PARENS, line.strip())
                    partition_key_str = re.findall(RE_PARENS, pk_str[0])
                    indexed_names = re.split(RE_COMMAS, pk_str[0])

                    if len(partition_key_str):
                        table.clustering_keys = re.split(RE_COMMAS, partition_key_str[0])
                        table.asc_keys = indexed_names[len(table.clustering_keys) :]
                    else:
                        table.clustering_keys = indexed_names[0]
                        table.asc_keys = indexed_names[1:]
                # data column definition line
                else:
                    field = Field()

                    # get field name and type
                    comment_idx: None | int = None
                    type_tokens: list[str] = []
                    for i, token in enumerate(tokens):
                        if token == "--":
                            comment_idx = i
                            break
                        elif i == 0:
                            field.name = token
                        else:
                            type_tokens.append(token)

                    # join type tokens
                    type_str = re.sub(r",$", "", " ".join(type_tokens))
                    generics_items: list[str] = re.findall(RE_GERERIC, type_str)

                    if type_str.endswith(" static"):
                        field.is_static = True
                        type_str = type_str.replace(" static", "")
                    if type_str.startswith("counter"):
                        field.is_counter = True
                        type_str = type_str.replace("counter", "")
                        
                    if len(generics_items) > 0:
                        field.container_type = str_to_container_type(type_str.split("<")[0])
                        field.types = re.split(RE_COMMAS, generics_items[0])
                    else:
                        field.types = [] if type_str == "" else [ type_str ]

                    # join comments
                    comment_tokens: list[str] = []
                    if comment_idx is not None:
                        comment_tokens = tokens[(comment_idx + 1) :]

                    field.comment = " ".join(comment_tokens)

                    # add to table
                    table.fields.append(field)
            # table options
            elif table.name != "" and line.startswith(")"):
                ordering_str: list[str] = re.findall(RE_PARENS, line.strip())

                if len(ordering_str):
                    ordering_items: list[str] = re.split(RE_COMMAS, ordering_str[0])

                    for item in ordering_items:
                        [col_name, ordering_type] = re.split(RE_SPACES, item)

                        if ordering_type == "ASC":
                            table.alter_clustering_order(col_name, False)
                        elif ordering_type == "DESC":
                            table.alter_clustering_order(col_name, True)

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
