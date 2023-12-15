#!/usr/bin/env bash

# cspell: words testunit testdocs RUSTDOCFLAGS Zunstable depgraph

# This script is run inside the `check` stage for rust projects to perform all
# high level non-compilation checks.
# These are the Standard checks which ALL rust targets must pass before they
# will be scheduled to be `build`.
# Individual targets can add extra `check` steps, but these checks must always
# pass.

source "$(dirname "$0")/colors.sh"


# This is set up so that ALL build steps are run and it will fail if any fail.
# This improves visibility into all issues that need to be corrected for `build`
# to pass without needing to iterate excessively.

rc=0

## Build the code
status $rc "Building all code in the workspace" \
    cargo build --release --workspace --locked; rc=$?

## Check the code passes all clippy lint checks.
status $rc "Checking all Clippy Lints in the workspace" \
    cargo lint; rc=$?

## Check we can generate all the documentation
status $rc "Checking Documentation can be generated OK" \
    cargo docs; rc=$?

## Check if all Self contained tests pass (Test that need no external resources).
status $rc "Checking Self contained Unit tests all pass" \
    cargo testunit; rc=$?

## Check if all documentation tests pass.
status $rc "Checking Documentation tests all pass" \
    cargo testdocs; rc=$?

## Check if any benchmarks defined run (We don;t validate the results.)
status $rc "Checking Benchmarks all run to completion" \
    cargo bench --all-targets; rc=$?

## Generate dependency graphs
status $rc "Generating workspace dependency graphs" \
    $(cargo depgraph --workspace-only --dedup-transitive-deps > target/doc/workspace.dot); rc=$?
status $rc "Generating full dependency graphs" \
    $(cargo depgraph --dedup-transitive-deps > target/doc/full.dot); rc=$?
status $rc "Generating all dependency graphs" \
    $(cargo depgraph --all-deps --dedup-transitive-deps > target/doc/all.dot); rc=$?

export NO_COLOR=1
## Generate Module Trees for documentation purposes.
for lib in $1;
do
    status $rc "Generate Module Trees for $lib" \
        $(cargo modules generate tree --orphans --types --traits --tests --all-features \
            --package $lib --lib > target/doc/$lib.lib.modules.tree); rc=$?

    status $rc "Generate Module Graphs for $lib" \
        $(cargo modules generate graph --all-features --modules \
            --package $lib --lib > target/doc/$lib.lib.modules.dot); rc=$?
done
for bin in $2;
do
    IFS="/" read -r package bin <<< "$bin"
    status $rc "Generate Module Trees for $package/$bin" \
        $(cargo modules generate tree --orphans --types --traits --tests --all-features \
            --package $package --bin $bin > target/doc/$package.$bin.bin.modules.tree); rc=$?

    status $rc "Generate Module Graphs for $package/$bin" \
        $(cargo modules generate graph --all-features --modules \
            --package $package --bin $bin > target/doc/$package.$bin.bin.modules.dot); rc=$?
done

# Return an error if any of this fails.
exit $rc