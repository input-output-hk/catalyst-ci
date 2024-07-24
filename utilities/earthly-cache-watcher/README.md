<!-- cspell: words loguru inotify journalctl -->

# Earthly Cache Watcher

Logs an error when cache layers reach their maximum size limit.

## Functionality

* Watch files changes in a specified directory.
* Trigger events when either an individual file or
a watched directory grows beyond certain criteria.
* Main triggering criteria: single file size exceeds, watched directory size exceeds,
watched directory growth in size within an interval exceeds.

## Configuration Parameters

There are several options of configurable parameters:

* `watch_dir` - A directory to watch recursively. (default: `.`)
* `large_layer_size` - A parameter to determine and detect an individual file
if reaches the criteria of a large-sized file. (default: `1073741824` bytes)
* `max_cache_size` - A parameter to determine `watch_dir`
if reaches the criteria. (default: `536870912000` bytes)
* `time_window` - The duration of time interval to detect growth
in size of `watch_dir`. (default: `10` secs)
* `max_time_window_growth_size` - A criteria to determine within an interval to detect
if `watch_dir` exceeds the size criteria. (default: `53687091200`)

Typically, these configuration will be read from the specified file.

## System Setup

If the system has many files to watch, you should consider to config this parameter
with `sysctl` to raise the maximum numbers of files to watch:

```bash
sudo sysctl fs.inotify.max_user_watches=25000000
echo 'fs.inotify.max_user_watches=25000000' | sudo tee -a /etc/sysctl.conf
```

Feel free to change the number of the parameter to fit your requirement.

## Systemd Unit Installation

Run the following commands to install the program as a unit in systemd service:

```bash
systemctl daemon-reload
systemctl enable /path/to/your/watchdog.service
systemctl start watchdog
```

To view the status and logs, use these two commands:

```bash
systemctl status watchdog
```

Or

```bash
journalctl -xeu watchdog.service
```

## Logging Example

Logging example using `loguru`:

```json
{
  "text": "read config from '/root/catalyst-ci/utilities/earthly-cache-watcher/default.conf'\n",
  "record": {
    "elapsed": {
      "repr": "0:00:00.007240",
      "seconds": 0.00724
    },
    "exception": null,
    "extra": {},
    "file": {
      "name": "main.py",
      "path": "/root/catalyst-ci/utilities/earthly-cache-watcher/main.py"
    },
    "function": "main",
    "level": {
      "icon": "ℹ️",
      "name": "INFO",
      "no": 20
    },
    "line": 298,
    "message": "read config from '/root/catalyst-ci/utilities/earthly-cache-watcher/default.conf'",
    "module": "main",
    "name": "__main__",
    "process": {
      "id": 59917,
      "name": "MainProcess"
    },
    "thread": {
      "id": 8615431168,
      "name": "MainThread"
    },
    "time": {
      "repr": "2024-07-04 19:22:31.458044+07:00",
      "timestamp": 1720095751.458044
    }
  }
}
```

Notes: The logging result is prettified, the actual result is a single-lined message.
