# jorm-metrics-server

> A small Prometheus exporter for aggregating Jormungandr metrics

This service scrapes the Jormungandr node API on a routine basis and exposes useful metrics in the Prometheus format.
Once pointed at a node, it will expose a predetermined list of Prometheus metrics at `/metrics`.

## Usage

Build the container:

```terminal
earthly +publish
```

Point it at the root address of a Jormungandr node and run it:

```terminal
docker run -p 8080:8080 -e API_URL="https://core.projectcatalyst.io" jorm-metrics-server
```

The metrics will be exposed at `http://localhost:8080/metrics`.

## Configuration

The service can be configured with the following environment variables:

| Name                | Description                                                                     | Required | Default   |
| ------------------- | ------------------------------------------------------------------------------- | -------- | --------- |
| `API_URL`           | The root address of the Jormungandr node to scrape                              | Yes      | N/A       |
| `ADDRESS`           | The address the metrics server should listen on                                 | No       | `0.0.0.0` |
| `PORT`              | The port the metrics server should listen on                                    | No       | `8080`    |
| `INTERVAL`          | The interval at which the service will scrape the Jormungandr node (in seconds) | No       | `60`      |
| `DISABLE_JSON_LOGS` | Disable JSON log output                                                         | No       | `false`   |

## Metrics

The following metrics are currently exposed:

| Name                | Description                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| `num_unique_voters` | The number of unique voters that have cast at least one vote on the node |