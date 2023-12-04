#!/usr/bin/env bash

# cspell: words REINIT PGHOST PGPORT PGUSER PGPASSWORD psql initdb isready dotglob
# cspell: words dbhost dbdesc dbdescription dbpath pgsql 

# ---------------------------------------------------------------
# Entrypoint script for database container
# ---------------------------------------------------------------
#
# This script serves as the entrypoint for the general database container. It sets up
# the environment, performing optional database initialization if configured,
# and then runs the migrations.
#
# All ENVVARS are optional, although the passwords should be set for security reasons.
#
# DB_HOST - The hostname of the database server
# DB_PORT - The port of the database server
# DB_NAME - The name of the database
# DB_DESCRIPTION - The description of the database
# DB_SUPERUSER - The username of the database superuser
# DB_SUPERUSER_PASSWORD - The password of the database superuser
# DB_USER - The username of the database user
# DB_USER_PASSWORD - The password of the database user
# DEBUG - If set, the script will print debug information (optional)
# DEBUG_SLEEP - If set, the script will sleep for the specified number of seconds (optional)
# STAGE - The stage being run.  Currently only controls if stage specific data is applied to the DB (optional)
# ---------------------------------------------------------------

source "/scripts/include/db_ops.sh"
source "/scripts/include/debug.sh"

set +x
shopt -s dotglob

show_db_config

dbhost=$(get_param dbhost env_vars defaults "$@")
initdb=$(get_param init_and_drop_db env_vars defaults "$@")
migrations=$(get_param with_migrations env_vars defaults "$@")
dbdesc=$(get_param dbdescription env_vars defaults "$@")
dbpath=$(get_param dbpath env_vars defaults "$@")

echo ">>> Starting entrypoint script for DB: ${dbdesc} @ ${dbhost}..."

# Enforce that we must supply passwords as env vars
REQUIRED_ENV=(
    "DB_SUPERUSER_PASSWORD"
    "DB_USER_PASSWORD"
)
check_env_vars "${REQUIRED_ENV[@]}"

# Sleep if DEBUG_SLEEP is set
debug_sleep

# Run postgreSQL database in this container if the host is localhost
if [[ "${dbhost}" == "localhost" ]]; then

    if [[ "${initdb}" == "true" ]]; then
        rm -rf "${dbpath}" 2> /dev/null
        status 0 "Local DB Data Purge" \
            true
    fi

    # Init the db data in a tmp place
    status_and_exit "DB Initial Setup" \
        init_db "$@"

    # Start the db server
    status_and_exit "DB Start" \
        run_pgsql "$@"
fi

# Wait for the DB server to actually start
status_and_exit "Waiting for the DB to be Ready" \
    wait_ready_pgsql "$@"

# Initialize and drop database if necessary
if [[ "${initdb}" == "true" ]]; then
    # Setup the base db namespace
    status_and_exit "Initial DB Setup - Clearing all DB data" \
        setup_db ./setup-db.sql "$@"
fi

# Run migrations
if [[ "${migrations}" == "true" ]]; then
    # Run all migrations
    status_and_exit "Running Latest DB Migrations" \
        migrate_schema "$@"
fi

# Apply seed data
seed_database

if [[ "${dbhost}" == "localhost" ]]; then
    echo ">>> Waiting until the Database terminates: ${dbdesc} @ ${dbhost}..."
    # Infinite loop until the DB stops, because we are serving the DB from this container.
    wait_pgsql_stopped
fi

echo ">>> Finished DB entrypoint script for DB: ${dbdesc} @ ${dbhost}..."
