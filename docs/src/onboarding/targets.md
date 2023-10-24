# Targets

As discussed in the overview, the Catalyst CI automatically searches for and executes distinct Earthly targets.
By creating these targets in your `Earthfile`, you can hook into the Catalyst CI process with minimal effort.
This section is dedicated to explaining what these targets are, how they work, and how to use them.

## Check

### Summary

The `check` target is responsible for validating that a given subproject is healthy and up to the appropriate standards.
This target should be used by all subprojects to improve the upkeep of code.
No additional tasks are performed before or after running the target.

### How it Works

Of all the targets, the `check` target is the simplest in that the CI executes it and only expects it to pass.
The `check` target is the **first target run** in the CI pipeline.
Additionally, the `check` target **must pass** before any other targets are run.
This means that all subsequent CI steps, such as building and publishing artifacts, will not be run if the `check` target fails.

### Usage

It's important to avoid adding any steps that may have flaky results to the `check` target.
Reducing the runtime of the `check` phase by avoiding any lengthy processes is also advisable.
This includes things like complex integrations tests or E2E tests that should have their own dedicated workflows.

Some typical tasks that would be appropriate for the `check` target are as follows:

1. Validating code format
2. Linting code
3. Running static analysis tools (i.e. vulnerability scanners)
4. Running unit tests
5. Validating code generation (i.e. making sure code generation has been run)

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
