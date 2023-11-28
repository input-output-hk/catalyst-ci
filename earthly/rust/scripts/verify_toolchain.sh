#!/usr/bin/env bash

if [[ ${BASH_SOURCE[0]} = */* ]]; then
    basedir=${BASH_SOURCE%/*}/
else
    basedir=./
fi

source "${basedir}/include/colors.sh"

default_rust_channel=$1
RUST_VERSION=$2

if [[ "${default_rust_channel}" != "${RUST_VERSION}" ]]; then
    echo -e "${YELLOW}Your Rust Toolchain is set to Version : ${RED}${default_rust_channel}${NC}"
    echo -e "${YELLOW}This Builder requires it to be        : ${GREEN}${RUST_VERSION}${NC}"
    echo -e "${RED}Either use the correct Earthly Rust Builder version from CI, or correct './rust-toolchain.toml' to match.${NC}"
    exit 1; 
fi
