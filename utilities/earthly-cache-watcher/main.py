# cspell: words dotenv levelname loguru

import os
import sys
import threading
import time
from collections.abc import Callable
from typing import Set

from dotenv import dotenv_values
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import helper

logger.remove()  # Remove the default handler
logger.add(sys.stdout, level="INFO", serialize=True, format="{message}")

class Interval:
    """
    A class that repeatedly executes a function
    at specified intervals in a separate thread.
    """

    def __init__(self, interval: int, func: Callable[[], None]):
        """
        Initializes the Interval instance
        with the specified interval and function.
        """

        self.interval = interval
        self.func = func
        self.stop_event = threading.Event()

        thread = threading.Thread(target=self.set_interval)
        thread.start()

    def set_interval(self):
        """
        Repeatedly executes the function at
        the specified interval until the stop event is set.
        """

        next_time = time.time() + self.interval
        while not self.stop_event.wait(next_time - time.time()):
            next_time += self.interval
            self.func()

    def drop(self):
        """
        Signals the thread to stop executing the function.
        """

        self.stop_event.set()


class ChangeEventHandler(FileSystemEventHandler):
    """
    Handles file system events.
    """

    def __init__(self, interval: int):
        self.layer_growth_index: dict[str, int] = {}
        self.layer_index: dict[str, int] = {}
        self.file_index: dict[str, int] = {}
        self.triggered_layers: Set[str] = set()
        self.triggered_growth_layers: Set[str] = set()
        self.interval = Interval(interval, self.handle_interval_change)

        self.list_initial_sizes()

    def list_initial_sizes(self):
        """
        Lists initial file sizes during initialization.
        """

        logger.info("initializing...")

        for root, _directories, files in os.walk(watch_dir):
            for filename in files:
                dir_abspath = os.path.abspath(root)
                file_path = os.path.join(dir_abspath, filename)
                layer_name = helper.get_subdirectory_name(watch_dir, file_path)

                if not os.path.isfile(file_path):
                    continue

                try:
                    size = os.path.getsize(file_path)

                    self.file_index[file_path] = size
                    helper.add_or_init(self.layer_index, layer_name, size)

                    logger.debug(
                        f"initial file: {file_path} (size: {size:,} bytes)"
                    )
                except OSError as e:
                    if log_file_accessing_err:
                        logger.error(f"error accessing file: {file_path} ({e})")

        # checks total
        self.check_sizes(layer_name="")

        # check individual
        for layer_name in self.layer_index:
            self.check_sizes(layer_name, skip_sum_check=True)

        logger.info("finished initializing")

    def on_any_event(self, event):
        """
        Logs any file system event.
        """

        if event.is_directory:
            return None

        if event.event_type == "created":
            self.handle_created(event.src_path)
        elif event.event_type == "modified":
            self.handle_modified(event.src_path)
        elif event.event_type == "moved":
            self.handle_moved(event.src_path, event.dest_path)
        elif event.event_type == "deleted":
            self.handle_deleted(event.src_path)

        logger.debug(event.event_type)

    def handle_interval_change(self):
        logger.debug("interval changed")

        self.layer_growth_index.clear()
        self.triggered_growth_layers.clear()

    def handle_created(self, file_path: str):
        logger.debug(f"new file created: {file_path}")

        try:
            layer_name = helper.get_subdirectory_name(watch_dir, file_path)
            size = os.path.getsize(file_path)

            self.file_index[file_path] = size
            helper.add_or_init(self.layer_index, layer_name, size)
            helper.add_or_init(self.layer_growth_index, layer_name, size)

            # checks
            self.check_sizes(layer_name)
        except OSError as e:
            if log_file_accessing_err:
                logger.error(f"error accessing file: {file_path} ({e})")

    def handle_modified(self, file_path: str):
        logger.debug(f"file modified: {file_path}")

        try:
            layer_name = helper.get_subdirectory_name(watch_dir, file_path)
            size = os.path.getsize(file_path)

            if file_path not in self.file_index:
                self.handle_created(file_path)
            elif size != self.file_index[file_path]:
                prev_size = self.file_index[file_path]
                d_size = size - prev_size

                self.file_index[file_path] = size
                helper.add_or_init(self.layer_index, layer_name, d_size)
                helper.add_or_init(self.layer_growth_index, layer_name, d_size)

                # checks
                self.check_sizes(layer_name)

                logger.debug(" ".join([
                    f"file modified: {file_path}",
                    f"(size changed from {prev_size:,} bytes",
                    f"to {size:,} bytes)"
                ]))
            else:
                logger.debug(f"file modified: {file_path} (size unchanged)")
        except OSError as e:
            if log_file_accessing_err:
                logger.error(f"error accessing file: {file_path} ({e})")

    def handle_moved(self, src_path: str, dest_path: str):
        logger.debug(f"file moved: {src_path}")

        src_layer_name = helper.get_subdirectory_name(watch_dir, src_path)
        dest_layer_name = helper.get_subdirectory_name(watch_dir, dest_path)

        if src_path in self.file_index:
            size = self.file_index[src_path]
            self.file_index[dest_path] = size
            del self.file_index[src_path]

            if src_layer_name != dest_layer_name:
                helper.add_or_init(self.layer_index, src_layer_name, -size)
                helper.add_or_init(self.layer_index, dest_layer_name, size)

    def handle_deleted(self, file_path: str):
        logger.debug(f"file deleted: {file_path}")

        if file_path in self.file_index:
            layer_name = helper.get_subdirectory_name(watch_dir, file_path)
            prev_size = self.file_index[file_path]

            del self.file_index[file_path]

            helper.add_or_init(self.layer_index, layer_name, -prev_size)
            helper.add_or_init(self.layer_growth_index, layer_name, -prev_size)

            if self.layer_index[layer_name] < large_layer_size:
                self.triggered_layers.discard(layer_name)
            if self.layer_index[layer_name] <= 0:
                del self.layer_index[layer_name]

    def check_sizes(self, layer_name: str, skip_sum_check=False):
        if (
            layer_name in self.layer_index
            and self.layer_index[layer_name]
            >= large_layer_size
        ):
            self.trigger_layer_size_exceeded(layer_name)

        if (
            not skip_sum_check
            and sum(self.layer_growth_index.values())
            >= max_time_window_growth_size
        ):
            self.trigger_interval_growth_exceeded()

        if (
            not skip_sum_check
            and sum(self.layer_index.values()) >= max_cache_size
        ):
            self.trigger_max_cache_size()

    def trigger_layer_size_exceeded(self, layer_name: str):
        if layer_name in self.triggered_layers:
            return

        self.triggered_layers.add(layer_name)

        logger.error(
            " ".join([
                f"layer '{layer_name}' exceeds large layer size criteria",
                f"(size: {self.layer_index[layer_name]:,} bytes",
                f"- limit: {large_layer_size:,} bytes)"
            ]),
            extra={
                "err_type": "layer_size_exceeded",
                "layer": layer_name,
                "size": self.layer_index[layer_name],
                "limit": large_layer_size
            }
        )

    def trigger_interval_growth_exceeded(self):
        try:
            has_triggered_layer = False
            for layer_name, size in self.layer_growth_index.items():
                if layer_name in self.triggered_growth_layers:
                    continue

                has_triggered_layer = True
                self.triggered_growth_layers.add(layer_name)

                logger.error(
                    " ".join([
                        f"layer '{layer_name}'",
                        f"- {size:,} bytes within the interval"
                    ]),
                    extra={
                        "err_type": "layer_list_growth_exceeded",
                        "layer": layer_name,
                        "size": size
                    }
                )

            if has_triggered_layer:
                size = sum(self.layer_growth_index.values())

                logger.error(
                    " ".join([
                        "the total amount of cache growth",
                        f"within {time_window:,} secs exceeds the limit",
                        f"(size: {size:,} bytes",
                        f"- limit: {max_time_window_growth_size:,} bytes)"
                    ]),
                    extra={
                        "err_type": "interval_growth_exceeded",
                        "size": size,
                        "limit": max_time_window_growth_size,
                        "within": time_window
                    }
                )
        except RuntimeError as e:
            logger.error(f"an error occurred: {e}")

    def trigger_max_cache_size(self):
        size = sum(self.layer_index.values())

        logger.error(
            " ".join([
                "the total amount of cache exceeds the limit",
                f"(size: {size:,} bytes",
                f"- limit: {max_cache_size:,} bytes)"
            ]),
            extra={
                "err_type": "max_cache_size_exceeded",
                "size": size,
                "limit": max_cache_size
            }
        )

    def drop(self):
        self.interval.drop()

