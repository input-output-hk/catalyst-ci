# High level Postgres Database Operations

# cspell: words dbhost dbport dbname dbuser dbuserpw dbsuperuser dbsuperuserpw
# cspell: words dbnamesuperuser dbdescription dbpath dbauthmethod dbcollation
# cspell: words dbreadytimeout setupdbsql dbrefinerytoml dbmigrations
# cspell: words dbseeddatasrc pwfile pgctl rtype initdb isready

import argparse
import os
import time
from typing import Optional
import python.cli as cli
import tempfile
import threading

DB_ARGUMENTS = [
    ["dbhost", "DB_HOST", "localhost"],
    ["dbport", "DB_PORT", 5432],
    ["dbname", "DB_NAME", "public"],
    ["dbuser", "DB_USER", "postgres"],
    ["dbuserpw", "DB_USER_PASSWORD", "CHANGE_ME"],
    ["dbsuperuser", "DB_SUPERUSER", "admin"],
    ["dbsuperuserpw", "DB_SUPERUSER_PASSWORD", "CHANGE_ME"],
    ["dbnamesuperuser", "DB_NAME_SUPERUSER", "postgres"],
    ["dbdescription", "DB_DESCRIPTION", "PostgreSQL Database"],
    ["dbpath", "DB_PATH", "/var/lib/postgresql/data"],
    ["dbauthmethod", "DB_AUTH_METHOD", "trust"],
    ["dbcollation", "DB_COLLATION", "en_US.utf8"],
    ["dbreadytimeout", "DB_READY_TIMEOUT", None],
    ["setupdbsql", "SETUP_DB_SQL", "/sql/setup-db.sql"],
    ["dbrefinerytoml", "DB_REFINERY_TOML", "./refinery.toml"],
    ["dbmigrations", "DB_MIGRATIONS", "./migrations"],
    ["dbseeddatasrc", "DB_SEED_DATA_SRC", "./seed"],
    ["init_and_drop_db", "INIT_AND_DROP_DB", False],
    ["with_migrations", "WITH_MIGRATIONS", False],
    ["with_seed_data", "WITH_SEED_DATA", None],
]


def add_args(parser: argparse.ArgumentParser):
    """
    Adds the command line arguments to the given `argparse.ArgumentParser` object.

    Args:
        parser (argparse.ArgumentParser): The `argparse.ArgumentParser` object to which the command line arguments will be added.

    Returns:
        None
    """
    for opt in DB_ARGUMENTS:
        parser.add_argument(
            f"--{opt[0]}",
            default=os.environ.get(opt[1], opt[2]),
        )


