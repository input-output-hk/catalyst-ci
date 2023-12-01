# Set the Earthly version to 0.7
VERSION 0.7
FROM debian:stable-slim

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

# Check all source and documentation files.
check-spelling:
    FROM ghcr.io/streetsidesoftware/cspell:8.0.0
    # Use the existing directory from the image itself containing `cspell` binary.
    WORKDIR /app

    COPY . .
    RUN npx cspell lint . --dot

check:
    BUILD +check-spelling

repo-docs:
    # Create artifacts of extra files we embed inside the documentation when its built.
    FROM scratch
    #FROM alpine:3.18

    WORKDIR /repo
    COPY --dir *.md LICENSE-APACHE LICENSE-MIT .
    #RUN ls -al /repo

    SAVE ARTIFACT /repo repo