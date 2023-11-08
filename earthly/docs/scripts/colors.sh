#!/bin/bash

# shellcheck disable=SC2034 # This file is intended to bo sourced.

BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color


status() {
    local rc="$1"
    local message="$2"
    shift 2

    # Check if the command returned a bad status
    if "$@"; then
        # Append green OK to the message
        echo -e "${CYAN}${message} : ${GREEN}[OK]${NC}"
    else
        # Append red ERROR to the message
        echo -e "${CYAN}${message} : ${RED}[ERROR]${NC}"
        rc=1
    fi

    # Return the current status
    return "$rc"
}
