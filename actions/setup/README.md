# setup

> Performs required steps to setup CI

This Github Action will perform common configuration steps required to set up a GitHub runner to interact with actions in this
repository, including:

1. Install Earthly
2. Install the CLI provided by this repository
3. Configure AWS credentials
4. Configure GHCR and ECR registries
5. Configure the GitHub runner to connect to an Earthly remote runner

Most steps can be disabled to limit the amount the action does.

To see a full demonstration of this action, see the [release workflow](../../.github/workflows/release.yml).

## Usage

```yaml
- name: Setup CI
  uses: input-output-hk/catalyst-ci/actions/setup@master
  with:
    aws_ecr_registry: 1234567890.dkr.ecr.us-east-1.amazonaws.com
    aws_role_arn: arn:aws:iam::1234567890:role/github
    aws_region: us-east-1
    cli_version: latest
    configure_registries: "true"
    earthly_version: latest
    earthly_runner_secret: ${{ secrets.EARTHLY_RUNNER_SECRET }}
```

## Inputs

| Name                  | Description                                                        | Required | Default               |
| --------------------- | ------------------------------------------------------------------ | -------- | --------------------- |
| aws_ecr_registry      | The address to the ECR registry that will be configured            | No       | `""`                  |
| aws_role_arn          | The ARN of the AWS role to configure credentials for               | No       | `""`                  |
| aws_region            | The default AWS region to use in all requests                      | No       | `""`                  |
| cli_skip_install      | If "true", will skip installing the CI CLI                         | No       | `"false"`             |
| cli_version           | The version of the CI CLI to install                               | No       | `"latest"`            |
| configure_registries  | If "true", the action will login to container registries           | No       | `"false"`             |
| earthly_runner_secret | The ID of the AWS secret holding Earthly remote runner credentials | No       | `""`                  |
| earthly_skip_install  | If "true", will skip installing Earthly                            | No       | `"false"`             |
| earthly_version       | The version of Earthly to install (defaults to latest)             | No       | `"latest"`            |
| github_token          | Github token used to login to GHCR                                 | No       | `${{ github.token }}` |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
