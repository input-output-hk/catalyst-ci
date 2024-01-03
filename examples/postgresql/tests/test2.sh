#!/usr/bin/env bash

# cspell: words pgsql dbreadytimeout dbconn psql

source "/scripts/include/colors.sh"
source "/scripts/include/assert.sh"
source "/scripts/include/db_ops.sh"

show_db_config

# Wait for the DB Server to start up and migrate.
sleep 10

# Wait until the server is running
status_and_exit "DB Ready" \
    wait_ready_pgsql "$@" --dbreadytimeout="30"

dbconn=$(pgsql_user_connection "$@")

rc=1
if ! res=$(psql "${dbconn}" -c "SELECT * FROM users" 2>&1); then
    rc=0
fi

if [[ ${rc} -eq 0 ]]; then
    expected=$(printf "%s\n%s\n%s\n" \
        "ERROR:  relation \"users\" does not exist" \
        "LINE 1: SELECT * FROM users" \
        "                      ^")

    status "${rc}" "Query Result" \
        assert_eq "${expected}" "${res}"
    rc=$?
fi

status 0 "DB Query with No Migrations in DB: SELECT * FROM users" \
    [ "${rc}" == 0 ]

exit "${rc}"
