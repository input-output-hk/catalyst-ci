VERSION 0.8

IMPORT ./earthly/mdlint AS mdlint-ci
IMPORT ./earthly/cspell AS cspell-ci
IMPORT ./earthly/bash AS bash-ci
IMPORT ./earthly/spectral AS spectral-ci

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
    FROM debian:stable-slim
    DO cspell-ci+CLEAN

# check-spelling Check spelling in this repo inside a container.
check-spelling:
    DO cspell-ci+CHECK

# check-bash - test all bash files lint properly according to shellcheck.
check-bash:
    FROM alpine:3.20.3

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

    SAVE ARTIFACT /repo repo

# edit-docs - Target to assist in editing docs.
edit-docs:
    LOCALLY

    RUN ./earthly/docs/dev/local.py cat-ci-docs:latest

# check-lint-openapi - OpenAPI linting from a given directory
check-lint-openapi:
    FROM spectral-ci+spectral-base
    DO spectral-ci+BUILD_SPECTRAL --dir="./examples/openapi"