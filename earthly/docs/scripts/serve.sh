#!/usr/bin/env bash

# We do not support serving live docs, however this can be used for limited testing purposes.
cd /poetry || exit 1
poetry run mkdocs -v --color serve -f /docs/mkdocs.yml --dev-addr=0.0.0.0:8000
exit $?
