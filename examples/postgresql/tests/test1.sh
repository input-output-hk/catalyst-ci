#!/usr/bin/env bash

source "/scripts/include/colors.sh"
source "/scripts/include/assert.sh"
source "/scripts/include/db_ops.sh"

# Wait until the server is running
status_and_exit "DB Ready" \
    wait_ready_pgsql "$@" --dbreadytimeout="10"

rc=0
res=$(psql postgresql://example-dev:example-pass@0.0.0.0:5432/ExampleDb -c "SELECT * FROM users")
rc=$?

if [[ ${rc} -eq 0 ]]; then
    expected=$(printf "%s\n%s\n%s\n%s\n%s\n%s\n" \
        "  name   | age " \
        "---------+-----" \
        " Alice   |  20" \
        " Bob     |  30" \
        " Charlie |  40" \
        "(3 rows)")
    assert_eq "${expected}" "${res}"
fi

exit "${rc}"
