#!/usr/bin/env bash
# Run `shellcheck` on all files in a directory, recursively.
# $1 = The directory to check.

# Import utility functions - only works inside containers.
source "/scripts/include/colors.sh"

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
