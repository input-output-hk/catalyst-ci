# use with https://github.com/casey/just
#
# Developer convenience functions

default:
    @just --list --unsorted

# Fix and Check Markdown files
check-markdown:
    earthly +markdown-check-fix

# Check Spelling
check-spelling:
    earthly +clean-spelling-list
    earthly +check-spelling

# Fix and Check Code Format for Python files
format-python-code:
    ruff check --select I --fix .
    ruff format .

# Fix and Check Lint for Python files
lint-python: format-python-code
    ruff check --fix .
    ruff check .

# Pre Push Checks - intended to be run by a git pre-push hook.
pre-push: check-markdown check-spelling format-python-code lint-python

# Preview docs locally
preview-docs:
    earthly/docs/dev/local.py cat-ci-docs:latest