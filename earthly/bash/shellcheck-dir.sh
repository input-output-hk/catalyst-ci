#!/usr/bin/env bash
# Run `shellcheck` on all files in a directory, recursively.
# $1 = The directory to check.

# Get our includes relative to this file's location.
source "$(dirname "$0")/include/colors.sh"

shopt -s globstar
rc=0
for file in "$1"/**/*.sh; do
    path=$(dirname "${file}")
    filename=$(basename "${file}")
    pushd "${path}" > /dev/null || return 1
    status "${rc}" "Checking Bash Lint of '${file}'" \
        shellcheck --check-sourced --external-sources --color=always --enable=all "${filename}"
    popd > /dev/null || return 1

    rc=$?
done

exit "${rc}"
