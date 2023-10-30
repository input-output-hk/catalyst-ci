#!/usr/bin/env bash

# cspell: words REINIT PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE

# ---------------------------------------------------------------
# Entrypoint script for database container
# ---------------------------------------------------------------
#
# This script serves as the entrypoint for the general database container. It sets up
# the environment, performing optional database initialization if configured,
# and then runs the migrations.
#
# It expects the following environment variables to be set except where noted:
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
set +x
set -o errexit
set -o pipefail
set -o nounset
set -o functrace
set -o errtrace
set -o monitor
set -o posix
shopt -s dotglob

check_env_vars() {
    local env_vars=("$@")

    # Iterate over the array and check if each variable is set
    for var in "${env_vars[@]}"; do
        echo "Checking $var"
        if [ -z "${!var:-}" ]; then
            echo ">>> Error: $var is required and not set."
            exit 1
        fi
    done
}

debug_sleep() {
    if [ -n "${DEBUG_SLEEP:-}" ]; then
        echo "DEBUG_SLEEP is set. Sleeping for ${DEBUG_SLEEP} seconds..."
        sleep "${DEBUG_SLEEP}"
    fi
}

echo ">>> Starting entrypoint script..."

# Check if all required environment variables are set
REQUIRED_ENV=(
    "DB_HOST"
    "DB_PORT"
    "DB_NAME"
    "DB_DESCRIPTION"
    "DB_SUPERUSER"
    "DB_SUPERUSER_PASSWORD"
    "DB_USER"
    "DB_USER_PASSWORD"
)
check_env_vars "${REQUIRED_ENV[@]}"

# Export environment variables
export PGHOST="${DB_HOST}"
export PGPORT="${DB_PORT}"
export PGUSER="${DB_SUPERUSER}"
export PGPASSWORD="${DB_SUPERUSER_PASSWORD}"
export PGDATABASE="${DB_NAME}"

: "${ADMIN_FIRST_NAME:='Admin'}"
: "${ADMIN_LAST_NAME:='Default'}"
: "${ADMIN_ABOUT:='Default Admin User'}"
: "${ADMIN_EMAIL:='admin.default@projectcatalyst.io'}"

# Sleep if DEBUG_SLEEP is set
debug_sleep

# Set the timeout value in seconds (default: 0 = wait forever)
TIMEOUT=${TIMEOUT:-0}
echo "TIMEOUT is set to ${TIMEOUT}"

# Start PostgreSQL in the background
initdb -D /var/lib/postgresql/data || true
pg_ctl -D /var/lib/postgresql/data start &

# Check if PostgreSQL is running using psql
echo "Waiting for PostgreSQL to start..."
until pg_isready -h $DB_HOST -p $DB_PORT -d postgres >/dev/null 2>&1; do
    sleep 1
    if [ $TIMEOUT -gt 0 ]; then
        TIMEOUT=$((TIMEOUT - 1))
        if [ $TIMEOUT -eq 0 ]; then
            echo "Timeout: PostgreSQL server did not start within the specified time"
            exit 1
        fi
    fi
done
echo "PostgreSQL is running"

# Initialize database if necessary
echo ">>> Initializing database..."
psql -h $DB_HOST -p $DB_PORT -d postgres -f ./setup-db.sql \
    -v dbName="${DB_NAME}" \
    -v dbDescription="${DB_DESCRIPTION}" \
    -v dbUser="${DB_USER}" \
    -v dbUserPw="${DB_USER_PASSWORD}"

# Run migrations
echo ">>> Running migrations..."
export DATABASE_URL="postgres://${DB_USER}:${DB_USER_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
refinery migrate -e DATABASE_URL -c ./refinery.toml -p ./migrations

echo ">>> Applying data..."
while IFS= read -r -d '' file; do
    echo "Applying data from $file"
    psql -f "$file"
done < <(find ./data -name '*.sql' -print0 | sort -z)

echo ">>> Finished entrypoint script"
