# setup-deploy

## Description

Performs required steps to setup CI.

## Inputs

| parameter       | description                                        | required | default |
| --------------- | -------------------------------------------------- | -------- | ------- |
| aws_role_arn    | The ARN of the CI role (used for fetching secrets) | `true`   |         |
| aws_region      | The AWS region to use                              | `true`   |         |
| cli_version     | The version of the CI CLI to install               | `false`  | 0.0.1   |
| earthly_version | The version of Earthly to install                  | `false`  | latest  |

## Runs

This action is a `composite` action.
