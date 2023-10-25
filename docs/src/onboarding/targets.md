# Targets

As discussed in the overview, the Catalyst CI automatically searches for and executes distinct Earthly targets.
By creating these targets in your `Earthfile`, you can hook into the Catalyst CI process with minimal effort.
This section is dedicated to explaining what these targets are, how they work, and how to use them.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    The targets discussed below are *not* required to be implemented in every single `Earthfile`.
    Consider each target a building block that can be composed into a complete structure that CI runs.
    The system is meant to be adaptable to different workflows.
<!-- markdownlint-enable max-one-sentence-per-line -->

## Check

### Summary

The `check` target is responsible for validating that a given subproject is healthy and up to the appropriate standards.
This target should be used by all subprojects to improve the upkeep of code.
No additional tasks are performed before or after running the target.

### How it Works

The `check` target is the **first target run** in the CI pipeline and **must pass** before any other targets are run.
The CI will call the `check` target and fail if it returns a non-zero exit code.

### Usage

It's important to avoid adding any steps that may have flaky results to the `check` target.
Reducing the runtime of the `check` phase by avoiding any lengthy processes is also advisable.
This includes things like complex integrations tests or E2E tests that should have their own dedicated workflows.
The goal of the `check` target is to "fail fast" and avoid running a lengthy CI pipeline if there are immediate problems with the
code.

Some typical tasks that would be appropriate for the `check` target are as follows:

1. Validating code format
2. Linting code
3. Running static analysis tools (i.e. vulnerability scanners)

## Build

### Summary

The `build` target is responsible for building artifacts.
It serves two purposes:

1. To validate that a given build works prior to performing any other steps
2. To cache the build so future steps can re-use it without a performance impact.

No additional tasks are performed before or after running the target.
The target must pass before subsequent targets are called.

### How it Works

The `build` target is the **second target run** in the CI pipeline and **must pass** before any other targets are run.
The CI will call the `build` target and fail if it returns a non-zero exit code.

### Usage

The `build` artifact should only be used for running "build" processes.
What defines a build process is unique to each project.
For example, it could be anything from compiling a binary to transpiling a medium into its final form
(i.e., Typescript -> Javascript).

Downstream targets should always depend on the `build` target for maximizing cache hits.
For example, the `test` and `release` targets should either inherit from the `build` target or copy artifacts from it.

## Package

### Summary

The `package` target is responsible for taking multiple artifacts and packaging them together.
In mono-repos especially, deliverables sometime consist of more than one artifact being produced by different subprojects.
This target is intended to provide an additional step where this packaging can happen before the `test` phase where these packages
are usually utilized in E2E or integration testing.

### How it Works

The `package` target is the **third target run** in the CI pipeline and **must pass** before any other targets are run.
The CI will call the `package` target and fail if it returns a non-zero exit code.

### Usage

The `package` target is very similar to the `build` target in that it should be used for building artifacts.
However, the `build` target is geared specifically at building an artifact from the context of a single project
(i.e., a single binary).
The `package` target is instead focused on composing the outputs of multiple build artifacts into a single package.
What constitutes a package is intentionally left vague, as the definition can change from project to project.
In smaller repos, this target should be skipped.

## Test

### Summary

The `test` target is responsible for running tests to validate things are working as expected.
The target is intended to be versatile, and can be used to run several different formats of testing.
For example:

1. Unit tests
2. Smoke tests
3. Integration tests

### How it Works

The `test` target is the **fourth target run** in the CI pipeline and **must pass** before any other targets are run.
The CI will call the `test` target and fail if it returns a non-zero exit code.

### Usage

The `test` target is intended to be versatile.
In many cases, separate `Earthfile`s that are outside of the scope of a single subproject are created to hold a `test` target which
runs integration tests.
At the same time, individual subprojects may utilize this target to run their own unit tests.

The only requirement is that the target should *only* be used to run tests.
This target is the final target that is run (and must pass) before artifacts are released and/or published.

## Publish

### Summary

The `publish` target is responsible for building and publishing a container image to image registries.
This target should be used when a subproject needs to produce and publish a container image.
The CI will execute this target after the `check` target, assuming it passes.

### How it Works

After executing the target, the CI will automatically detect the name and tag of the resulting image and save it for future steps.
If the commit that triggered the CI is from a PR, the resulting image **will not** be published to an image registry.
Instead, after building the image, the CI will immediately stop.
This allows end-users to validate that an image is building correctly during the PR process without cluttering downstream image
registries with incomplete and/or broken images.

If the commit that triggered the CI is a merge into the default branch (i.e. `main`), the resulting image is re-tagged with the
commit hash and published to the Project Catalyst internal registry.
If the resulting image is deployable, the CI will automatically deploy it to the `dev` cluster (i.e. `dev.projectcatalyst.io`).
This ensures that the `dev` cluster always reflects changes from the mainline branch.

Finally, if the commit that triggered the CI contains a tag, the steps discussed in the previous section are also performed, but
with additional steps.
The resulting image is not only tagged with the commit hash, but also with the git tag contained in the commit.
The image is also published to the public GHCR registry associated with the GitHub repository.

### Usage

When creating the `target` image, the only requirement is that the target produce a **single** image at the end using `SAVE IMAGE`.
It's recommended that you use the `latest` tag, as by default the CI ignores the tag produced by the target.
The CI will automatically handle auxiliary tasks like image scanning and/or signing, so these steps should be omitted.

## Release

The `release` target is responsible for building and releasing artifacts to GitHub.
This target should be used when a subproject produces artifacts (i.e. a binary) that is appropriate to include in a GitHub release.
For example, a subproject may produce a binary that is intended to be used directly (i.e. a CLI) or it may produce a set of files
that end-users need access to during a release cycle.
The CI will execute this target after the `check` target, assuming it passes.

### How it Works

After executing the target, the CI will automatically detect any artifacts that were produced by the target and mark them to be
saved.
If the commit that triggered the CI does not contain a git tag, then the CI will immediately stop.
This allows end-users to validate that their release artifacts build as expected without relying on a release cycle.

If instead the commit contains a git tag, then the resulting artifacts are compressed into a single tarball and uploaded as an
artifact of the GitHub Action job.
The compression happens regardless of whether a single or multiple artifacts were produced.
After the `release` target has been run for *every* subproject, the produced artifacts from all subprojects are then attached into a
single GitHub release for the given git tag (i.e., `1.0.0`).

### Usage

When creating the `release` image, you may use as many `SAVE ARTIFACT` statements as you would like, however, it's recommended to
only use one.
At a minimum, the target must produce at least a single artifact.
An artifact may be a single file, multiple files, or even a complex folder structure.

Artifacts should have some relevance for a GitHub release.
For example, making the target save the local source code is redundant since GitHub automatically includes all source code when a
new release is created.
However, a consumer may want to be able to download precompiled versions of a binary (without relying on a container).
In this case, it makes sense to create a release target that produces the binary as an artifact.
