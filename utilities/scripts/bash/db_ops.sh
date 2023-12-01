#!/usr/bin/env bash

# cspell: words dbhost dbport dbuser dbuserpw dbname dbsuperuser dbsuperuserpw dbnamesuperuser dbdescription dbpath
# cspell: words dbauthmethod dbcollation dbreadytimeout setupdbsql dbrefinerytoml dbmigrations dbseeddatasrc
# cspell: words pgsql initdb pwfile dbconn isready dbdesc psql

# This script is not intended to be run by itself, and provides common functions
# for database operations.

source "/scripts/include/colors.sh"
source "/scripts/include/params.sh"

# define all the defaults we could need
declare -A defaults
# shellcheck disable=SC2034 # It really is used
defaults=(
    ["dbhost"]="localhost"
    ["dbport"]="5432"
    ["dbuser"]="postgres"
    ["dbuserpw"]="CHANGE_ME"
    ["dbname"]="postgres"
    ["dbsuperuser"]="admin"
    ["dbsuperuserpw"]="CHANGE_ME"
    ["dbnamesuperuser"]="postgres"
    ["dbdescription"]="PostgreSQL Database"
    ["dbpath"]="/var/lib/postgresql/data"
    ["dbauthmethod"]="trust"
    ["dbcollation"]="en_US.utf8"
    ["dbreadytimeout"]="-1"
    ["setupdbsql"]="/sql/setup-db.sql"
    ["dbrefinerytoml"]="./refinery.toml"
    ["dbmigrations"]="./migrations"
    ["dbseeddatasrc"]="./seed"
    ["init_and_drop_db"]=true
    ["with_migrations"]=true
    ["with_seed_data"]=""
)

# Define how parameters map to env vars
declare -A env_vars
# shellcheck disable=SC2034 # It really is used
env_vars=(
    ["dbhost"]="DB_HOST"
    ["dbport"]="DB_PORT"
    ["dbname"]="DB_NAME"
    ["dbdescription"]="DB_DESCRIPTION"
    ["dbuser"]="DB_USER"
    ["dbuserpw"]="DB_USER_PASSWORD"
    ["dbsuperuser"]="DB_SUPERUSER"
    ["dbsuperuserpw"]="DB_SUPERUSER_PASSWORD"
    ["dbnamesuperuser"]="DB_NAME_SUPERUSER"
    ["dbpath"]="DB_PATH"
    ["dbauthmethod"]="DB_AUTH_METHOD"
    ["dbcollation"]="DB_COLLATION"
    ["dbreadytimeout"]="DB_READY_TIMEOUT"
    ["setupdbsql"]="SETUP_DB_SQL"
    ["dbrefinerytoml"]="DB_REFINERY_TOML"
    ["dbmigrations"]="DB_MIGRATIONS"
    ["dbseeddatasrc"]="DB_SEED_DATA_SRC"
    ["init_and_drop_db"]="INIT_AND_DROP_DB"
    ["with_migrations"]="WITH_MIGRATIONS"
    ["with_seed_data"]="WITH_SEED_DATA"
)

