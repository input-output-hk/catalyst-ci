# PostgreSQL Earthly Build Containers and UDCs

<!-- cspell: words -->

This repo defines common PostgreSQL targets and UDCs.

## User Defined Commands

### BUILDER

This UDC prepares postgresSQL environment,
takes `entry.sh` and `setup-db.sql` added in the `postgres-base`.

### CHECK

This UDC runs lints for the sql files.

### FORMAT

This UDC runs lint's formatting sql files from the provided directory.
*NOTE* that it is necessary to build `postgres-base` image using `postgres-base-image` target:

```sh
earthly +postgres-base-image
```

### BUILD

This UDC builds postgresSQL image with all prepared migrations and seed data.

#### Invocation

In an `Earthfile` in your source repository add:

```Earthfile
builder:
    FROM +postgres-base

    WORKDIR /build

    COPY --dir ./example/migrations ./example/data ./example/refinery.toml .
    DO +BUILDER

check:
    FROM +builder

    DO +CHECK

format:
    LOCALLY

    DO +FORMAT --src=$(echo ${PWD})

build:
    FROM +builder

    DO +BUILD --image_name=example-db
```

An example `docker-compose` file you can find in `example/docker-compose.yml`.
Here it is important to note that this image have 4 possible options how to run:

* If `DB_HOST` env var established to `localhost`, container will run PostgreSQL server by itself,
otherwise will relies on remote PostgreSQL server connection.
* `INIT_AND_DROP_DB` env var defines to run initial initialization of the db with the clean state or not. (could be omitted)
* `WITH_MIGRATIONS` env var defines to run migrations defined inside `./migrations` dir or not.(could be omitted)
* `WITH_SEED_DATA` env var defines to setup db with some seed data defined inside `./data` dir or not.(could be omitted)
