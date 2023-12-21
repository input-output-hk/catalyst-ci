#!/usr/bin/env python3

# cspell: words dbmigrations dbviz dbhost dbuser dbuserpw Tsvg

from typing import Optional
import python.cli as cli
import python.db_ops as db_ops
import argparse
import rich
from rich import print
import os
import re
import json
from dataclasses import dataclass
from textwrap import indent


@dataclass
class DiagramCfg:
    title: str
    version: int
    migration_name: str
    tables: Optional[list[str]]
    included_tables: Optional[list[str]]
    excluded_tables: Optional[list[str]]
    comments: Optional[bool]
    column_description_wrap: Optional[int]
    table_description_wrap: Optional[int]
    sql_data: str

    def include(
        self, extra_includes: Optional[list[str]] = None
    ) -> Optional[list[str]]:
        # We exclude from the global include tables, any tables the migration
        # itself requests to be excluded.

        include_tables = self.included_tables if self.included_tables else []
        tables = self.tables if self.tables else []
        extra_includes = extra_includes if extra_includes else []
        excluded_tables = self.excluded_tables if self.excluded_tables else []
        
        print(excluded_tables)
        print(include_tables)
        for table in tables + extra_includes:
            print(table)
            if table not in excluded_tables and table not in include_tables:
                include_tables.append(table)

        if len(include_tables) == 0:
            include_tables = None

        return include_tables

    def exclude(
        self, extra_excludes: Optional[list[str]] = None
    ) -> Optional[list[str]]:
        # We exclude from the global exclude tables, any tables the migration
        # specifically includes.
        exclude_tables = self.excluded_tables if self.excluded_tables else []
        extra_excludes = extra_excludes if extra_excludes else []
        for table in extra_excludes:
            if table not in exclude_tables:
                exclude_tables.append(table)
        
        if len(exclude_tables) == 0:
            exclude_tables = None

        return exclude_tables


def process_sql_files(directory):
    file_pattern = r"V(\d+)__(\w+)\.sql"
    table_pattern = r"CREATE TABLE(?: IF NOT EXISTS)? (\w+)"

    diagram_option_pattern = r"^--\s*(Title|Include|Exclude|Comment|Column Description Wrap|Table Description Wrap)\s+:\s*(.*)$"

    migrations = {}
    largest_version = 0

    for filename in os.listdir(directory):
        clean_sql = ""
        title = None
        table_names = []
        included_tables = None
        excluded_tables = None
        comments = None
        column_description_wrap = None
        table_description_wrap = None
        
        match = re.match(file_pattern, filename)
        if match:
            version = int(match.group(1))
            migration_name = match.group(2)

            if version > largest_version:
                largest_version = version

            with open(os.path.join(directory, filename), "r") as file:
                sql_data = file.read()
                for line in sql_data.splitlines():
                    match = re.match(diagram_option_pattern, line)
                    if match:
                        if match.group(1).lower() == "title" and title is None:
                            title = match.group(2)
                        elif (
                            match.group(1).lower() == "include"
                            and len(match.group(2)) > 0
                        ):
                            if included_tables is None:
                                included_tables = []
                            included_tables.append(match.group(2).split())
                        elif (
                            match.group(1).lower() == "exclude"
                            and len(match.group(2)) > 0
                        ):
                            if excluded_tables is None:
                                excluded_tables = []
                            excluded_tables.append(match.group(2).split())
                        elif match.group(1).lower() == "comment":
                            if match.group(2).strip().lower() == "true":
                                comments = True
                        elif match.group(1).lower() == "column description wrap":
                            try:
                                column_description_wrap = int(match.group(2))
                            except:
                                pass
                        elif match.group(1).lower() == "table description wrap":
                            try:
                                table_description_wrap = int(match.group(2))
                            except:
                                pass
                    else:
                        # We strip diagram options from the SQL.
                        clean_sql += line + "\n"

                        match = re.match(table_pattern, line)
                        if match:
                            table_names.append(match.group(1))

            migrations[version] = DiagramCfg(
                title,
                version,
                migration_name,
                table_names,
                included_tables,
                excluded_tables,
                comments,
                column_description_wrap,
                table_description_wrap,
                clean_sql,
            )

    return migrations, largest_version


