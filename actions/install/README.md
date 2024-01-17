# install

> Installs the Catalyst-CI CLI

This Github Action will install the CLI provided by this repository to the local runner.
After installation, the CLI should be accessible via running `ci` (it will automatically be available via `$PATH`).
The CLI is required by a select few actions in order to perform certain operations.

**NOTE**: This action is included in the [CI setup action](../setup/).

## Usage

```yaml
- name: Install CLI
  uses: input-output-hk/catalyst-ci/actions/install@@feat/udcmigration
  with:
    version: latest  # Or select a specific version
- name: Run CLI
  run: ci --help
```

## Inputs

| Name    | Description                                               | Required | Default               |
| ------- | --------------------------------------------------------- | -------- | --------------------- |
| token   | Github token used to query API for available CLI releases | No       | `${{ github.token }}` |
| version | The version of the Catalyst-CI CLI to install             | No       | `latest`              |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
