# PostgreSQL Earthly Build Containers and UDCs

<!-- cspell: words -->

This repo defines common PostgreSQL targets and UDCs.

## User Defined Commands

### BUILDER

This UDC prepares postgresSQL environment,
takes `entry.sh` and `setup-db.sql` added in the `postgres-base`.

### BUILD

This UDC builds postgresSQL image with all prepared migrations and seed data.

#### Invocation

In an `Earthfile` in your source repository add:

```Earthfile
builder:
    FROM +postgres-base

    WORKDIR /build

    COPY --dir example/migrations example/data example/refinery.toml
    DO +BUILDER

build:
    FROM +builder

    DO +CHECK
    DO +BUILD --image_name=example-db
```

An example `docker-compose` file you can find in `example/docker-compose.yml`.
Here it is important to note that this image have 4 possible options how to run:

* If `DB_HOST` env var established to `localhost`, container will run PostgreSQL server by itself,
otherwise will relies on remote PostgreSQL server connection.
* `INIT_AND_DROP_DB` env var defines to run initial initialization of the db with the clean state or not. (could be omitted)
* `WITH_MIGRATIONS` env var defines to run migrations defined inside `./migrations` dir or not.(could be omitted)
* `WITH_SEED_DATA` env var defines to setup db with some seed data defined inside `./data` dir or not.(could be omitted)
