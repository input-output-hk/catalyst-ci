#!/usr/bin/env python3

# cspell: words gmtime

import subprocess
import time
import webbrowser
from dataclasses import dataclass, field
import argparse
import sys
import urllib.request


class ProcessRunError(Exception):
    pass


class DocBuildError(Exception):
    pass


class DocContainerNotFoundError(Exception):
    pass


class ImageNotFound(Exception):
    pass


def run_command(command):
    """
    Run a command and print its output.

    Args:
        command (str): The command to be executed.

    Returns:
        int: The exit code of the command.
    """
    if isinstance(command, list):
        command = " ".join(command)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True,
    )

    for line in iter(process.stdout.readline, ""):
        print(line, end="")

    process.stdout.close()

    rc = process.wait()

    if rc != 0:
        raise ProcessRunError(f"Command '{command}' failed with exit code {rc}.")


@dataclass
class DocsContainer:
    # Images Name
    name: str
    target: str
    exposed_port: int

    image_id: str = field(default="")
    container_id: str = field(default="")
    last_log_time: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

    def __post_init__(self):
        """
        Builds and Retrieves information about docs container.

        This function is a post-initialization hook that is called after the object is initialized.
        It retrieves information about a container, such as its ID, status, image, and creation timestamp.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None

        Raises:
            DocBuildError: If there is an error while running the command.
            DocContainerNotFoundError: If the container with the specified name is not found.
        """
        # Make sure the container target is up-to-date
        # try:
        #     run_command(["earthly", self.target])
        # except ProcessRunError as exc:
        #     raise DocBuildError from exc

        try:
            # Get the container image ID
            result = subprocess.run(
                ["docker", "images", "-q", self.name], capture_output=True, text=True
            )
            self.image_id = result.stdout.strip()
        except subprocess.CalledProcessError:
            raise ImageNotFound(f"Image '{self.name}' not found.")

    def run_container(self):
        """
        Runs a Docker container.

        :return: None
        :raises ProcessRunError: If the Docker container fails to start.
        """
        try:
            # Run the Docker container
            cmd = [
                "docker",
                "run",
                "-d",
                "-p",
                f"{self.exposed_port}:80",
                "--restart",
                "no",
                "--rm",
                "--name",
                self.name.replace(":", "_"),
                self.name,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.container_id = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ProcessRunError from e

    def stop_container(self):
        """
        Stops the Docker container.

        This function stops the Docker container specified by `self.container_id`. It uses the `docker stop` command to stop the container. After stopping the container, it waits until Docker has finished stopping the container.

        Parameters:
            None

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: If there is an error stopping or removing the Docker container.
        """
        try:
            # Stop the Docker container
            subprocess.run(["docker", "stop", self.name.replace(":", "_")])

            # Wait until Docker has finished stopping the container
            while True:
                result = subprocess.run(
                    ["docker", "ps", "-aq", "--filter", f"id={self.container_id}"],
                    capture_output=True,
                    text=True,
                )
                if result.stdout.strip() == "":
                    break
                time.sleep(1)
        except subprocess.CalledProcessError as e:
            print(f"Error stopping or removing Docker container: {e}")

    def print_logs(self):
        cmd = f"docker logs --since {self.last_log_time} {self.container_id}"
        output = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        for line in output.stdout:
            print(line.decode().strip())
        self.last_log_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="View docs locally and re-deploy if the docs source changes."
    )
    parser.add_argument("container_name", help="Name of the container")
    parser.add_argument(
        "--exposed-port", type=int, default=8123, help="Exposed port of the container"
    )
    parser.add_argument(
        "--target", default="./docs+local", help="Earthly target to run"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not open the browser"
    )
    args = parser.parse_args()

    # Create a ContainerInfo instance
    docs_container = DocsContainer(
        name=args.container_name, target=args.target, exposed_port=args.exposed_port
    )

    browsed = False
    while True:
        try:
            docs_container.run_container()

            # Wait until the exposed port returns a valid response
            while True:
                try:
                    url = f"http://localhost:{docs_container.exposed_port}"
                    with urllib.request.urlopen(url) as response:
                        if response.getcode() == 200:
                            break
                except (urllib.error.URLError, ConnectionResetError):
                    pass
                time.sleep(1)

            # Open the webpage in a browser (once)
            if not browsed:
                browsed=True
                if not args.no_browser:
                    webbrowser.open(f"http://localhost:{docs_container.exposed_port}")

            while True:
                docs_container.print_logs()
                # Wait for 10 seconds
                time.sleep(10)

                try:
                    new_docs = DocsContainer(
                        name=args.container_name,
                        target=args.target,
                        exposed_port=args.exposed_port,
                    )
                    if docs_container.image_id != new_docs.image_id:
                        docs_container.stop_container()
                        docs_container = new_docs
                        docs_container.run_container()
                        break
                    else:
                        print("Docs did not change. Waiting...")
                except Exception as exc:
                    print(f"Error rebuilding docs: {exc}")

        except KeyboardInterrupt:
            print("\nExiting...")
            docs_container.stop_container()
            sys.exit(0)


if __name__ == "__main__":
    main()
