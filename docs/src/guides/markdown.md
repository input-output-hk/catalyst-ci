---
icon: simple/markdown
---

# Markdown Check

This Earthly Target and Function enables uniform linting of Markdown files to maintain consistency and quality.

This Function is **NOT** intended to be used inside container builds.
Its sole purpose is to enforce uniform style rules for all markdown files in a repository.
It makes no assumptions about which files may or may not end up inside a container or are part of a build.
This is *INTENTIONAL*.

IF this Function is used inside a container build, it is **NOT** a bug if it does not do the correct thing.

## Introduction

Markdown file checking is integrated into the `check` pipeline.
The reference to the pipeline can be found [here](https://input-output-hk.github.io/catalyst-ci/onboarding/).
The goal of the `check` stage is to ensure the overall health of the project.
Specifically, for markdown checks, it ensures that all markdown files follow valid rules.

## Configuration

Each repo will need two configuration files in the root of the repository:

* `.markdownlint.jsonc` - Configures individual markdown rules.
* `.markdownlint-cli2.jsonc` - Configures the CLI Tool.

The configuration should be copied from the root of the Catalyst-CI repository into the target repo.
Individual projects should have no need to individually customize these rules.
Any changes to the markdown rules should be it's own PR.
It should first be made to the Base rules in the Catalyst-CI project and only once merged, copied into all other effected repos.

This is to ensure a consistent rule set across all repos.

Additional references to the rules can be read [here](https://github.com/DavidAnson/markdownlint/)

## How it works

Linting is performed with the [`mdlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) program.

This linter is to be used in preference to any other Markdown linter.
This is because we need to provide uniform and consistent Markdown formatting and linting across the project and between projects.

## Using the markdown check

### Locally

#### Running check

Executing `earthly +check` will automatically run all checks, including the verification of markdown files in the repository.
To view the specific checks performed during the `check` stage, use the command `earthly doc`.
All the check done in check target should be named as `check-<name>`.

#### Running markdown fix

If an error occurs, `earthly +markdown-check-fix` can be used to automatically fix the error.
<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Please note that this command will fix the issues based on the capabilities of the linter.
<!-- markdownlint-enable max-one-sentence-per-line -->

### Remotely

Performing a markdown check can be done in your repository by adding the following code:

#### Checking the markdown in your repo

```earthfile
check-markdown:
    DO github.com/input-output-hk/catalyst-ci/earthly/mdlint:<tag>+CHECK
```

Note that the source directory is not required since default is set as current directory.

#### Checking and fixing the markdown in your repo

```earthfile
markdown-check-fix:
    LOCALLY

    DO github.com/input-output-hk/catalyst-ci/earthly/mdlint:<tag>+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix
```

In this use case, the Function is run Locally, so that the markdown in the repo can be directly checked.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    `tag` is needed to be specified to the right version.
<!-- markdownlint-enable max-one-sentence-per-line -->

## Disable markdownlint rules

Markdown linter rules can be disable for specific file or lines.

``` html
<!-- markdownlint-disable rules -->
```

For more example, please refer to this [doc](https://github.com/DavidAnson/markdownlint/#configuration)

## Editor Integration

mdlint-cli2 is integrated into VSCode and may be integrated into other Editors.

The editor integration should pick up both the `.markdownlint.jsonc` and `.markdownlint-cli2.jsonc` configuration files.
It will then behave exactly the same as the Earthly Function.
