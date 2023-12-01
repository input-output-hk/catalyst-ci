#!/usr/bin/env bash

# cspell: words dbname dbdesc dbpath pgsql dbreadytimeout

# This script is run inside the `build` stage.
# It validates that all the migrations and importable data are able to be
# used without error.

source "/scripts/include/colors.sh"
source "/scripts/include/db_ops.sh"

setup_and_migrate() {
    local reason="$1"
    shift 1

    # Setup the base db namespace
    status_and_exit "${reason}: DB Setup" \
        setup_db ./setup-db.sql "$@" --dbname=test --dbdesc="Test DB"

    # Run all migrations
    status_and_exit "${reason}: DB Migrate" \
        migrate_schema "$@" --dbname=test
}

# Init the db data in a tmp place
status_and_exit "DB Initial Setup" \
    init_db "$@" --dbpath="/tmp/data"

# Start the db server
status_and_exit "DB Start" \
    run_pgsql "$@" --dbpath="/tmp/data"

# Wait for the DB server to actually start
status_and_exit "DB Ready" \
    wait_ready_pgsql "$@" --dbreadytimeout="10"

# Setup Schema and run migrations.
setup_and_migrate "Initialization" "$@"

# Test each seed data set can apply cleanly
rc=0
while IFS= read -r -d '' file; do
    status "${rc}" "Applying seed data from ${file}" \
        apply_seed_data "${file}" --dbname=test
    rc=$?

    # Reset schema so all seed data get applied to a clean database.
    setup_and_migrate "Reset" "$@"
done < <(find ./seed/* -maxdepth 1 -type d -print0 | sort -z) || true

# Stop the database
status_and_exit "DB Stop" \
    stop_pgsql --dbpath="/tmp/data"


# We DO NOT want the tmp db in the final image, clean it up.
rm -rf /tmp/data

# These tests will immediately fail if the DB is not setup properly.
exit "${rc}"
