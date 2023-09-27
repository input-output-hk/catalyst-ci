# Python Earthly Build Containers and UDCs

This repo defines common python targets and UDCs for use with python.

## User Defined Commands

### POETRY_SETUP

This UDC setus up a python based container that uses poetry for dependency management.
Once the UDC has run, the Earthly target that invoked it will

#### Invocation

In an `Earthfile` in your source repository add:

```Earthfile
example_python_target:
    FROM python:3.11-bullseye
    DO github.com/input-output-hk/catalyst-ci:v1.2.0/earthly/python+POETRY_SETUP
```

You may also pass optional arguments:

* `extra_files`: Defining extra files into the `/poetry` directory in the container.
* `opts`: Options to the `poetry install` command.

These arguments are optional and neither is required to be set.

The directory that contains the Earthfile that invokes this UDC MUST have:

* `pyproject.toml` : Definitions of the project to be installed with Poetry.
* `poetry.lock` : Dependency lock file.
  Up-to-date by running:
  * `poetry lock --no-update` : Update lock file, but do not update dependencies; or
  * `poetry lock` : Update lock file and dependencies as required.
