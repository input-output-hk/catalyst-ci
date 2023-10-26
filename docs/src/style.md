# Style Guide

## Introduction

This style guide is intended for individuals who are contributing towards the various `Earthfile`s within Catalyst repositories.
It provides a set of standards that we use in creating these files.
In most circumstances, the standards provided by this style guide should *not* be violated.
If an exception must me made, the rationale should be included in the respective PR.
Any `Earthfile` which does not adhere to this style guide will be rejected if no further justification is made.

## Organization

### Adhere to a consistent structure

The following structure should be used to provide a consistent structure to `Earthfile`s:

```Earthfile
VERSION 0.7  # Should be the same across the repository

deps:
    FROM <base image>
    # This target should download and install all external dependencies. This
    # includes language dependencies as well as system dependencies.

src:
    FROM +deps
    # This target should copy in all source code.
    # By doing this, it makes it clear what's considered source code.
    # It also consolidates this step to a single target and avoids trying to
    # track the source files across multiple targets.

check:
    FROM +src
    # This target is used by the CI and should perform linting/formatting/static
    # analysis checks.

build:
    FROM +build
    # This target is used by the CI and should be used to build the project.

test:
    FROM +build
    # This target is used by the CI and should be used to running all tests that
    # are related to the project. This includes unit tests and basic smoke tests.

release:
    FROM +build
    SAVE ARTIFACT ./artifact
    # This target is used by the CI and should use `SAVE ARTIFACT` to save the
    # result of the build step in cases where the artifact should be included
    # with the GitHub release (i.e., things that are self-contained like CLIs).

publish:
    FROM <base image>
    COPY +build/artifact .
    SAVE IMAGE image:latest
    # This target is used by the CI and should use `SAVE IMAGE` to save a
    # container image that should be published to a registry by the CI. It
    # typically copies artifacts from the build target and then sets up the
    # required container environment.
```

While the above structure is not perfect for every situation, it's flexible enough to meet most requirements.
When steering away from this structure, every effort should be made to keep as much of it as possible for the sake of consistency.

### Avoid using the base target

Every `Earthfile` has an invisible "base" target.
This target is made up of the commands that appear outside of an existing target.
For example:

```Earthfile
VERSION 0.7
FROM ubuntu:latest  # Apart of the base target
WORKDIR /work  # Apart of the base target
```

By default, any target which does not inherit from a base image will use the
`FROM` statement included in the base target.
This can become especially confusing when the target is far away from the base
target which is usually put at the beginning of the file.

There's no technical advantage for using the base target, and at most it makes
code a bit more DRY.
However, this comes at the expense of clarity.
As such, the base target should be avoided, and individual targets should be
clear about their intentions:

```Earthfile
VERSION 0.7

deps:
    FROM ubuntu:latest
    WORKDIR /work
```

## Syntax

### Always tag remote Earthfile references

When referencing an Earthfile from another repository, always append a git tag
to it.
For example:

```
DO github.com/input-output-hk/catalyst-ci/earthly/udc+NAME:tag
```

Where `tag` is the git tag.
This ensures that upstream changes do not incidentally break builds.

### Avoid `--no-cache`

The `RUN` command allows passing a `--no-cache` flag which will force Earthly
to skip caching this particular command.
The result is that the cache will *always* be broken at this step.
This is especially frustrating when downstream targets inherit a target using
this flag and all caching proceeds to immediately stop.

To prevent this, the `--no-cache` should be avoided at all times.
The only acceptable time to use it is for debugging purposes.

### Prefer UDCs

The primary purpose of a UDC is to reduce boilerplate and promote reusing common workflows.
Many build patterns tend to be repetitive.
For example, copying a package lockfile and installing dependencies is very common.

In these cases, a UDC should be preferred.
The `catalyst-ci` repository provides a number of UDCs in the `earthly` subdirectory.
These should be used prior to writing a new one.
If a common use case is not covered in this subdirectory, a PR should be opened to add it.
