#!/usr/bin/env bash

# This script is not intended to be run by itself, and provides common functions
# for database operations.

# shellcheck disable=SC2120 
function init_db() {
    # Start PostgreSQL in the background
    # $1 = Path to the DB data directory (optional)
    local data_dir="${1:-/var/lib/postgresql/data}"
    # $2 = Auth Method (Optional) = trust | md5 | scram-sha-256 | password | any other valid auth method
    local trust_method="${POSTGRES_HOST_AUTH_METHOD:-${2:-trust}}"

    echo "POSTGRES_HOST_AUTH_METHOD is set to ${trust_method}"

    if ! initdb -D "${data_dir}" --locale-provider=icu --icu-locale=en_US; then
        return 1
    fi

    printf "\n host all all all %s \n" "${trust_method}" >> /var/lib/postgresql/data/pg_hba.conf

    return 0
}

function run_pgsql() {
    # Function to start PostgreSQL, and wait for it to start
    # $1 = Path to the DB data directory (optional)
    local data_dir="${1:-/var/lib/postgresql/data}"
    # $2 = timeout to wait in seconds.
    local timeout="${2:-0}"

    if ! pg_ctl -D /tmp/data start; then
        return 1
    fi

    # Check if PostgreSQL is running using pg_isready
    echo "Waiting $((timeout == 0 ? "Forever" : timeout)) for PostgreSQL to start..."
    until pg_isready -d postgres >/dev/null 2>&1; do
        sleep 1
        if [[ ${timeout} -gt 0 ]]; then
            timeout=$((timeout - 1))
            if [[ ${timeout} -eq 0 ]]; then
                echo "Timeout: PostgreSQL server did not start within the specified time"
                return 1
            fi
        fi
    done

    echo "PostgreSQL is running"

    return 0
}

function stop_pgsql() {
    pg_ctl -D /tmp/data stop

    return $?
}

# Custom function to run your desired SQL commands using psql
function setup_db() {
    local setup_db_sql="${1:-./setup-db.sql}"
    local dbname="${DB_NAME:-${2:?}}"
    local dbdesc="${DB_DESCRIPTION:-${3:?}}"
    local dbuser="${DB_USER:-${4:?}}"
    local dbuserpw="${DB_USER_PASSWORD:-${5:?}}"

    psql -d postgres -f "${setup_db_sql}" \
        -v dbName="${dbname}" \
        -v dbDescription="${dbdesc}" \
        -v dbUser="${dbuser}" \
        -v dbUserPw="${dbuserpw}"

    return $?
}

function migrate_schema() {
    local dbname="${DB_NAME:-${1:?}}"
    local dbhost="${DB_HOST:-${2:?}}"
    local dbport="${DB_PORT:-${3:?}}"
    local dbuser="${DB_USER:-${4:?}}"
    local dbuserpw="${DB_USER_PASSWORD:-${5:?}}"

    export DATABASE_URL="postgres://${dbuser}:${dbuserpw}@${dbhost}:${dbport}/${dbname}"
    refinery migrate -e DATABASE_URL -c ./refinery.toml -p ./migrations
}
