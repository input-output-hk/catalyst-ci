---
icon: simple/postgresql
title: PostgreSQL
tags:
    - PostgreSQL
---

<!-- markdownlint-disable single-h1 -->
# :simple-postgresql: PostgreSQL
<!-- markdownlint-enable single-h1 -->

<!-- cspell: words healthcheck isready psql -->

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
VERSION 0.8

IMPORT ../../earthly/postgresql AS postgresql-ci
IMPORT ../../utilities/scripts AS scripts
IMPORT ../../ AS cat-ci

# Internal: builder is our Event db builder target. Prepares all necessary artifacts.
#   CI target : dependency
builder:
    DO postgresql-ci+BUILDER

    # MUST Manually copy the .sqlfluff config used in the repo because the FUNCTION
    # above can not be passed a reference to a local target as an argument.
    COPY cat-ci+repo-config/repo/.sqlfluff .
```

<!-- TODO - FIX this part -->
Given `BUILDER`
```Earthfile
# Common build setup steps.
# Arguments:
#   sqlfluff_cfg - REQUIRED - Location of repos .sqlfluff configuration file.
#   migrations - OPTIONAL - Location of Migrations directory - DEFAULT: ./migrations
#   seed - OPTIONAL - Location of Seed data directory - DEFAULT: ./seed
#   refinery_toml - OPTIONAL - Location of refinery,toml which configures migrations. DEFAULT: ./refinery.toml
BUILDER:
    FUNCTION

    ARG migrations=./migrations
    ARG seed=./seed
    ARG refinery_toml=./refinery.toml
    
    FROM +postgres-base

    WORKDIR /build

    COPY --dir $sqlfluff_cfg .
    COPY --dir $migrations .
    COPY --dir $seed .
    COPY --dir $refinery_toml .
```

The first target we are going to consider will be responsible to prepare a PostgreSQL environment (Earthly `+postgres-base` target),
migrations, migrations configuration and seed data (`COPY --dir ./migrations ./data ./refinery.toml .`),
doing some final build step (Earthly `+BUILDER` FUNCTION).

In the next steps we are going to inheriting from this `+builder` target which contains all necessary data,
dependencies, environment to properly run PostgreSQL database.

### Running checks

```Earthfile
VERSION 0.8

IMPORT ../../earthly/postgresql AS postgresql-ci
IMPORT ../../utilities/scripts AS scripts
IMPORT ../../ AS cat-ci

# check if the sql files are properly formatted and pass lint quality checks.
#   CI target : true
check:
    FROM +builder

    # Now you can run the script without the file not found error
    DO postgresql-ci+CHECK

# Internal: builder is our Event db builder target. Prepares all necessary artifacts.
#   CI target : dependency
builder:
    DO postgresql-ci+BUILDER

    # MUST Manually copy the .sqlfluff config used in the repo because the FUNCTION
    # above can not be passed a reference to a local target as an argument.
    COPY cat-ci+repo-config/repo/.sqlfluff . 

# format all SQL files in the current project.  Local developers tool.
#   CI target : false
format:
    LOCALLY

    DO postgresql-ci+FORMAT --src=$(echo ${PWD})
```

With prepared environment and all data, we're now ready to start operating with the source code - `*.sql` files.
At this step we can begin performing static checks against `*.sql` files.
These checks are intended to verify the code is healthy and well formatted to a certain standard
and done with the help of the `sqlfluff` tool which is already configured during the `+postgres-base` target.

To apply and fix some formatting issues you can run `+format` target which will picks up directory
where your Earthly file lies in as a source dir for formatting and run `+FORMAT` FUNCTION.
Under the hood `+FORMAT` FUNCTION runs `sqlfluff-image` docker image,
which contains the same configuration and setup which is applied during the `+check`.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Specific configuration of `sqlfluff` which is applied during the check and formatting you can find at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/earthly/postgresql/.sqlfluff).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Build

```Earthfile
# build an event db docker image.
#   CI target : true
build:
    FROM +builder

    DO postgresql-ci+BUILD --image_name=example-db
    DO postgresql-ci+DOCS
```

With the `*.sql` files validation out of the way, we can finally build our PostgreSQL docker image.
Since we need migration and seed data files,
we'll inherit from the `builder` target.
The actual image build process is pretty straight-forward
and fully defined under the `+BUILD` FUNCTION.
The only thing it is needed to specify is a few arguments:

* `tag` - the tag of the image, default value `latest`.
* `registry` - the registry of the image.
* `image_name` - the name of the image (required).

### Run

To run already builded docker image it is possible with the following `docker-compose.yml`

```yaml
version: "3"

services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 2s
      timeout: 5s
      retries: 10
    ports:
      - 5433:5432

  example:
    image: example-db:latest
    environment:
      # Required environment variables for migrations
      - DB_HOST=${DB_HOST:-localhost}
      - DB_PORT=5432
      - DB_NAME=ExampleDb
      - DB_DESCRIPTION=Example DB
      - DB_SUPERUSER=postgres
      - DB_SUPERUSER_PASSWORD=postgres
      - DB_USER=example-dev
      - DB_USER_PASSWORD=example-pass

      - INIT_AND_DROP_DB=${INIT_AND_DROP_DB:-true}
      - WITH_MIGRATIONS=${WITH_MIGRATIONS:-true}
      - WITH_SEED_DATA=${WITH_SEED_DATA:-true}
    ports:
      - 5432:5432
