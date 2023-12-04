# Set the Earthly version to 0.7
VERSION 0.7
FROM debian:stable-slim

# cspell: words livedocs sitedocs

# Check Markdown in this repo.
markdown-check:
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD})

# Check Markdown remotely.
check-markdown: 
    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD})

# Check Markdown with fix argument in this repo.
markdown-check-fix:
    LOCALLY

    DO ./earthly/mdlint+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix

spell-check:
    # Check spelling in this repo.
    LOCALLY

    DO ./earthly/cspell+CSPELL_LOCALLY --src=$(echo ${PWD})

check:
    BUILD +check-markdown

repo-docs:
    # Create artifacts of extra files we embed inside the documentation when its built.
    FROM scratch
    #FROM alpine:3.18

    WORKDIR /repo
    COPY --dir *.md LICENSE-APACHE LICENSE-MIT .
    #RUN ls -al /repo

    SAVE ARTIFACT /repo repo