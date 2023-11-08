# Catalyst Documentation Builders and UDCs

This directory contains targets for the Catalyst Documentation builders, and associated UDCs.

## Check

This target includes a check to ensure the MkDocs base builder works as expected.

```bash
earthly -P +check
```

## Updating Dependencies

If a new dependency is added to `pyproject.toml` ensure to run:

```sh
poetry lock
```

in the `earthly/docs` directory to update the locked dependencies.
