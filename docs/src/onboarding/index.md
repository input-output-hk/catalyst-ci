# Welcome

Welcome to the onboarding section of the documentation.
This section will guide you through the fundamentals of the Catalyst CI process and introduce you to the various tools and processes
that we use.

## Overview

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    This section will talk about concepts related to [Earthly](https://earthly.dev).
    If you are not familiar with Earthly, please head over [to the appendix](./appendix/earthly.md) to learn more about it before
    continuing.
<!-- markdownlint-enable max-one-sentence-per-line -->

To understand how the overall CI process works, it first helps to understand the problem.

### The Problem

Project Catalyst owns several monorepos, each containing many subprojects.
Each of these subprojects carry a number of deliverables: images, artifacts, etc.
Trying to track each of these deliverables in CI becomes difficult, and usually results in a plethora of workflows being created.
Worse, sometimes these workflows conflict, or build the same thing more than once.

### The Solution

To solve this problem while simultaneously reducing developer cognitive load, a unique discovery system was designed.
The discovery system utilizes a small CLI shipped with the Catalyst CI repository which crawls a given monorepo and discovers the
location of all `Earthfile`s.
An additional target filter can be applied to the discovery process such that it only returns `Earthfile`s with a given target.
Using this CLI, the discovery process can, for example, find the location of all `Earthfile`s with a `release` target.

Using the above filtered discovery process, we can now standardize on a small number of reserved targets with which the CI system
is guaranteed to interact with.
These targets are as follows:

1. `check` - This target is expected to run all necessary checks to validate the health of the project.
   This includes formatting, linting, and possibly unit tests.
   This target must pass for other targets to run.
1. `build` - This target is expected to build any artifacts provided by the project
   The primary purpose of this target is to validate that things are building without error.
   This target must pass for other targets to run.
1. `package` - This target is expected to package multiple artifacts into a single package.
   It is typically used outside of the scope of a single subproject and instead combines outputs from multiple subprojects into a
   single deliverable.
   This target must pass for other targets to run.
1. `test` - This target is expected to run tests that prove the subproject, or multiple subprojects, are working as expected.
   The target can be used to run any sort of test, including unit tests, smoke tests, and integration tests.
   This target must pass for other targets to run.
1. `release` - This target is expected to produce a single release artifact.
   This could be a binary, a collection of resources, or even certain reports.
   When a tag commit is pushed, the CI will build this target and include the produced artifact as part of a GitHub Release.
1. `publish` - This target is expected to produce a single container image.
   The CI will automatically build and publish this image to configured registries during certain types of git events.

The above summaries are not exhaustive and only intended to introduce you to the overall concept.
We will dig further into these reserved targets at a later point.

The primary point to take away is that the discovery process allows developers to contractually declare all of their deliverables
from a single `Earthfile` that is tightly coupled to the subproject they are working within.
While knowledge of how the CI system is helpful for troubleshooting purposes, it's purely extracurricular and not required.
Instead, a developer must only remember these reserved targets in order to have their deliverables handled accordingly.

In the remaining sections of this onboarding guide, we will cover the components that make up Catalyst CI, how they are molded
together to create reusable workflows, and finally some examples to get started using these actions and workflows.
