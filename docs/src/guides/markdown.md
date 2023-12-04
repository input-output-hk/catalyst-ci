---
icon: material/simple-markdown
---

# Markdown Check

## Introduction

Markdown file checking is integrated into the `check` pipeline.
The reference to the pipeline can be found [here](https://input-output-hk.github.io/catalyst-ci/onboarding/).
The goal of the `check` stage is to ensure the overall health of the project.
Specifically, for markdown checks, it ensures that all markdown files follow valid rules.

## Configuration

Each repo will need two configuration files in the root of the repository:

* `.markdownlint.jsonc` - Configures individual markdown rules.
* `.markdownlint-cli2.jsonc` - Configures the CLI Tool.

References to the rules can be read [here](https://github.com/DavidAnson/markdownlint/)

## How it works

### Locally

#### Running check

Executing `earthly +check` will automatically run all checks, including the verification of markdown files in the repository.
To view the specific checks performed during the `check` stage, use the command `earthly doc`.

#### Running markdown fix

If an error occurs, `earthly +markdown-check-fix` can be used to automatically fix the error.
<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Please note that this command will fix the issues based on the capabilities of the linter.
<!-- markdownlint-enable max-one-sentence-per-line -->

### Remotely

#### Running check

Running `check` stage can be done by referencing to the `check` target created in this repository by adding

``` Earthfile
IMPORT github.com/input-output-hk/catalyst-ci/:<tag>
```

## Disable markdownlint rules

Markdown linter rules can be disable for specific file or lines.

``` html
<!-- markdownlint-disable rules -->
```

For more example, please refer to this [doc](https://github.com/DavidAnson/markdownlint/#configuration)