function pgsql_user_connection() {
    # shellcheck disable=SC2155 # Can not fail
    local dbname=$(get_param dbname env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbhost=$(get_param dbhost env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbport=$(get_param dbport env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbuser=$(get_param dbuser env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbuserpw=$(get_param dbuserpw env_vars defaults "$@")

    echo "postgres://${dbuser}:${dbuserpw}@${dbhost}:${dbport}/${dbname}"
}

function pgsql_superuser_connection() {
    # shellcheck disable=SC2155 # Can not fail
    local dbname=$(get_param dbnamesuperuser env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbhost=$(get_param dbhost env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbport=$(get_param dbport env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbsuperuser=$(get_param dbsuperuser env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbsuperuserpw=$(get_param dbsuperuserpw env_vars defaults "$@")

    echo "postgres://${dbsuperuser}:${dbsuperuserpw}@${dbhost}:${dbport}/${dbname}"
}

# Initialize the database
# --dbpath = <Path to the DB data directory (optional)>
# --dbauthmethod = <Auth Method (Optional) = trust | md5 | scram-sha-256 | password | any other valid auth method>
function init_db() {
    # Start PostgreSQL in the background

    # shellcheck disable=SC2155 # Can not fail
    local data_dir=$(get_param dbpath env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local auth_method=$(get_param dbauthmethod env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local super_user=$(get_param dbsuperuser env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local super_user_pw=$(get_param dbsuperuserpw env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local collation=$(get_param dbcollation env_vars defaults "$@")

    echo "data dir: ${data_dir}"
    echo "auth method: ${auth_method}"

    echo "POSTGRES_HOST_AUTH_METHOD is set to ${auth_method}"

    if ! initdb -D "${data_dir}" \
        --locale-provider=icu --icu-locale="${collation}" --locale="${collation}" \
        -A "${auth_method}" \
        -U "${super_user}" --pwfile=<(echo "${super_user_pw}"); then
        return 1
    fi

    echo "include_if_exists ${data_dir}/pg_hba.extra.conf" >>"${data_dir}/pg_hba.conf"
    echo "include_if_exists /sql/pg_hba.extra.conf" >>"${data_dir}/pg_hba.conf"

    return 0
}

# Start PostgreSQL Local database server in the background
# --dbpath = <Path to the DB data directory (optional)>
function run_pgsql() {
    # Function to start the local PostgreSQL server

    # shellcheck disable=SC2155 # Can not fail
    local data_dir=$(get_param dbpath env_vars defaults "$@")

    if ! pg_ctl -D "${data_dir}" start; then
        return 1
    fi

    echo "PostgreSQL is starting"

    return 0
}

# Wait until PostgreSQL is ready to serve requests
# --dbreadytimeout = <Time in seconds to wait before giving up (optional), 0 = Never, -1 = Forever>
function wait_ready_pgsql() {

    # shellcheck disable=SC2155 # Can not fail
    local dbconn=$(pgsql_superuser_connection "$@")

    echo "DB connection: ${dbconn}"

    # shellcheck disable=SC2155 # Can not fail
    local timeout=$(get_param dbreadytimeout env_vars defaults "$@")
    if [[ ${timeout} -lt 0 ]]; then
        delay="Forever"
    elif [[ ${timeout} -eq 0 ]]; then
        delay="Not at all"
    else
        delay="${timeout} seconds"
    fi

    # If there is no wait, then just return.
    echo "Waiting ${delay} for PostgreSQL to start..."
    if [[ ${timeout} -eq 0 ]]; then
        return 0
    fi

    # Check if PostgreSQL is running using pg_isready
    until pg_isready -d "${dbconn}" > /dev/null 2>&1; do
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

# Wait until PostgreSQL is no longer ready to serve requests
# shellcheck disable=SC2120
function wait_pgsql_stopped() {

    # shellcheck disable=SC2155 # Can not fail
    local dbconn=$(pgsql_superuser_connection "$@")

    echo "Waiting for PostgreSQL DB to stop..."

    # Check if PostgreSQL is running using pg_isready
    until ! pg_isready -d "${dbconn}" > /dev/null 2>&1; do
        sleep 60
    done

    return 0
}

# Stop the local PostgreSQL server
function stop_pgsql() {
    # shellcheck disable=SC2155 # Can not fail
    local data_dir=$(get_param dbpath env_vars defaults "$@")

    pg_ctl -D "${data_dir}" stop

    return $?
}

# Setup the default User and Database
# WARNING: Will destroy all data in the DB
function setup_db() {
    # shellcheck disable=SC2155 # Can not fail
    local setup_db_sql=$(get_param setupdbsql env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbname=$(get_param dbname env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbdesc=$(get_param dbdesc env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbuser=$(get_param dbuser env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbuserpw=$(get_param dbuserpw env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local dbconn=$(pgsql_superuser_connection "$@")

    psql -v ON_ERROR_STOP=on \
        -d "${dbconn}" \
        -f "${setup_db_sql}" \
        -v dbName="${dbname}" \
        -v dbDescription="${dbdesc}" \
        -v dbUser="${dbuser}" \
        -v dbUserPw="${dbuserpw}"

    return $?
}

# Run schema migrations
function migrate_schema() {
    # shellcheck disable=SC2155 # Can not fail
    local refinery_toml=$(get_param dbrefinerytoml env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local migrations=$(get_param dbmigrations env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    export DATABASE_URL=$(pgsql_user_connection "$@")

    refinery migrate -e DATABASE_URL -c "${refinery_toml}" -p "${migrations}"
}

function apply_seed_data() {
    local seed_data=$1
    shift 1

    # shellcheck disable=SC2155 # Can not fail
    local dbconn=$(pgsql_user_connection "$@")

    echo "Applying seed data from directory: $1"
    rc=0

    while IFS= read -r -d '' file; do
        echo "    ++++ : ${file}"
        psql -v ON_ERROR_STOP=on -1 -d "${dbconn}" -f "${file}"
        psql_rc=$?
        if [[ ${psql_rc} -ne 0 ]]; then
            echo "Failed to apply seed data from ${file} with exit code ${psql_rc}"
            rc=1
        fi
    done < <(find "${seed_data}" -maxdepth 1 -name '*.sql' -print0 | sort -z) || true

    return "${rc}"
}

# Check if a seed data directory exists, and if it does apply it.
# if one is defined, but it can not be found, that is a fatal error.
# shellcheck disable=SC2120
seed_database() {

    # shellcheck disable=SC2155 # Can not fail
    local seed_data=$(get_param with_seed_data env_vars defaults "$@")
    # shellcheck disable=SC2155 # Can not fail
    local seed_data_dir=$(get_param dbseeddatasrc env_vars defaults "$@")

    rc=0

    if [[ -n "${seed_data}" ]]; then
        local full_path="${seed_data_dir}/${seed_data}"

        if [[ -d "${full_path}" ]]; then
            apply_seed_data "${full_path}"
            rc=$?
        else
            echo "ERROR: Seed Data Directory not found: ${full_path}"
            rc=1
        fi
    fi

    return "${rc}"
}

# Dump all our configuration
# shellcheck disable=SC2120
function show_db_config() {
    local insecure=${1:-false}

    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbhost"]} = $(get_param dbhost env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbport"]} = $(get_param dbport env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbuser"]} = $(get_param dbuser env_vars defaults "$@")"

    if [[ ${insecure} == "true" ]]; then
        # shellcheck disable=SC2155,SC2312 # Can not fail
        echo "${env_vars["dbuserpw"]} = $(get_param dbuserpw env_vars defaults "$@")"
    else
        echo "${env_vars["dbuserpw"]} = XXXX"
    fi

    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbname"]} = $(get_param dbname env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbdescription"]} = $(get_param dbdescription env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbsuperuser"]} = $(get_param dbsuperuser env_vars defaults "$@")"

    if [[ ${insecure} == "true" ]]; then
        # shellcheck disable=SC2155,SC2312 # Can not fail
        echo "${env_vars["dbsuperuserpw"]} = $(get_param dbsuperuserpw env_vars defaults "$@")"
    else
        echo "${env_vars["dbsuperuserpw"]} = XXXX"
    fi

    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbnamesuperuser"]} = $(get_param dbnamesuperuser env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbpath"]} = $(get_param dbpath env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbauthmethod"]} = $(get_param dbauthmethod env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbcollation"]} = $(get_param dbcollation env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbreadytimeout"]} = $(get_param dbreadytimeout env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["setupdbsql"]} = $(get_param setupdbsql env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbrefinerytoml"]} = $(get_param dbrefinerytoml env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbmigrations"]} = $(get_param dbmigrations env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["dbseeddatasrc"]} = $(get_param dbseeddatasrc env_vars defaults "$@")"

    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["init_and_drop_db"]} = $(get_param init_and_drop_db env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["with_migrations"]} = $(get_param with_migrations env_vars defaults "$@")"
    # shellcheck disable=SC2155,SC2312 # Can not fail
    echo "${env_vars["with_seed_data"]} = $(get_param with_seed_data env_vars defaults "$@")"
}
