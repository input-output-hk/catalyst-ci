#!/usr/bin/env bash

# This script is run inside the `build` stage.
# It validates that all the migrations and importable data are able to be
# used without error.

basedir=$(dirname "$0")

source "${basedir}/include/colors.sh"
source "${basedir}/db_ops.sh"

# Init the db data in a tmp place
status_and_exit "DB Initial Setup" \
    init_db /tmp/data

# Start the db server
status_and_exit "DB Start" \
    run_pgsql /tmp/data 10

# Setup the base db namespace
status_and_exit "DB Setup" \
    setup_db ./setup-db.sql test "Test DB" test test

# Run all migrations
status_and_exit "DB Migrate" \
    migrate_schema test localhost 5432 test test

# Stop the database
status_and_exit "DB Stop" \
    stop_pgsql

# We DO NOT want the tmp db in the final image, clean it up.
rm -rf /tmp/data

# These tests will immeditaley fail if the DB is not setup properly.
exit 0