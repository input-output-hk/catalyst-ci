# Checks if two files that should exist DO, and are equal.
# used to enforce consistency between local config files and the expected config locked in CI.

import python.cli as cli

def colordiff_check(vendor_file_path: str, provided_file_path: str) -> cli.Result:
    return cli.run(f"colordiff -Nau {provided_file_path} {vendor_file_path}",
                    name=f"Checking if Provided File {provided_file_path} == Vendored File {vendor_file_path}")
