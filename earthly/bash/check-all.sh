#!/usr/bin/env bash
# Run `shellcheck` on all files in a directory, recursively.
# $1 = The directory to check.

basedir=$(dirname "$0")
# Get our includes relative to this file's location.
source "${basedir}/include/colors.sh"

echo BASEDIR = "${basedir}"

rc=0

"${basedir}"/duplicated-scripts.sh "$1"
rc_dup=$?

"${basedir}"/shellcheck-dir.sh "$1"
rc_lint=$?

# Return an error if any of this fails.
status "${rc}" "Duplicated Bash Scripts" \
    [ "${rc_dup}" == 0 ]
rc=$?
status "${rc}" "Lint Errors in Bash Scripts" \
    [ "${rc_lint}" == 0 ]
rc=$?

exit "${rc}"