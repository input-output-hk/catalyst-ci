#!/usr/bin/env bash

# cspell: words fmtchk fmtfix rustfmt stdcfgs nextest

# This script is run inside the `check` stage for rust projects to perform all
# high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `build`.
# Individual targets can add extra `check` steps, but these checks must always
# pass.

if [[ ${BASH_SOURCE[0]} = */* ]]; then
    basedir=${BASH_SOURCE%/*}/
else
    basedir=./
fi

source "${basedir}/include/colors.sh"

rc=0

# This is set up so that ALL checks are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `check`
# to pass without needing to iterate excessively.

## Check configs are as they should be.
check_vendored_files "${rc}" .sqlfluff /root/.sqlfluff
rc=$?

# Check sqlfluff linter against sql files.
status "${rc}" "Checking SQLFluff Linter against SQL Files" sqlfluff lint -vv .
rc=$?

# Return an error if any of this fails.
exit "${rc}"
