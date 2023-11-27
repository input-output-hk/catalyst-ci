# Set the Earthly version to 0.7
VERSION 0.7

# cspell: words livedocs sitedocs

markdown-check:
    # Check Markdown in this repo.
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD})

markdown-check-fix:
    # Check Markdown in this repo.
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix

spell-check:
    # Check spelling in this repo.
    LOCALLY

    DO ./earthly/cspell+CSPELL_LOCALLY --src=$(echo ${PWD})

# Internal: shell-check - test all bash files lint properly according to shellcheck.
shell-check:
    FROM alpine:3.18

    DO ./earthly/bash+SHELLCHECK --src=.

# check all repo wide checks are run from here
check:
    FROM alpine:3.18

    # Lint all bash files.
    BUILD +shell-check

# Internal: Reference to our repo root documentation used by docs builder.
repo-docs:
    # Create artifacts of extra files we embed inside the documentation when its built.
    FROM scratch
    #FROM alpine:3.18

    WORKDIR /repo
    COPY --dir *.md LICENSE-APACHE LICENSE-MIT .
    #RUN ls -al /repo

    SAVE ARTIFACT /repo repo