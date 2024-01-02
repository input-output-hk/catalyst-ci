#!/usr/bin/env bash

debug_sleep() {
    if [[ -n "${DEBUG_SLEEP:-}" ]]; then
        echo "DEBUG_SLEEP is set. Sleeping for ${DEBUG_SLEEP} seconds..."
        sleep "${DEBUG_SLEEP}"
    fi
}