def main():
    global \
        watch_dir, \
        large_layer_size, \
        max_cache_size, \
        time_window, \
        max_time_window_growth_size, \
        log_file_accessing_err

    default_config_path = sys.argv[1] if len(sys.argv) > 1 else "default.conf"

    # init configs
    watch_dir = "."
    large_layer_size = 1073741824  # 1GB
    max_cache_size = 536870912000  # 500GB
    time_window = 10  # 10 secs
    max_time_window_growth_size = 53687091200  # 50GB
    log_file_accessing_err = True

    if os.path.isfile(default_config_path):
        logger.info(
            f"read config from {os.path.abspath(default_config_path)!r}"
        )

        cfg = dotenv_values(default_config_path)

        watch_dir = str(cfg["watch_dir"])
        large_layer_size = int(cfg["large_layer_size"])
        max_cache_size = int(cfg["max_cache_size"])
        time_window = int(cfg["time_window"])
        max_time_window_growth_size = int(cfg["max_time_window_growth_size"])
        log_file_accessing_err = True if str(cfg["log_file_accessing_err"]) == "True" else False
    else:
        logger.info("cannot find the config file, use default config instead")

    logger.info(f"start watching directory {os.path.abspath(watch_dir)!r}")
    logger.info(f"with `large_layer_size` set to {large_layer_size:,} bytes")
    logger.info(f"with `max_cache_size` set to {max_cache_size:,} bytes")
    logger.info(f"with `time_window` set to {time_window:,} secs")
    logger.info(" ".join([
        "with `max_time_window_growth_size` set to",
        f"{max_time_window_growth_size:,} bytes"
    ]))

    # init watcher
    handler = ChangeEventHandler(time_window)

    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        handler.drop()
    finally:
        observer.join()


if __name__ == "__main__":
    main()
