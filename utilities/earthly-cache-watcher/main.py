import sys
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ChangeEventHandler(FileSystemEventHandler):
    """Handles file system events."""

    def __init__(self):
        self.file_indexes = {}

        self.list_initial_sizes()

    def list_initial_sizes(self):
        """Lists initial file sizes during initialization."""

        for root, directories, files in os.walk(watch_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
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
            print(f"New file created: {event.src_path}")
        elif event.event_type == 'modified':
            print(f"File modified: {event.src_path}")
        elif event.event_type == 'deleted':
            print(f"File deleted: {event.src_path}")

def main():
    global watch_dir
    watch_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    logging.info(f'start watching directory {watch_dir!r}')

    observer = Observer()
    observer.schedule(ChangeEventHandler(), watch_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()

if __name__ == "__main__":
    main()