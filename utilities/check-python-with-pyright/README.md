# Check Python with Pyright

Usage:

Just run `uv run main.py <directory>`.

All python files will be linted with pyright.
The standard `pyrightconfig.json` needs to be in the root of the project.

IF a python directory is not ready for linting with `pyright` add a non empty `.skip_pyright` file beside the python files.
This will cause those files to be skipped in CI (but not when editing code in VSCode for example).
