# Earthly Cache Watcher

## Functionality

* Watch files changes in a specified directory.
* Trigger events when a whether an individual file or
a watched directory grows exceeding the certain criteria.
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
