VERSION 0.8

IMPORT ./earthly/mdlint AS mdlint-ci
IMPORT ./earthly/cspell AS cspell-ci
IMPORT ./earthly/bash AS bash-ci
IMPORT ./earthly/spectral AS spectral-ci
IMPORT ./earthly/python AS python-ci
IMPORT ./earthly/debian AS debian

ARG --global REGISTRY="harbor.shared-services.projectcatalyst.io/dockerhub/library"

# cspell: words livedocs sitedocs


# check-markdown can be done remotely.
check-markdown:
    DO ./earthly/mdlint+CHECK

# markdown-check-fix perform markdown check with fix in this repo.
markdown-check-fix:
    LOCALLY

    DO mdlint-ci+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix

# Make sure the project dictionary is properly sorted.
clean-spelling-list:
    FROM debian+debian-clean
    DO cspell-ci+CLEAN

# check-spelling Check spelling in this repo inside a container.
check-spelling:
    DO cspell-ci+CHECK

# check-bash - test all bash files lint properly according to shellcheck.
check-bash:
    DO bash-ci+SHELLCHECK --src=.

# Internal: Reference to our repo root documentation used by docs builder.
repo-docs:
    # Create artifacts of extra files we embed inside the documentation when its built.
    FROM scratch

    WORKDIR /repo
    COPY --dir *.md LICENSE-APACHE LICENSE-MIT .

    SAVE ARTIFACT /repo repo

repo-config:
    # Create artifacts of config file we need to refer to in builders.
    FROM scratch

    WORKDIR /repo
    COPY --dir .sqlfluff .
    COPY --dir ruff.toml .

    SAVE ARTIFACT /repo repo

# edit-docs - Target to assist in editing docs.
edit-docs:
    LOCALLY

    RUN ./earthly/docs/dev/local.py cat-ci-docs:latest

# We lint python globally in repos, so that all scripts and programs
# are linted equally.
# Its also fast.
check-python:
    DO python-ci+LINT_PYTHON
