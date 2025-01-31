# use with https://github.com/casey/just
#

# cspell: words prereqs, commitlog

default:
    @just --list --unsorted


# Fix and Check Markdown files
check-markdown:
    earthly +markdown-check-fix

# Check Spelling
check-spelling:
    earthly +clean-spelling-list
    earthly +check-spelling


# Fix and Check Markdown files
format-python-code:
    ruff check --select I --fix .
    ruff format .

# Fix and Check Markdown files
lint-python:
    ruff check .

# Pre Push Checks - intended to be run by a git pre-push hook.
pre-push: check-markdown check-spelling format-python-code lint-python