```

There are 4 possible options how to run:

* If `DB_HOST` env var established to `localhost`,
PostgreSQL server runs as a part of the `example` service,
otherwise will relies on remote PostgreSQL server connection
(as an example already defined `postgres` service).
* `INIT_AND_DROP_DB` env var defines to run initial initialization of the db with the clean state or not
(optional, default `false`).
* `WITH_MIGRATIONS` env var defines to run migrations defined inside `./migrations` dir or not
(optional, default `false`).
* `WITH_SEED_DATA` env var defines to setup db with some seed data defined inside `./data` dir or not
(optional, default `false`).

### Test

Finally we can test already configured and prepared PostgreSQL image
and trial it against 4 different cases

<!-- TODO - FIX this part? -->
```Earthfile
# Container runs PostgreSQL server, drops and initialise db, applies migrations, applies seed data.
test-1:
    FROM ./../../earthly/postgresql+postgres-base

    COPY ./../../earthly/utils+shell-assert/assert.sh .

    ENV INIT_AND_DROP_DB true
    ENV WITH_MIGRATIONS true
    ENV WITH_SEED_DATA true
    COPY ./docker-compose.yml .
    WITH DOCKER \
        --compose docker-compose.yml \
        --load example-db:latest=+build \
        --service example \
        --allow-privileged
        RUN sleep 5;\
            res=$(psql postgresql://example-dev:example-pass@0.0.0.0:5432/ExampleDb -c "SELECT * FROM users");\
            
            source assert.sh;\
            expected=$(printf "  name   | age \n---------+-----\n Alice   |  20\n Bob     |  30\n Charlie |  40\n(3 rows)");\
            assert_eq "$expected" "$res"
    END

# Container runs PostgreSQL server, drops and initialise db, doesn't apply migrations, doesn't apply seed data.
test-2:
    FROM ./../../earthly/postgresql+postgres-base

    ENV INIT_AND_DROP_DB true
    ENV WITH_MIGRATIONS false
    ENV WITH_SEED_DATA false
    COPY ./docker-compose.yml .
    WITH DOCKER \
        --compose docker-compose.yml \
        --load example-db:latest=+build \
        --service example \
        --allow-privileged
        RUN sleep 5;\
            ! psql postgresql://example-dev:example-pass@0.0.0.0:5432/ExampleDb -c "SELECT * FROM users"
    END

# Container runs PostgreSQL server, drops and initialise db, applies migrations, doesn't apply seed data.
test-3:
    FROM ./../../earthly/postgresql+postgres-base

    COPY ./../../earthly/utils+shell-assert/assert.sh .

    ENV INIT_AND_DROP_DB true
    ENV WITH_MIGRATIONS true
    ENV WITH_SEED_DATA false
    COPY ./docker-compose.yml .
    WITH DOCKER \
        --compose docker-compose.yml \
        --load example-db:latest=+build \
        --service example \
        --allow-privileged
        RUN sleep 5;\
            res=$(psql postgresql://example-dev:example-pass@0.0.0.0:5432/ExampleDb -c "SELECT * FROM users");\

            source assert.sh;\
            expected=$(printf " name | age \n------+-----\n(0 rows)");\
            assert_eq "$expected" "$res"
    END

# PostgreSQL server runs as a separate service, drops and initialise db, applies migrations, applies seed data.
test-4:
    FROM ./../../earthly/postgresql+postgres-base

    COPY ./../../earthly/utils+shell-assert/assert.sh .

    ENV DB_HOST postgres
    ENV INIT_AND_DROP_DB true
    ENV WITH_MIGRATIONS true
    ENV WITH_SEED_DATA true
    COPY ./docker-compose.yml .
    WITH DOCKER \
        --compose docker-compose.yml \
        --pull postgres:16 \
        --load example-db:latest=+build \
        --service example \
        --service postgres \
        --allow-privileged
        RUN sleep 5;\
            res=$(psql postgresql://postgres:postgres@0.0.0.0:5433/ExampleDb -c "SELECT * FROM users");\
            
            source assert.sh;\
            expected=$(printf "  name   | age \n---------+-----\n Alice   |  20\n Bob     |  30\n Charlie |  40\n(3 rows)");\
            assert_eq "$expected" "$res"
    END

# Invoke all tests
test:
    BUILD +test-1
    BUILD +test-2
    BUILD +test-3
    BUILD +test-4
```

It is a pretty standard way how to test builded image with the specified `docker-compose.yml` file,
which was mentioned below.
Notice that it is used basic `postgres-base` environment instead of `builder` as before,
because we dont need to have migrations and seed data as a part of the test environment itself.
With the help of `ENV` we are specifying
`DB_HOST`, `INIT_AND_DROP_DB`, `WITH_MIGRATIONS`, `WITH_SEED_DATA` environment variables for various test cases.

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
It is pretty strait forward for this builder process,
because as a part of `+build` target we already creating a docker image.

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/postgresql/Earthfile)
and any other files in the same directory.
This `Earthfile` will check the health of our source code, build and test PostgreSQL image,
and then finally release it to GitHub and publish it to one or more container registries.
At this point, please feel free to experiment more and run each target individually.
Once you're ready, you can copy this example and modify it for your specific context.
