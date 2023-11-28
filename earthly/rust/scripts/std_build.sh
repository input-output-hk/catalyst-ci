#!/usr/bin/env bash

# cspell: words testci testdocs

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

# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.

rc=0

## Build the code
status "${rc}" "Building all code in the workspace" \
    cargo build --release --workspace --locked
rc=$?

## Check the code passes all clippy lint checks.
status "${rc}" "Checking all Clippy Lints in the workspace" \
    cargo lint
rc=$?

## Check we can generate all the documentation
status "${rc}" "Checking Documentation can be generated OK" \
    cargo docs
rc=$?

## Check if all Self contained tests pass (Test that need no external resources).
status "${rc}" "Checking Self contained Unit tests all pass" \
    cargo testci
rc=$?

## Check if all documentation tests pass.
status "${rc}" "Checking Documentation tests all pass" \
    cargo testdocs
rc=$?

ls -al "${basedir}"
ls -al "${basedir}/include"
ls -al .
ls -al ./include

## Check if any benchmarks defined run (We don;t validate the results.)
status "${rc}" "Checking Benchmarks all run to completion" \
    cargo bench --all-targets
rc=$?

## Generate Module Trees for documentation purposes.
# cargo modules generate tree --orphans --types --traits --fns --tests --all-features --lib
# cargo modules generate tree --orphans --types --traits --fns --tests --all-features --bin <name>

## Generate Module Graphs for documentation purposes.
#  cargo modules generate graph --all-features --types --traits --fns --modules --uses --externs --acyclic --lib
#  cargo modules generate graph --all-features --types --traits --fns --modules --uses --externs --acyclic --bin <name>

# Return an error if any of this fails.
exit "${rc}"
