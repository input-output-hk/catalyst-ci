# Set the Earthly version to 0.7
VERSION 0.7
FROM debian:stable-slim

# cspell: words livedocs sitedocs

# Check Markdown in this repo.
markdown-check:
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD})

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

repo-docs:
    # Create artifacts of extra files we embed inside the documentation when its built.
    FROM scratch
    #FROM alpine:3.18

    WORKDIR /repo
    COPY --dir *.md LICENSE-APACHE LICENSE-MIT .
    #RUN ls -al /repo

    SAVE ARTIFACT /repo repo