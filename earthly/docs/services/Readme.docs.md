# Documentation Service Definitions

<!-- cspell: words livedocs sitedocs -->

## Live Documentation

To build documentation live, from the root of the repo run:

```sh
docker compose up -f local/docker-compose.livedocs.yml up
```

Go to [Live documentation](http://localhost:10080) to view live docs.

## Inspect built static site documentation

```sh
docker compose up -f local/docker-compose.sitedocs.yml up --abort-on-container-exit
```

## Earthly Integration

Add targets like the following to the root Earthly file of the project.

```Earthly
live-docs-development:
    LOCALLY
    # Build Container we need to serve live docs.
    BUILD ./docs+mkdocs-material

    # We use python to open a browser on Windows/Mac or Linux
    RUN python -c "import webbrowser; webbrowser.open('http://localhost:10080')"
    # Run the containers we need and serve live docs.
    RUN docker compose -f local/docker-compose.livedocs.yml up --abort-on-container-exit

site-docs-development:
    LOCALLY
    BUILD ./docs/+build

    # We use python to open a browser on Windows/Mac or Linux
    RUN python -c "import webbrowser; webbrowser.open('http://localhost:10081')"
    # Run the containers we need and serve site built docs.
    RUN docker compose -f local/docker-compose.sitedocs.yml up --abort-on-container-exit
```