class DBOps:
    def __init__(self, args: argparse.Namespace):
        """
        Initialize the class with the given arguments.

        Args:
            args (argparse.Namespace): The command line arguments.

        Returns:
            None
        """
        self.args = args

    def user_connection(self) -> str:
        """
        Generate a connection string for the user.

        Returns:
            str: The connection string in the format postgres://<dbuser>:<dbuserpw>@<dbhost>:<dbport>/<dbname>
        """
        return f"postgres://{self.args.dbuser}:{self.args.dbuserpw}@{self.args.dbhost}:{self.args.dbport}/{self.args.dbname}"

    def superuser_connection(self) -> str:
        """
        Generates a connection string for the superuser to connect to the database.

        :return: The connection string for the superuser.
        :rtype: str
        """
        return f"postgres://{self.args.dbsuperuser}:{self.args.dbsuperuserpw}@{self.args.dbhost}:{self.args.dbport}/{self.args.dbnamesuperuser}"

    def init_database(self) -> cli.Result:
        """
        Initializes the database by creating a temporary password file, running the 'initdb' command,
        and updating the 'pg_hba.conf' file. The function takes no parameters and returns a 'cli.Result' object.
        """

        with tempfile.NamedTemporaryFile(delete=False) as pwfile:
            pwfile.write(self.args.dbsuperuserpw.encode())
            pwfile.flush()

            # Initialize the database
            res = cli.run(
                f"initdb -D {self.args.dbpath}"
                + f" --locale-provider=icu --icu-locale={self.args.dbcollation} --locale={self.args.dbcollation}"
                + f" -A {self.args.dbauthmethod}"
                + f" -U {self.args.dbsuperuser} --pwfile={pwfile.name}",
                name="Initializing Database",
            )

            os.remove(pwfile.name)

        if res.ok():
            with open(f"{self.args.dbpath}/pg_hba.conf", "a") as file:
                file.write(f"include_if_exists {self.args.dbpath}/pg_hba.extra.conf\n")
                file.write(f"include_if_exists /sql/pg_hba.extra.conf\n")

        return res

    def __start(self):
        """
        Start the database.

        This function starts the database by running the command `pg_ctl -D "{dbpath}" start`,
        where `dbpath` is the path to the database directory.

        Parameters:
            None

        Returns:
            None
        """
        # print("Starting Database")
        cli.run(
            f'pg_ctl -D "{self.args.dbpath}" start',
            name="Starting Database",
            verbose=True,
        )

    def start(self) -> None:
        """
        Start the process of starting the database server.

        This function starts the database server by spawning a subprocess using `pg_ctl` command.
        It does this inside a `threading.Thread` to prevent the `Popen` from returning
        and checks for the database to start later.

        Parameters:
            None

        Returns:
            None
        """

        # `pgctl` will spawn a subprocess itself, this will prevent the python
        # POpen from returning.  So, we do that here inside a thread, and we
        # check for the DB to start later.

        proc = threading.Thread(target=self.__start, daemon=True)
        proc.start()
        time.sleep(0.1)  # Give the thread a chance to actually run.

        return

    def db_ready(self) -> cli.Result:
        """
        Check if the database is ready for use.

        :return: A `cli.Result` object containing the result of the `pg_isready` command.
        """
        return cli.run(
            f"pg_isready -d {self.superuser_connection()}", name="Database Ready"
        )

    def wait_ready(self, timeout: Optional[int] = None) -> cli.Result:
        """
        Waits for the database to be ready within the specified timeout period.

        Parameters:
            timeout (Optional[int]): The maximum number of seconds to wait for the database to be ready. Defaults to None.

        Returns:
            cli.Result: An object representing the result of the database readiness check.
        """
        start_time = time.perf_counter()

        while not self.db_ready().ok() and (
            time is None or time.perf_counter() - start_time < timeout
        ):
            time.sleep(1)

        res = self.db_ready()
        res.runtime = time.perf_counter() - start_time

        return res

    def setup(self) -> cli.Result:
        """
        Setup the default User and Database.
        
        WARNING: Will destroy all data in the DB
        
        :return: The result of running the setup command.
        :rtype: cli.Result
        """
        # Setup the default User and Database
        # WARNING: Will destroy all data in the DB

        return cli.run(
            f"psql -v ON_ERROR_STOP=on"
            + f" -d {self.superuser_connection()} "
            + f" -f {self.args.setupdbsql}"
            + f' -v dbName="{self.args.dbname}"'
            + f' -v dbDescription="{self.args.dbdescription}"'
            + f' -v dbUser="{self.args.dbuser}"'
            + f' -v dbUserPw="{self.args.dbuserpw}"',
            name="Setup Database",
            verbose=True
        )

    def migrate_schema(self) -> cli.Result:
        """
        Run schema migrations.

        :return: A cli.Result object representing the result of running the migrations.
        """
        # Run schema migrations
        return cli.run(
            f"DATABASE_URL={self.user_connection()}"
            + f" refinery migrate -e DATABASE_URL"
            + f" -c {self.args.dbrefinerytoml} "
            + f" -p {self.args.dbmigrations}",
            name="Migrate Schema",
            verbose=True,
        )
