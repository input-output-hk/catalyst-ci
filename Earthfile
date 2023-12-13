# Set the Earthly version to 0.7
VERSION --global-cache 0.7

# cspell: words livedocs sitedocs

# check-markdown can be done remotely.
check-markdown: 
    DO ./earthly/mdlint+CHECK

# markdown-check-fix perform markdown check with fix in this repo.
markdown-check-fix:
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix

# check-spelling Check spelling in this repo inside a container.
check-spelling:
    DO ./earthly/cspell+CHECK

## -----------------------------------------------------------------------------
##
## Standard CI targets.
##
## These targets are discovered and executed automatically by CI.

# check run all checks.
check:
    BUILD +check-spelling
    BUILD +check-markdown

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

    SAVE ARTIFACT /repo repo

repo-config:
    # Create artifacts of config file we need to refer to in builders.
    FROM scratch

    WORKDIR /repo
    COPY --dir .sqlfluff .

    SAVE ARTIFACT /repo repo