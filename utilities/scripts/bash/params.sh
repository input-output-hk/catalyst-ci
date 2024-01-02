#!/usr/bin/env bash

# This script is not intended to be run by itself, and provides common functions
# for database operations.

# Check if an env var is set, if so return it,
# if not look for it in a list of parameters and return that,
# and if thats not found return a default
# the default can be an individual value, or a map, in which case the default will
# be retrieved according to the <param_name>
# get_param <param_name> <env_var_map_name> <default_map_name> [--param1=value1 --param2=value2 ...]
get_param() {
    local param_name="$1"
    local env_var_map_name="$2"
    local default_map_name="$3"

    # Access the values of the associative arrays
    local env_var_map
    local default_map
    declare -n env_var_map="${env_var_map_name}"
    declare -n default_map="${default_map_name}"
    shift 3

    # Check if ENV_VAR defined, has priority over options and defaults
    local env_var_name="${env_var_map[${param_name}]:-}"
    if [[ -n "${env_var_name}" ]]; then
        local env_var_value="${!env_var_name}"
        if [[ -n "${env_var_value}" ]]; then
            echo "${env_var_value}"
            return
        fi
    fi

    # Check for the parameter in the named options
    for arg in "$@"; do
        if [[ "${arg}" == "--${param_name}="* ]]; then
            echo "${arg#*=}"
            return
        fi
    done

    # Return the default value
    local default_value="${default_map[${param_name}]:-}"
    echo "${default_value:-}"

    return

}

# Check if a list of env vars have been set.
check_env_vars() {
    # shellcheck disable=SC2190 # This is an array, not an associative array
    local env_vars=("$@")

    # Iterate over the array and check if each variable is set
    for var in "${env_vars[@]}"; do
        echo "Checking ${var}"
        if [[ -z "${!var:-}" ]]; then
            echo ">>> Error: ${var} is required and not set."
            exit 1
        fi
    done
}
