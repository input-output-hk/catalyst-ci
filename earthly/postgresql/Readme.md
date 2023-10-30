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
