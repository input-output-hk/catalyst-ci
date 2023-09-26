# Documentation Service Definitions

<!-- cspell: words livedocs sitedocs -->

## Live Documentation

To build documentation live, from the root of the repo run:

```sh
docker compose up -f local/docker-compose.livedocs.yml up --abort-on-container-exit
```

Go to [Live documentation](http://localhost:10080) to view live docs.

## Inspect built static site documentation

```sh
docker compose up -f local/docker-compose.sitedocs.yml up
```
