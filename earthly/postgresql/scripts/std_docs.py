#!/usr/bin/env python3

# cspell: words dbmigrations dbhost dbuser dbuserpw Tsvg pgsql11

from typing import Optional
import python.exec_manager as exec_manager
import python.db_ops as db_ops
import argparse
import rich
from rich import print
import os
import re
from textwrap import indent

def process_sql_files(directory):
    file_pattern = r"V(\d+)__(\w+)\.sql"
    migrations = {}
    largest_version = 0

    for filename in os.listdir(directory):
        match = re.match(file_pattern, filename)
        if match:
            version = int(match.group(1))
            migration_name = match.group(2)

            if version > largest_version:
                largest_version = version

            with open(os.path.join(directory, filename), "r") as file:
                sql_data = file.read()

            migrations[version] = {
                "version": version,
                "migration_name": migration_name,
                "sql_data": sql_data
            }

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
        self.migrations, self.migration_version = process_sql_files(args.dbmigrations)

    def create_markdown_file(self, file_path):
        with open(file_path, "w") as markdown_file:
            # Write the title with the maximum migration version
            markdown_file.write(
                "# Migrations (Version {}) \n\n".format(self.migration_version)
            )

            # Write the contents of each file in order
            for version in sorted(self.migrations.keys()):
                migration = self.migrations[version]
                sql_data = migration["sql_data"].strip()

                # Write the title of the file
                markdown_file.write(f"## {migration['migration_name']}\n\n")

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
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    db_ops.add_args(parser)

    args = parser.parse_args()

    db = db_ops.DBOps(args)

    results = exec_manager.Results("Generate Database Documentation")

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
        # Create the docs directory
        exec_manager.cli_run("mkdir -p docs")  # Where we build the docs.

        # Get all info about the migrations.
        migrations = Migrations(args)

    if results.ok():
        schemaspy_cmd = (
            f"java -jar /bin/schemaspy.jar -t pgsql11 "
            f"-dp /bin/postgresql.jar "
            f"-db {args.dbname} "
            f"-host {args.dbhost} "
            f"-u {args.dbuser} "
            f"-p {args.dbuserpw} "
            f"-o docs/database_schema/ "
        )
        res = exec_manager.cli_run(
            schemaspy_cmd,
            name="Generate SchemaSpy Documentation",
            verbose=True
        )
        results.add(res)

        # If SchemaSpy command completes without error, create .pages file to hide the schema folder
        if res.ok():
            exec_manager.cli_run(
                'echo "hide: true" > docs/database_schema/.pages',
                name="Create .pages file",
                verbose=True
            )

        migrations.create_markdown_file("docs/migrations.md")

    results.print()

    if not results.ok():
        exit(1)

if __name__ == "__main__":
    main()