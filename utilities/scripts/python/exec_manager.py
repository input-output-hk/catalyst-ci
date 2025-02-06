# cspell: words rtype

import concurrent.futures
import multiprocessing
import subprocess
import textwrap
import time
from dataclasses import dataclass
from typing import Optional

from rich import print
from rich.table import Table
from rich.text import Text


def status_for_rc(rc: int) -> str:
    """
    Returns a status emoji based on the given RC (return code) value.

    Parameters:
        rc (int): The return code to evaluate.

    Returns:
        str: The corresponding status emoji (":white_check_mark:" for rc == 0, ":x:" otherwise).
    """
    return ":white_check_mark:" if rc == 0 else ":x:"


def format_execution_time(execution_time: float):
    """
    Formats the given execution time into a human-readable string representation.

    Args:
        execution_time (float): The execution time to format.

    Returns:
        str: The formatted execution time string.

    """
    if execution_time < 1e-3:
        execution_time *= 1e6
        unit = "us"
    elif execution_time < 1:
        execution_time *= 1e3
        unit = "ms"
    else:
        unit = "s"

    return f"{execution_time:.4f} {unit}"


def indent(text: str, first: str, rest: str) -> str:
    """
    Indent the given text using the specified indentation strings.

    Args:
        text (str): The text to be indented.
        first (str): The string to be used as the first line indentation.
        rest (str): The string to be used as the indentation for the subsequent lines.

    Returns:
        str: The indented text.
    """
    return first + textwrap.indent(text, rest)[len(first) :]


@dataclass
class ProcedureResult:
    rc: int
    cmd: str
    out: str


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
        """
        Check if the value of `rc` is equal to 0.

        :param self: The current instance of the class.
        :return: True if `rc` is equal to 0, False otherwise.
        :rtype: bool
        """
        return self.rc == 0

    def status(self) -> str:
        """
        Returns the status of the object.
        :return: A string representing the status.
        """
        return status_for_rc(self.rc)

    def duration(self) -> str:
        """
        Calculates the duration of the function execution.

        :return: A string representing the formatted execution time.
        :rtype: str
        """
        return format_execution_time(self.runtime)

    def print(
        self, verbose: bool = False, verbose_errors: bool = False, name_width: int = 0
    ) -> None:
        """
        Print the information about the task, including its name, duration, and status.

        Args:
            verbose (bool, optional): Whether to print additional information. Defaults to False.
            verbose_errors (bool, optional): Whether to print errors even when verbose is False. Defaults to False.
            name_width (int, optional): The width of the name field. Defaults to 0.

        Returns:
            None
        """
        print(
            f"[bold cyan]{self.get_name():<{name_width}}[/bold cyan] : {self.duration()} : {self.status()}"
        )
        if verbose or (self.rc != 0 and verbose_errors):
            print(
                f"[italic bright_red]{indent(self.get_command(), '  $ ', '  . ')}[/italic bright_red]"
            )
            print(Text(indent(self.out, "  > ", "  . ")))


def cli_run(
    command: str,
    name: Optional[str] = None,
    log: bool = True,
    timeout=None,
    verbose=False,
    env=None,
) -> Result:
    def procedure() -> ProcedureResult:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            env=env,
        )
        return ProcedureResult(result.returncode, command, result.stdout)

    return procedure_run(procedure, name, log, verbose)


def procedure_run(
    procedure,
    name: Optional[str] = None,
    log: bool = True,
    verbose=False,
) -> Result:
    """
    Execute a command and return the result.

    Args:
        command (str): The command to be executed.
        name (Optional[str], optional): The name of the command. Defaults to None.
        log (bool, optional): Whether to log the result. Defaults to True.
        input (Optional[str], optional): The input to be passed to the command. Defaults to None.
        timeout (Any, optional): The maximum time to wait for the command to complete. Defaults to None.
        verbose (bool, optional): Whether to print verbose errors. Defaults to False.

    Returns:
        Result: The result of executing the command.

    Note:
        - If `name` is not provided, it is set to the command itself.
        - If `input` is not provided, no input is passed to the command.
        - If `timeout` is not provided, there is no time limit for the command.
        - If `log` is True, the result is logged using `Result.print()`.

    Example:
        >>> result = run('ls -l', name='List Files', log=True, verbose=True)
    """
    start_time = time.perf_counter()

    result = procedure()

    execution_time = time.perf_counter() - start_time

    res = Result(result.rc, result.cmd, result.out, execution_time, name)

    if log:
        res.print(verbose_errors=True, verbose=verbose)

    return res


class Results:
    def __init__(self, title: str) -> None:
        """
        Initializes a new instance of the class.

        Args:
            title (str): The title of the instance.

        Returns:
            None
        """
        self.title = title
        self.results = []

    def add(self, result: Result | list[Result]) -> None:
        """
        Add a result to the list of results.

        Args:
            result (Result): The result object (or list of result objects) to be added.

        Returns:
            None
        """
        if isinstance(result, list):
            self.results.extend(result)
        else:
            self.results.append(result)

    def print(self):
        """
        Prints the results of a test run in a formatted table.

        Parameters:
            None

        Returns:
            None
        """
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

    def ok(self) -> bool:
        """
        Check if all results in the list are ok.

        :param self: The current object.
        :return: True if all results are ok, False otherwise.
        :rtype: bool
        """
        for result in self.results:
            if not result.ok():
                return False
        return True


class ParallelRunner:
    def __init__(self, name: str, max_workers: int = None) -> None:
        self.max_workers = max_workers if max_workers else multiprocessing.cpu_count()
        self.results = Results(name)
        self.executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers
        )
        self.processes = []
        self.start_time = time.perf_counter()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the multiprocessing pool when done.
        self.executor.shutdown()

    def run(self, func, *args, **kwargs) -> None:
        self.processes.append(self.executor.submit(func, *args, **kwargs))

    def get_results(self) -> Results:
        """
        A method that calculates the execution time of each process in self.processes
        and adds the results to the Results object.
        As execution time overlaps, the recalculated execution time is based on
        when tasks complete vs how long they ran internally.

        Returns a Results object.
        """
        start_time = self.start_time
        for complete in concurrent.futures.as_completed(self.processes):
            res = complete.result()
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            start_time = end_time
            if isinstance(res, list):
                for r in res:
                    r.runtime = execution_time
                    execution_time = 0.0
            else:
                res.runtime = execution_time

            self.results.add(res)

        return self.results
