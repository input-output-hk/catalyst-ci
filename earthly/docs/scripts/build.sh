#!/usr/bin/env bash

# Builds the documentation to the `/site` directory inside the container.

#!/usr/bin/env bash

source "$(dirname "$0")/include/colors.sh"

rc=0

## Build the code
status "${rc}" "Changing to Poetry Environment Workspace" \
    cd /poetry; rc=$?

## Building the documentation.  
status "${rc}" "Building Documentation" \
    poetry run mkdocs -v --color build --strict --clean -f /docs/mkdocs.yml -d /site; rc=$?

# Return an error if any of this fails.
exit "${rc}"

