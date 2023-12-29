---
icon: joystick
---

# Earthly Simulator

## Overview

The following document provides an overview and usage guide for the Earthly Simulator.
It is used to simulate the execution of Earthly targets.
This tool allows users to run multiple Earthly targets concurrently and preview the outcomes.

The simulator executes targets concurrently using goroutines, providing a faster simulation experience.
Additionally, the simulator captures and displays both standard output and standard error of each Earthly target's execution.

## SimulateCmd Struct

The simulateCmd struct is designed to be used with a command-line interface (CLI) and has the following fields:

* `Path`: Specifies the directory path to be iterated to search for targets within the Earthfile.
* `Target`: A list of Earthly target patterns that the simulation will run.
  This is specified as a command-line argument.

## Usage

The `simulate` command is written in Go, which located in
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

### Running the simulate command

In the `cli` directory, the following command can be run

``` bash
go run ./cmd/main.go simulate <path>
```

### Build a binary file

``` bash
go build -o bin/ci cmd/main.go
```

Now the `ci` command can be run directly without Go command

### Default targets workflow

If the target flag is not set, the default target patterns will be used.
The defaults value include `check check-* build test test-*`.

``` bash
ci simulate .
```

### Customize targets workflow

Specific stages can be simulated by adding target flag.
The argument is a list of target pattern, for example, `-t <target> <target2>`

``` bash
ci simulate . -t "test test-*"
```
