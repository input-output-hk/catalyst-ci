# configure-runner

> Configures Earthly to use a remote runner

This Github Action will automatically perform the necessary steps to configure the local GitHub runner to connect to a remote
Earthly runner.
It expects a secret to be stored in [AWS Secrets Manager][asm] (see setup section below).
It will automatically pull down TLS certificates, place them into a temporary location on the local runner, and then configure
Earthly to consume them correctly.

**NOTE**: This action is included in the [CI setup action](../setup/).

## Usage

```yaml
- name: Setup Remote Runner
  uses: input-output-hk/catalyst-ci/actions/configure-runner@@feat/udcmigration
  with:
    path: /path/to/store/certs  # Optional, defaults to /tmp/certs
    secret: ${{ secrets.EARTHLY_RUNNER_SECRET }} # The full name of the secret in AWS SM
- name: Run Earthly
  run: earthly --buildkit-host "tcp://my-remote-runner:8372" build+target
```

## Setup

You must already have a [remote runner][rr] created and configured with a set of client certificates that have been signed by the
same CA used for signing the certificates present in AWS SM.
The secret in AWS should have the following format:

```json
{
  "private_key": "-----BEGIN EC PRIVATE KEY-----...",
  "certificate": "-----BEGIN CERTIFICATE-----....",
  "ca_certificate": "-----BEGIN CERTIFICATE-----...."
}
```

Where the full contents of the respective certificates/keys should be included.

## Inputs

| Name   | Description                                         | Required | Default      |
| ------ | --------------------------------------------------- | -------- | ------------ |
| path   | The path to store runner certificates               | No       | `/tmp/certs` |
| secret | The AWS secret to read the runner certificates from | Yes      | `N/A`        |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```

[asm]: https://aws.amazon.com/secrets-manager/
[rr]: https://docs.earthly.dev/docs/remote-runners
