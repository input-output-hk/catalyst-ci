#!/usr/bin/env bash

# This script is run inside the `check` stage for rust projects to perfom all 
# high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `buuild`. 
# Individual targets can add extra `check` steps, but these checks must always
# pass. 

source "$(dirname "$0")/colors.sh"

# Checks if two files that should exist DO, and are equal.
# used to enforce consistency between local config files and the expected config locked in CI.
check_vendored_files() {
    local rc=$1
    local localfile=$2
    local vendorfile=$3

    status "$rc" "Checking if Local File '$localfile' == Vendored File '$vendorfile'" \
        colordiff -Naur "$localfile" "$vendorfile"
    return $?
}

# This is set up so that ALL checks are run and it will fail if any fail.
# This imporvies visibility into all issues that need to be corrected for `check`
# to pass without needing to iterate excessively.

rc=0

## Check if .cargo.config.toml has been modified.
check_vendored_files $rc .cargo/config.toml "$CARGO_HOME"/config.toml; rc=$?
check_vendored_files $rc rustfmt.toml /stdcfgs/rustfmt.toml; rc=$?

# Check if the rust src is properly formatted.
status $rc "Checking Rust Code Format" cargo +nightly fmtchk; rc=$?
if [ $rc -ne 0 ]; then
    echo -e "    ${YELLOW}You can locally fix format errors by running: \`cargo +nightly fmtfix\`${NC}"
fi

# Check if we have unused dependencies declared in our Cargo.toml files.
status $rc "Checking for Unused Dependencies" cargo machete; rc=$?

# Return an error if any of this fails.
exit $rc