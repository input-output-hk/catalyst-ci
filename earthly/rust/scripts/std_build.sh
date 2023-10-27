#!/usr/bin/env bash

# This script is run inside the `check` stage for rust projects to perfom all 
# high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `buuild`. 
# Individual targets can add extra `check` steps, but these checks must always
# pass. 

source "$(dirname "$0")/colors.sh"


# This is set up so that ALL build steps are run and it will fail if any fail.
# This imporvies visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.

rc=0

## Build the code
status $rc "Building all code in the workspace" \
    cargo build --release --workspace --locked; rc=$?

## Check the code passes all clippy lint checks.

## Check we can generate all the documentation

## Check if all Self contained tests pass (Test that need no external resources).

## Check if all documentation tests pass.

## Check if any benchmarks defined run (We don;t validate the results.)

## Check if there are any circular dependencies in the project.

## Generate Module Trees for documentation purposes.

## Generate Module Graphs for documentation purposes.

## Save all the artifacts so we can use them.

# Return an error if any of this fails.
exit $rc