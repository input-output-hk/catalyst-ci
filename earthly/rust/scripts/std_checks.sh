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

# This is set up so that ALL checks are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `check`
# to pass without needing to iterate excessively.

# Check if the rust src is properly formatted.
# Note, we run this first so we can print help how to fix.
status 0 "Checking Rust Code Format" cargo +nightly fmtchk; rc=$?
if [[ "${rc}" -ne 0 ]]; then
    echo -e "    ${YELLOW}You can locally fix format errors by running: \`cargo +nightly fmtfix\`${NC}"
fi

## Check if .cargo.config.toml has been modified.
check_vendored_files "${rc}" .cargo/config.toml "${CARGO_HOME:?}"/config.toml; rc=$?
check_vendored_files "${rc}" rustfmt.toml /stdcfgs/rustfmt.toml; rc=$?
check_vendored_files "${rc}" .config/nextest.toml /stdcfgs/nextest.toml; rc=$?
check_vendored_files "${rc}" clippy.toml /stdcfgs/clippy.toml; rc=$?
check_vendored_files "${rc}" deny.toml /stdcfgs/deny.toml; rc=$?

# Check if we have unused dependencies declared in our Cargo.toml files.
status "${rc}" "Checking for Unused Dependencies" cargo machete; rc=$?

# Check if we have any supply chain issues with dependencies.
status "${rc}" "Checking for Supply Chain Issues" cargo deny check; rc=$?

# Return an error if any of this fails.
exit "${rc}"