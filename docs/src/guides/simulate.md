---
icon: material/gamepad-variant
---

# Earthly Simulator

## Overview

The following document provides an overview and usage guide for simulating Earthly locally.

The simulation can be done in 2 ways

1. Running a command line `simulate`.
This will run Earthly command on every targets that match the given input targets.
The targets will run sequentially, then preview the outcomes.
1. Running a command line `generate`.
This will create an Earthfile that has a main target called `simulate`.
Inside the main `simulate` target will contains all the targets that match the given input targets.
In order to test it, `earthly +simulate` can be run directly.

## Setup

Both of the commands are written in Go, which located in
[catalyst-ci](https://github.com/input-output-hk/catalyst-ci/cli/cmd/main.go) .

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Make sure that your `GOPATH` is set correctly.
<!-- markdownlint-enable max-one-sentence-per-line -->

To begin, clone the Catalyst CI repository:

``` bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `cli` directory.
The command can be found in `cli/cmd/main.go`

### Running the command

In the `cli` directory, the following command can be run

``` bash
go run ./cmd/main.go <command> <path> <flag>
```

### Build a binary file

Instead of running the command directly from `main.go`,
building binary file can be done instead.

``` bash
go build -o bin/ci cmd/main.go
```

Now the `ci` command can be run directly without Go command

## Simulate Command Usage

### SimulateCmd Struct

The simulateCmd struct is designed to be used with a command-line interface (CLI) and has the following fields:

* `Path`: Specifies the directory path to be iterated to search for targets within the Earthfile.
* `Target`: A list of Earthly target patterns that the simulation will run.
If the flag is not set, the default pipeline will be run `check check-* build test test-*`

### Default targets workflow

If the target flag is not set, the default target patterns will be used.
The defaults value include `check check-* build test test-*`.

``` bash
ci simulate .
```

### Customize targets workflow

Specific stages can be simulated by adding target flag.
The argument is a list of target pattern, for example, `-t "<target> <target2>"`

``` bash
ci simulate . -t "test" -t "test-*"
```

## Generate Command Usage

### GenerateCmd Struct

The generateCmd struct is designed to be used with a command-line interface (CLI) and has the following fields:

* `Path`: Specifies the directory path to be iterated to search for targets within the Earthfile.
* `Target`: A list of Earthly target patterns that the simulation will run.
If the flag is not set, the default pipeline will be run `check check-* build test test-*`
* `Version`: An Earthly version that need to be specify at the top of Earthfile.
The default version is 0.7
* `Directory`: A directory where the Earthfile will be place in.
The default directory is `generate/`

### Default value

If the target flag is not set, the default target patterns will be used.
The defaults value include `check check-* build test test-*`.

``` bash
ci generate .
```

The ci will create an Earthfile in `generate/` folder of the current directory.
The version of the Earthly will be set to 0.7
The targets will be listed under the `simulate` target.
eg. `BUILD /User/work/test/+target`

### Customize targets workflow

Customization can be done by specifying flags.

* Adding target flag `-t "<target>" -t "<target2>"`
* Adding version flag `-v <version>`
* Adding directory flag `-d <directory>`

``` bash
ci generate . -t "test-*" -t "check-*" -v 0.6 -d ../
```

The command above will iterate through the current directory.
Find the target that match `test-*` and `check-*`.
Set the version of Earthly to 0.6.
Then create Earthfile to the `../` directory.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Warning
    Make sure that the directory of the Earthfile is not conflict with the existing Earthfile.
    The Earthfile should be ignore in the `.gitignore`

<!-- markdownlint-enable max-one-sentence-per-line -->