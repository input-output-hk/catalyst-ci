#!/usr/bin/env bash
# Run `shellcheck` on all files in a directory, recursively.
# $1 = The directory to check.

# cspell: words FORCECOLOR

# Get our includes relative to this file's location.
source "/scripts/include/colors.sh"

rc=0

./duplicated-scripts.sh "$1"
rc_dup=$?

./shellcheck-dir.sh "$1"
rc_lint=$?

FORCECOLOR=1 shfmt -d "$1"
rc_shfmt=$?

# Return an error if any of this fails.
status "${rc}" "Duplicated Bash Scripts" \
    [ "${rc_dup}" == 0 ]
rc=$?
status "${rc}" "Lint Errors in Bash Scripts" \
    [ "${rc_lint}" == 0 ]
rc=$?
status "${rc}" "ShellFmt Errors in Bash Scripts" \
    [ "${rc_shfmt}" == 0 ]
rc=$?

if [[ ${rc_shfmt} -ne 0 ]]; then
    echo "Shell files can be autoformatted with: 'shfmt -w .' from the root of the repo."
fi

exit "${rc}"
