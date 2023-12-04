# Markdown Linter

This Earthly Target and UDC enables uniform linting of Markdown files to maintain consistency and quality.

## DO NOT RUN AS PART OF A CONTAINER BUILD TARGET

This UDC is **NOT** intended to be used inside container builds.
Its sole purpose is to enforce uniform style rules for all markdown files in a repository.
It makes no assumptions about which files may or may not end up inside a container or are part of a build.
This is *INTENTIONAL*.

IF this UDC is used inside a container build, it is **NOT** a bug if it does not do the correct thing.

## How it works

Linting is performed with the [`mdlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) program.

Use the `MDLINT` Earthly UDC to enable uniform and consistent Markdown Format checking.

This linter is to be used in preference to any other Markdown linter.
This is because we need to provide uniform and consistent Markdown formatting and linting across the project and between projects.

## Using the markdown check

In an Earthfile in your repo, add the following:

### Checking the markdown in your repo

Note that the source directory is not required since default is set as current directory.

```earthfile
markdown-lint:
    DO github.com/input-output-hk/catalyst-ci/earthly/mdlint:<tag>+CHECK
```

### Checking and fixing the markdown in your repo

```earthfile
markdown-lint-fix:
    LOCALLY

    DO github.com/input-output-hk/catalyst-ci/earthly/mdlint:<tag>+MDLINT_LOCALLY --src=$(echo ${PWD}) --fix=--fix
```

In this use case, the UDC is run Locally, so that the markdown in the repo can be directly checked.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Please note that this command will fix the issues based on the capabilities of the linter.
    Additionally, `tag` is needed to be specified.
<!-- markdownlint-enable max-one-sentence-per-line -->

## Configuration

Each repo will need two configuration files in the root of the repository:

* `.markdownlint.jsonc` - Configures individual markdown rules.
* `.markdownlint-cli2.jsonc` - Configures the CLI Tool.

The configuration should be copied from the root of the Catalyst-CI repository into the target repo.
Individual projects should have no need to individually customize these rules.
Any changes to the markdown rules should be it's own PR.
It should first be made to the Base rules in the Catalyst-CI project and only once merged, copied into all other effected repos.

This is to ensure a consistent rule set across all repos.

## Editor Integration

mdlint-cli2 is integrated into VSCode and may be integrated into other Editors.

The editor integration should pick up both the `.markdownlint.jsonc` and `.markdownlint-cli2.jsonc` configuration files.
It will then behave exactly the same as the Earthly UDC.