class Migrations:
    def __init__(self, args: argparse.Namespace):
        """
        Initialize the class with the given arguments.

        Args:
            args (argparse.Namespace): The command line arguments.

        Returns:
            None
        """
        self.args = args

        with open(args.diagram_config) as f:
            self.config = json.load(f)

        self.migrations, self.migration_version = process_sql_files(args.dbmigrations)

    def schema_name(self) -> str:
        return self.config.get("name", "Database Schema")

    def all_schema_comments(self) -> bool:
        return self.config.get("all_schema", {}).get("comments", False)

    def full_schema_comments(self) -> bool:
        return self.config.get("full_schema", {}).get(
            "comments", self.all_schema_comments()
        )

    def all_schema_included_tables(self) -> list[str]:
        return self.config.get("all_schema", {}).get("included_tables", [])

    def all_schema_excluded_tables(self) -> list[str]:
        return self.config.get("all_schema", {}).get("excluded_tables", [])

    def full_schema_excluded_tables(self) -> list[str]:
        return self.config.get("full_schema", {}).get(
            "excluded_tables", self.all_schema_excluded_tables()
        )

    def all_schema_column_description_wrap(self) -> int:
        return self.config.get("all_schema", {}).get("column_description_wrap", 50)

    def full_schema_column_description_wrap(self) -> int:
        return self.config.get("full_schema", {}).get(
            "column_description_wrap", self.all_schema_column_description_wrap()
        )

    def all_schema_table_description_wrap(self) -> int:
        return self.config.get("all_schema", {}).get("table_description_wrap", 50)

    def full_schema_table_description_wrap(self) -> int:
        return self.config.get("full_schema", {}).get(
            "table_description_wrap", self.all_schema_table_description_wrap()
        )

    def dbviz(
        self,
        filename: str,
        name: str,
        title: str,
        included_tables: Optional[list[str]] = None,
        excluded_tables: Optional[list[str]] = None,
        comments: Optional[bool] = None,
        column_description_wrap: Optional[int] = None,
        table_description_wrap: Optional[int] = None,
    ) -> cli.Result:
        if len(title) > 0:
            title = f' --title "{title}"'

        if included_tables and len(included_tables) > 0:
            included_tables = " -i " + " ".join(included_tables)
        else:
            included_tables = ""

        if excluded_tables and len(excluded_tables) > 0:
            excluded_tables = " -e " + " ".join(excluded_tables)
        else:
            excluded_tables = ""

        if comments:
            comments = " --comments"
        else:
            comments = ""

        if column_description_wrap and column_description_wrap > 0:
            column_description_wrap = (
                f" --column-description-wrap {column_description_wrap}"
            )
        else:
            column_description_wrap = ""

        if table_description_wrap and table_description_wrap > 0:
            table_description_wrap = (
                f" --table-description-wrap {table_description_wrap}"
            )
        else:
            table_description_wrap = ""

        res = cli.run(
            f"dbviz -d {self.args.dbname}"
            + f" -h {self.args.dbhost}"
            + f" -u {self.args.dbuser}"
            + f" -p {self.args.dbuserpw}"
            + f"{title}"
            + f"{included_tables}"
            + f"{excluded_tables}"
            + f"{comments}"
            + f"{column_description_wrap}"
            + f"{table_description_wrap}"
            + f" > {filename}.dot",
            name=f"Generate Schema Diagram: {name}",
            verbose=True
        )

        if res.ok:
            cli.run(
                f"dot -Tsvg {filename}.dot -o {filename}",
                name=f"Render Schema Diagram to SVG: {name}",
                verbose=True,
            )

        return res

    def full_schema_diagram(self) -> cli.Result:
        # Create a full Schema Diagram.
        return self.dbviz(
            "docs/full-schema.svg",
            "Full Schema",
            self.schema_name(),
            excluded_tables=self.full_schema_excluded_tables(),
            comments=self.full_schema_comments(),
            column_description_wrap=self.full_schema_column_description_wrap(),
            table_description_wrap=self.full_schema_table_description_wrap(),
        )

    def migration_schema_diagram(self, ver: int) -> cli.Result:
        # Create a schema diagram for an individual migration.
        if ver in self.migrations:
            migration = self.migrations[ver]

            include_tables = migration.include(self.all_schema_included_tables())
            if include_tables is None:
                return cli.Result(
                    0,
                    "",
                    "",
                    0.0,
                    f"Migration {ver} has no tables to diagram.",
                )

            exclude_tables = migration.exclude(self.all_schema_excluded_tables())
            
            title = f"{migration.migration_name}"
            if migration.title and len(migration.title) > 0:
                title = migration.title

            return self.dbviz(
                f"docs/migration-{ver}.svg",
                f"V{ver}__{migration.migration_name}",
                title,
                included_tables=include_tables,
                excluded_tables=exclude_tables,
                comments=migration.comments,
                column_description_wrap=migration.column_description_wrap,
                table_description_wrap=migration.table_description_wrap,
            )

    def create_diagrams(self, results: cli.Results) -> cli.Results:
        # Create a full Schema Diagram first.
        res = self.full_schema_diagram()
        results.add(res)

        for ver in sorted(self.migrations.keys()):
            res = self.migration_schema_diagram(ver)
            results.add(res)

        # cli.run("ls -al docs", verbose=True)

        return results

    def create_markdown_file(self, file_path):
        with open(file_path, "w") as markdown_file:
            # Write the title with the maximum migration version
            markdown_file.write(
                "# Migrations (Version {}) \n\n".format(self.migration_version)
            )

            # Link the full schema diagram.
            markdown_file.write('??? example "Full Schema Diagram"\n\n')
            markdown_file.write(
                '    ![Full Schema](./full-schema.svg "Full Schema")\n\n'
            )

            # Write the contents of each file in order
            for version in sorted(self.migrations.keys()):
                migration = self.migrations[version]
                sql_data = migration.sql_data.strip()

                # Write the title of the file
                markdown_file.write(f"## {migration.migration_name}\n\n")

                if os.path.exists(f"docs/migration-{version}.svg"):
                    markdown_file.write('??? example "Schema Diagram"\n\n')
                    markdown_file.write(
                        f"    ![Migration {migration.migration_name}]"
                        + f'(./migration-{version}.svg "{migration.migration_name}")\n\n'
                    )

                markdown_file.write('??? abstract "Schema Definition"\n\n')
                markdown_file.write(
                    indent(f"```postgres\n{sql_data}\n```", "    ") + "\n\n"
                )

        print("Markdown file created successfully at: {}".format(file_path))


def main():
    # Force color output in CI
    rich.reconfigure(color_system="256")

    parser = argparse.ArgumentParser(
        description="Standard Postgresql Documentation Processing."
    )
    parser.add_argument("diagram_config", help="Diagram Configuration JSON")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    db_ops.add_args(parser)

    args = parser.parse_args()

    db = db_ops.DBOps(args)

    results = cli.Results("Generate Database Documentation")

    # Init the DB.
    res = db.init_database()
    results.add(res)

    if res.ok():
        db.start()
        res = db.wait_ready(timeout=10)
        results.add(res)

    if res.ok():
        res = db.setup()
        results.add(res)

    if res.ok():
        res = db.migrate_schema()
        results.add(res)

    if res.ok():
        cli.run("mkdir docs")  # Where we build the docs.

        # Get all info about the migrations.
        migrations = Migrations(args)
        results = migrations.create_diagrams(results)

    if results.ok():
        migrations.create_markdown_file("docs/migrations.md")
        # cli.run("cat /tmp/migrations.md", verbose=True)

    results.print()
    
    if not results.ok():
        exit(1)

if __name__ == "__main__":
    main()
