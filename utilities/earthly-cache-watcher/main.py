import sys
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
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Interval:
    def __init__(self, interval: int, func: Callable[[], None]):
        self.interval = interval
        self.func = func
        self.stop_event = threading.Event()

        thread = threading.Thread(target=self.set_interval)
        thread.start()

    def set_interval(self):
        nextTime=time.time()+self.interval
        while not self.stop_event.wait(nextTime-time.time()):
            nextTime+=self.interval
            self.func()

    def drop(self):
        self.stop_event.set()

class ChangeEventHandler(FileSystemEventHandler):
    """Handles file system events."""

    def __init__(self, interval: int):
        self.time_window_interval: int = interval
        self.growth_indexes: dict[str, int] = {}
        self.file_indexes: dict[str, int] = {}
        self.interval = Interval(interval, self.handle_interval_change)

        self.list_initial_sizes()

    def list_initial_sizes(self):
        """Lists initial file sizes during initialization."""

        dir_abspath = os.path.abspath(watch_dir)
        for root, directories, files in os.walk(watch_dir):
            for filename in files:
                file_path = os.path.join(dir_abspath, filename)
                try:
                    size = os.path.getsize(file_path)
                    self.file_indexes[file_path] = size
                    print(f"Initial file: {file_path} (size: {size} bytes)")
                except OSError as e:
                    print(f"Error accessing file: {file_path} ({e})")

    def on_any_event(self, event):
        """Logs any file system event."""
        
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            self.handle_created(event.src_path)
        elif event.event_type == 'modified':
            self.handle_modified(event.src_path)
        elif event.event_type == 'deleted':
            self.handle_deleted(event.src_path)

    def handle_interval_change(self):
        print(f"Interval changed")
        self.growth_indexes = {}

    def handle_created(self, file_path: str):
        print(f"New file created: {file_path}")

        self.file_indexes[file_path] = os.path.getsize(file_path)

    def handle_modified(self, file_path: str):
        print(f"File modified: {file_path}")

        current_size = os.path.getsize(file_path)

        if file_path not in self.file_indexes:
            self.file_indexes[file_path] = current_size

            print(f"New file created: {file_path}")
        elif current_size != self.file_indexes[file_path]:
            prev_size = self.file_indexes[file_path]
            diff_size = current_size - prev_size
            self.file_indexes[file_path] = current_size

            print(f"File modified: {file_path} (size changed from {prev_size} bytes to {current_size} bytes)")
        else:
            print(f"File modified: {file_path} (size unchanged)")

    def handle_deleted(self, file_path: str):
        print(f"File deleted: {file_path}")

        del self.file_indexes[file_path]

    def drop(self):
        self.interval.drop()

def main():
    global watch_dir, large_file_size, max_cache_size, time_window, time_window_large_file_growth

    cfg = dotenv_values("config.conf")
    watch_dir = str(cfg["watch_dir"])
    large_file_size = int(cfg["large_file_size"])
    max_cache_size = int(cfg["max_cache_size"])
    time_window = int(cfg["time_window"])
    time_window_large_file_growth = int(cfg["time_window_large_file_growth"])
    
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