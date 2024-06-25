# cspell: words dotenv levelname

import threading
import os
import time
import logging
from collections.abc import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import dotenv_values

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Interval:
    """
    A class that repeatedly executes a function at specified intervals in a separate thread.
    """

    def __init__(self, interval: int, func: Callable[[], None]):
        """
        Initializes the Interval instance with the specified interval and function.
        """

        self.interval = interval
        self.func = func
        self.stop_event = threading.Event()

        thread = threading.Thread(target=self.set_interval)
        thread.start()

    def set_interval(self):
        """
        Repeatedly executes the function at the specified interval until the stop event is set.
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
        self.time_window_interval: int = interval
        self.growth_indexes: dict[str, int] = {}
        self.file_indexes: dict[str, int] = {}
        self.interval = Interval(interval, self.handle_interval_change)

        self.list_initial_sizes()

    def list_initial_sizes(self):
        """
        Lists initial file sizes during initialization.
        """

        dir_abspath = os.path.abspath(watch_dir)
        for root, directories, files in os.walk(watch_dir):
            for filename in files:
                file_path = os.path.join(dir_abspath, filename)
                try:
                    size = os.path.getsize(file_path)
                    self.file_indexes[file_path] = size

                    # checks individual
                    self.check_sizes(file_path, skip_sum_check=True)

                    logging.debug(f"initial file: {file_path} (size: {size} bytes)")
                except OSError as e:
                    logging.error(f"error accessing file: {file_path} ({e})")

        # checks total
        self.check_sizes(file_path="")

    def on_any_event(self, event):
        """
        Logs any file system event.
        """
        
        if event.is_directory:
            return None
        
        if event.event_type == 'created':
            self.handle_created(event.src_path)
        elif event.event_type == 'modified':
            self.handle_modified(event.src_path)
        elif event.event_type == 'deleted':
            self.handle_deleted(event.src_path)

        logging.debug(event.event_type)

    def handle_interval_change(self):
        logging.debug(f"interval changed")

        self.growth_indexes.clear()

    def handle_created(self, file_path: str):
        logging.debug(f"new file created: {file_path}")

        if not os.path.isfile(file_path):
            return
        
        current_size = os.path.getsize(file_path)
        
        self.file_indexes[file_path] = current_size
        self.growth_indexes[file_path] = current_size

        # checks
        self.check_sizes(file_path)

    def handle_modified(self, file_path: str):
        logging.debug(f"file modified: {file_path}")

        if not os.path.isfile(file_path):
            return

        current_size = os.path.getsize(file_path)

        if file_path not in self.file_indexes:
            self.file_indexes[file_path] = current_size

            logging.debug(f"new file created: {file_path}")
        elif current_size != self.file_indexes[file_path]:
            prev_size = self.file_indexes[file_path]
            diff_size = current_size - prev_size

            self.file_indexes[file_path] = current_size

            if file_path not in self.growth_indexes:
                self.growth_indexes[file_path] = 0

            self.growth_indexes[file_path] += max(diff_size, 0)

            # checks
            self.check_sizes(file_path)

            logging.debug(f"file modified: {file_path} (size changed from {prev_size} bytes to {current_size} bytes)")
        else:
            logging.debug(f"file modified: {file_path} (size unchanged)")

    def handle_deleted(self, file_path: str):
        logging.debug(f"file deleted: {file_path}")

        if file_path in self.file_indexes:
            del self.file_indexes[file_path]
        if file_path in self.growth_indexes:
            del self.growth_indexes[file_path]

    def check_sizes(self, file_path: str, skip_sum_check = False):
        if file_path in self.file_indexes and self.file_indexes[file_path] >= large_file_size:
            self.trigger_file_size_exceeded(file_path)
        if not skip_sum_check and sum(self.growth_indexes.values()) >= max_time_window_growth_size:
            self.trigger_interval_growth_exceeded(file_path)
        if not skip_sum_check and sum(self.file_indexes.values()) >= max_cache_size:
            self.trigger_max_cache_size()

    def trigger_file_size_exceeded(self, file_path: str):
        logging.warning(f"{file_path} exceeds large file size criteria (size: {self.file_indexes[file_path]} bytes, limit: {large_file_size} bytes)")

    def trigger_interval_growth_exceeded(self):
        logging.warning(f"the total amount of cache growth within {time_window} secs exceeds the limit (size: {sum(self.growth_indexes.values())} bytes, limit: {max_time_window_growth_size} bytes)")

    def trigger_max_cache_size(self):
        logging.warning(f"the total amount of cache exceeds the limit (size: {sum(self.file_indexes.values())} bytes, limit: {max_cache_size} bytes)")

    def drop(self):
        self.interval.drop()

def main():
    global watch_dir, large_file_size, max_cache_size, time_window, max_time_window_growth_size

    cfg = dotenv_values("default.conf")
    watch_dir = str(cfg["watch_dir"])
    large_file_size = int(cfg["large_file_size"])
    max_cache_size = int(cfg["max_cache_size"])
    time_window = int(cfg["time_window"])
    max_time_window_growth_size = int(cfg["max_time_window_growth_size"])
    
    logging.info(f'start watching directory {watch_dir!r}')

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
