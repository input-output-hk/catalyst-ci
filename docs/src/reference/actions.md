# GitHub Actions

Catalyst CI is made up of several GitHub Actions that simplify the steps required to perform the CI process.
All of these GitHub Actions are compiled into reusable workflows which perform a majority of the CI logic.

## Overview

The following actions are provided by Catalyst CI:

* [configure-runner](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/configure-runner)
* [discover](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/discover)
* [install](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/install)
* [merge](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/merge)
* [push](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/push)
* [run](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/run)
* [setup](https://github.com/input-output-hk/catalyst-ci/tree/master/actions/setup)

This section will only highlight the actions which are commonly used in most workflows.
Additionally, we will not cover these actions in depth.
If you're interested in learning more about a specific action, please click the link above and review the `README`.

## Actions

### Setup

The `setup` action is by far the most common action and shows up in a majority of workflows.
It performs the necessary steps to setup the local GitHub runner to perform CI tasks.
This includes:

* Installing Earthly
* Installing the custom CI CLI
* Configuring access to AWS
* Authenticating with container registries
* Configuring the Earthly remote runner

Most of these steps are configurable and can be individually disabled.
When creating custom workflows, it's highly recommended to use this action to perform common set up tasks.
This action uses the `configure-runner` and `install` actions underneath the hood.
Using these actions individually should be avoided unless absolutely necessary.

### Discover

The `discover` action is another common action that shows up in many workflows.
It performs the "discovery" mechanism of finding Earthfiles with specific targets.
For example, the `check` workflow uses this action to discover all Earthfiles that have a `check` target.
The custom CI CLI **must** be installed (see the above section) in order for this action to work.

This action is useful when creating custom workflows which extend the existing Catalyst CI process.
It can be used to create similar logic for discovering and acting upon specific Earthly targets contained in a repository.

### Run

The `run` action is another common action that shows up in many workflows.
It is responsible for executing the `earthly` CLI underneath the hood.
A custom action was created to perform this task for the following reasons:

1. It simplifies long and hard to read Earthly invocations into a simple contractual interface.
2. It allows capturing and parsing output for additional information (i.e., the names of produced container images)
3. It allows bolting on additional functionality (i.e., automatic retries)

When creating custom workflows, it's highly recommended to use this action when calling Earthly for the above reasons.
If the action does not support the invocation you need, it's better to modify the action rather than manually execute the `earthly`
CLI.
The only exception to this rule is when the invocation is unlikely to be used in more than one place.
