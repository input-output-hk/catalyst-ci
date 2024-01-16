---
icon: material/book-open-page-variant-outline
---

# Docs

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/docs/Earthfile).
    This guide will provide detailed instructions for how this docs was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build [MkDocs](https://www.mkdocs.org) documentation.
By the end of it, we'll have an `Earthfile`
that utilizes docs build process, and it has been publishing on github pages.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `docs` directory to find current documentation
which you are reading right now.
This folder already has an `Earthfile` in it, which contains all build process.

## Building docs image

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    The below sections will walk through building our `Earthfile` step-by-step.
    In each section, only the fragments of the `Earthfile` relative to that section are displayed.
    This means that, as you go through each section, you should be cumulatively building the `Earthfile`.
    If you get stuck at any point, you can always take a look at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/docs/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

```Earthfile
VERSION --global-cache 0.7

# Copy all the source we need to build the docs
src:
    # Common src setup
    DO ../earthly/docs+SRC

    # Now copy into that any artifacts we pull from the builds.
    COPY --dir ../+repo-docs/repo includes
```

The first step of building process it preparing a source files.
It is mandatory to have a `src` directory with all documentation md files in it and `mkdocs.yml` file.
This directory and file will be picked during the execution of `+SRC` Function target.
Also it is possible to replace defined `includes`, `macros` and `overrides` dirs
to customize some docs appearance and configuration.

Default value of the content of `includes`, `macros` and `overrides` dirs you can find in `earthly/docs/common` folder.
Additionally it is possible to provide some additional files as for example to extend `includes` dir content.

The standard theme is defined in the `std-theme.yml`.
It must be included in the first line of the documentations `mkdocs.yml` file like so:

```yml
INHERIT: std-theme.yml
```

This file can be found in the `earthly/docs/common` folder.  
Changes to the standard theme should be intended to effect all documentation that uses the standard theme.  
Individual documentation targets can customize the theme in their `mkdocs.yml` file.

```Earthfile
# Build the docs here.
docs:
    FROM +src

    DO ../earthly/docs+BUILD
```

To build a docs artifact which will be used later just invoke `+BUILD` Function target
on the already prepared docs environment `+src` target which we have discussed before.

```Earthfile
# Make a docker image that can serve the docs for development purposes.
# This target is only for local developer use.
local:
    DO ../earthly/docs+PACKAGE

    COPY +docs/ /usr/share/nginx/html

    SAVE IMAGE cat-ci-docs:latest
```

To finally build a docker image which is pretty strait forward process,
you should firstly invoke `+PACKAGE` Function target which will prepare an environment for future docs image,
next step is to copy builded artifact from the previous step to `/usr/share/nginx/html` folder.
And the last step is to save a docker image with the specified name, tag and registry if it is needed.

## Local docs run

To locally run docs which it is needed to get a `earthly/docs/dev/local.py` python script
which will automatically invoke `+local` to build docs image what was discussed before.
This script will locally deploy docs and rebuild them if they changed every `10` seconds.
Script should be run from the root of the repository in which `docs` folder exists
with all documentation in it and already discussed `Earthfile`.
Script arguments:

* `container_name` - Name of the container.
* `--exposed-port` - Exposed port of the container (default `8123`).
* `--target` - Earthly target to run (default `./docs+local`).
* `-no-browser` - Do not open the browser.

Here is an example how to run it for current repo

```bash
earthly/docs/dev/local.py cat-ci-docs:latest
```

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    To deploy docs for any other repositories as for example `catalyst-voices` or any other
    as it was mentioned above it is needed to get `local.py` script and run it from the root
    of your repo as for example `<path_to_catalyst_ci>/earthly/docs/dev/local.py <docker_image_name>`
<!-- markdownlint-enable max-one-sentence-per-line -->

## Doc's update PR

When a PR is raised the documentation for that PR is built and published.
Branch docs are published to `<pages>/branch/<branch_name>`.
`<branch_name>` is the name of the branch with all non alpha-numeric characters replaced by underscore (`_`).

When the branch is finally merged, the branch documentation is removed.
This allows us to easily validate what any PR will do to the published documentation before its published officially.

All PR's documentation should be checked as part of PR review.
Not just the contents of the PR itself.
