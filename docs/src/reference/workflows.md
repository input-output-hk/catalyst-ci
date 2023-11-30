# Workflows

The Catalyst CI process works by combining several high-level reusable workflows into a single workflow that is used across all of
our repositories.
The purpose for this is to standardize the CI process across all repositories as well as provide control for easily updating the CI
process without having to make changes across multiple repositories.
This section gives a brief overview of these reusable workflows, which can aid in troubleshooting purposes.

## Overview

Most reusable workflows have a one-to-one relationship with the Earthly targets discussed in the previous section:

* `ci.yml` is responsible for running the entire CI pipeline
* `run.yml` is responsible for executing targets with no additional steps (i.e., `check`, `build`, and `package` targets)
* `publish.yml` is responsible for handling the `publish` target
* `release.yml` is responsible for handling the `release` target

Each workflow is self-contained and independent of the other workflows.
However, in most cases, they are tied together with conditionals (i.e. `publish` only runs if `check` succeeds).
Each workflow typically uses one or more custom GitHub Actions that are also provided by the Catalyst CI system.
These individual actions will be discussed in the next section.
Since most of the workflow logic was discussed in the previous section, this section will refrain from duplicating that effort and
instead focus on how to use the workflows (including covering their inputs).

### Common Inputs

#### AWS

Most of the workflows accept an optional AWS role and region.
The workflow will attempt to automatically authenticate and assume the role prior to performing any other steps.
In most cases, this is necessary, because the Catalyst CI uses a remote Earthly runner to improve caching efforts.
The credentials for the remote runner are held in AWS and need to be retrieved by the workflow.
The only other case where AWS authentication is required is during the `publish` workflow where images are pushed to ECR.

| Name         | Type   | Description                                                  | Required | Default |
| ------------ | ------ | ------------------------------------------------------------ | -------- | ------- |
| aws_role_arn | string | The ARN of the AWS role that will be assumed by the workflow | No       | `""`    |
| aws_region   | string | The AWS region that will be used by the workflow             | No       | `""`    |

#### Earthly Runner

As noted above, Catalyst CI uses a remote Earthly runner in order to maximize cache hits.
As a result, all workflows that interact with Earthly will accept optional inputs describing the address of the runner as well as
the name of an AWS secret containing the authentication details.
The workflow will configure the local GitHub runner using the TLS credentials retrieved from AWS so that it can successfully connect
and interact with the remote Earthly runner.

| Name                   | Type   | Description                                                 | Required | Default  |
| ---------------------- | ------ | ----------------------------------------------------------- | -------- | -------- |
| earthly_runner_address | string | The address of the Earthly runner that will be used         | No       | `""`     |
| earthly_runner_secret  | string | The ID of the AWS secret holding Earthly runner credentials | No       | `""`     |
| earthly_version        | string | The version of Earthly to use.                              | No       | `latest` |

#### CLI

Most workflows utilize the custom CLI provided by the Catalyst CI repository.
It's possible to specify a specific version of the CI to be installed (as opposed to the default of installing the latest).

| Name           | Type   | Description                       | Required | Default  |
| -------------- | ------ | --------------------------------- | -------- | -------- |
| ci_cli_version | string | The version of the CI CLI to use. | No       | `latest` |

## CI

The CI workflow is responsible for executing the entire CI pipeline.
This workflow is a composition of the other reusable workflows covered in this section.
It's purpose is to reduce the friction for introducing the CI process into a repository by consolidating it to a single workflow.

### Inputs

| Name             | Type   | Description                                                                        | Required | Default |
| ---------------- | ------ | ---------------------------------------------------------------------------------- | -------- | ------- |
| aws_ecr_registry | string | The AWS ECR registry that will be used to publish images                           | No       | `""`    |
| force_artifact   | bool   | If true, the workflow will always produce an artifact                              | No       | `false` |
| tags             | string | A line separated list of additional tags that will be applied to published images. | No       | `""`    |

## Run

The run workflow is a general purpose workflow that discovers and executes a given Earthly target.
Many of the CI steps follow this same pattern and this workflow serves the purpose of reducing boilerplate.
For adding ad-hoc steps, specifically ones that just need to execute a target, this is the correct workflow to use.

### Inputs

| Name   | Type   | Description                    | Required | Default |
| ------ | ------ | ------------------------------ | -------- | ------- |
| target | string | The target to discover and run | Yes      | N/A     |

## Publish

The publish workflow is responsible for performing the logic related to the `publish` target.
It uses the custom `run` GitHub Action to execute the target and parse the name/tag of the resulting image.
It then uses the custom `push` GitHub Action to re-tag the image and push it to the appropriate image registries.

### Inputs

| Name             | Type   | Description                                                                        | Required | Default                                         |
| ---------------- | ------ | ---------------------------------------------------------------------------------- | -------- | ----------------------------------------------- |
| aws_ecr_registry | string | The AWS ECR registry that will be used to publish images                           | No       | `""`                                            |
| default_branch   | string | The default branch of the repository.                                              | No       | `${{ github.event.repository.default_branch }}` |
| tags             | string | A line separated list of additional tags that will be applied to published images. | No       | `""`                                            |
| target           | string | The target used to mark check builds                                               | No       | `publish`                                       |

## Release

The release workflow is responsible for performing logic related to the `release` target.
It uses the custom `run` GitHub Action to execute the target and store the produced artifacts to a local directory on the runner.
These artifacts are then compressed and ultimately uploaded as artifacts for the job and/or a new GitHub release.

### Inputs

| Name           | Type   | Description                                           | Required | Default   |
| -------------- | ------ | ----------------------------------------------------- | -------- | --------- |
| target         | string | The target used to mark check builds                  | No       | `release` |
| force_artifact | bool   | If true, the workflow will always produce an artifact | No       | `false`   |

## Deploy

The deploy workflow is responsible for deploying services to the Catalyst `dev` cluster when new container images are produced.
It checks out the code from a private Project Catalyst repository and uses the custom `merge` GitHub Action to merge the new image
tags into the repository files.
The changes are then committed, which triggers the `dev` environment to deploy the newly produced images.

### Inputs

| Name            | Type   | Description                                              | Required | Default                          |
| --------------- | ------ | -------------------------------------------------------- | -------- | -------------------------------- |
| deployment_repo | string | The URL of the repository to merge with                  | No       | `input-output-hk/catalyst-world` |
| environment     | string | The target environment to deploy                         | No       | `dev`                            |
| images          | string | A newline separated list of image names to deploy        | Yes      | N/A                              |
| tag             | string | The image tag to deploy                                  | Yes      | N/A                              |
| token           | string | A Github token with access to the deployment repository. | Yes      | N/A                              |

## Pages

The pages workflow is responsible for building documentation and deploying to GitHub Pages.
It can be configured to point to an `Earthfile` and target that produces static documentation.
The workflow will execute the target, and if the commit is a merge to the default branch, push the resulting files to the `gh_pages`
branch.

### Inputs

| Name      | Type   | Description                                                        | Required | Default |
| --------- | ------ | ------------------------------------------------------------------ | -------- | ------- |
| earthfile | string | The path to the folder containing the Earthfile that will be built | Yes      | N/A     |
| target    | string | The target that will be used to build docs                         | Yes      | N/A     |
