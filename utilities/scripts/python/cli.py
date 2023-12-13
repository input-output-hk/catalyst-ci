#!/usr/bin/env python3

# cspell: words rtype

import subprocess
from typing import Optional
from rich import print
from rich.table import Table
from dataclasses import dataclass
import textwrap
import time
import shlex


def status_for_rc(rc: int) -> str:
    return ":white_check_mark:" if rc == 0 else ":x:"


def format_execution_time(execution_time: float):
    if execution_time < 1e-3:
        execution_time *= 1e6
        unit = "us"
    elif execution_time < 1:
        execution_time *= 1e3
        unit = "ms"
    else:
        unit = "s"

    return f"{execution_time:.4f} {unit}"


@dataclass
class Result:
    rc: int
    cmd: str
    out: str
    runtime: float
    name: Optional[str] = None

    def get_command(self) -> str:
        """
        Returns the command of the object.
        :return: A string representing the command of the object.
        :rtype: str
        """
        return self.cmd

    def get_name(self) -> str:
        """
        Returns the name of the object.
        :return: A string representing the name of the object.
        :rtype: str
        """
        return self.name or self.get_command()

    def ok(self) -> bool:
        return self.rc == 0

    def status(self) -> str:
        return status_for_rc(self.rc)

    def duration(self) -> str:
        return format_execution_time(self.runtime)

    def print(
        self, verbose: bool = False, verbose_errors: bool = False, name_width: int = 0
    ) -> None:
        print(
            f"[bold cyan]{self.get_name():<{name_width}}[/bold cyan] : {self.duration()} : {self.status()}"
        )
        if verbose or (self.rc != 0 and verbose_errors):
            print(f"[italic]{textwrap.indent(self.get_command(), '  $ ')}[/italic]")
            print(f"{textwrap.indent(self.out, '  > ')}")


def run(
    command: str,
    name: Optional[str] = None,
    log: bool = True,
    input: Optional[str] = None,
    timeout=None,
    verbose=False,
) -> Result:
    start_time = time.perf_counter()

    result = subprocess.run(
        command,
        shell=True,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )

    execution_time = time.perf_counter() - start_time

    res = Result(result.returncode, command, result.stdout, execution_time, name)

    if log:
        res.print(verbose_errors=True, verbose=verbose)

    return res


class Results:
    def __init__(self, title: str) -> None:
        self.title = title
        self.results = []

    def add(self, result: Result):
        self.results.append(result)

    def print(self):
        table = Table(title=self.title)
        table.add_column("Step", style="cyan")
        table.add_column("Duration", style="magenta")
        table.add_column("OK", style="green")

        total_rc = 0
        total_runtime = 0.0
        for result in self.results:
            table.add_row(result.get_name(), result.duration(), result.status())
            total_rc += result.rc
            total_runtime += result.runtime

        table.add_section()
        table.add_row(
            "Summary", format_execution_time(total_runtime), status_for_rc(total_rc)
        )

        print(table)
