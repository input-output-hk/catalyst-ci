---
icon: simple/postgresql
---
# :simple-postgresql: PostgreSQL

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/postgresql/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build PostgreSQL database.
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI to build,
release, and publish our PostgreSQL database.

To begin, clone the Catalyst CI repository:

```sh
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/postgresql` to find a basic PostgreSQL database configuration with some initial data.
This folder already contains an `Earthfile` in it.
This is the `Earthfile` we will be building in this guide.
You can choose to either delete the file and start from scratch, or read the guide and follow along in the file.

## Building the Earthfile

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    The below sections will walk through building our `Earthfile` step-by-step.
    In each section, only the fragments of the `Earthfile` relative to that section are displayed.
    This means that, as you go through each section, you should be cumulatively building the `Earthfile`.
    If you get stuck at any point, you can always take a look at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/postgresql/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Prepare base builder

```Earthfile
VERSION 0.7

builder:
    FROM ./../../earthly/postgresql+postgres-base

    WORKDIR /build

    COPY --dir ./migrations ./data ./refinery.toml .
    DO ./../../earthly/postgresql+BUILDER
```

The first target we are going to create will be responsible to prepare a PostgreSQL environment (Earthly `+postgres-base` target),
migrations, migrations configuration and seed data (`COPY --dir ./migrations ./data ./refinery.toml .`),
doing some final build step (Earthly `+BUILDER` UDC target).

In the next steps we are going to inheriting from this `+builder` target which contains all necessary data,
dependencies, environment to properly run PostgreSQL database.

### Running checks

```Earthfile
check:
    FROM +builder

    DO ./../../earthly/postgresql+CHECK

format:
    LOCALLY

    DO ./../../earthly/postgresql+FORMAT --src=$(echo ${PWD})
```

With prepared environment and all data, we're now ready to start operating with the source code - `*.sql` files.
At this step we can begin performing static checks against `*.sql` files.
These checks are intended to verify the code is healthy and well formatted to a certain standard.
These checks are done with the help of the `sqlfluff` tool which is already configured during the `+postgres-base` target.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Before perform formatting it is needed to build `sqlfluff-image` docker image using following command
    `earthly github.com/input-output-hk/catalyst-ci/earthly/postgresql+sqlfluff-image`
<!-- markdownlint-enable max-one-sentence-per-line -->

To apply and fix some formatting issues you can run `+format` target which will picks up directory
where your Earthly file lies in as a source dir for formatting and run `+FORMAT` UDC target.
Under the hood `+FORMAT` UDC target runs `sqlfluff-image` docker container,
which contains the same configuration and setup which is applied during the `+check`.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Specific configuration of `sqlfluff` which is applied during the check and formatting you can find at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/earthly/postgresql/.sqlfluff).
<!-- markdownlint-enable max-one-sentence-per-line -->
