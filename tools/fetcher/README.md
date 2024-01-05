# fetcher

> A simple CLI for fetching Jormungandr archives and artifacts

The `fetcher` CLI provides a simple interface for fetching Jormungandr archives and artifacts from a configured object store.
By default, it uses AWS S3.
The primary use of this CLI is in CI pipelines or container entrypoint scripts where archives or artifacts are needed.
By specifying the appropriate identification parameters, the CLI will automatically download the respective files from an object
store.

## Usage

The CLI uses cloud SDKs (like AWS) for authentication.
It assumes you've configured the appropriate credentials in your environment to authenticate with the cloud provider.

### Artifacts

To fetch a specific Jormungandr genesis file:

```shell
# Fetch v1.0.0 of the genesis file from the fund10 dev environment
fetcher --bucket "artifacts-bucket" artifact -e "dev" -f "fund10" -t "genesis" -v "1.0.0" ./block0.bin
```

To fetch a specific vit-ss database file:

```shell
# Fetch v1.0.0 of the vit-ss database from the fund10 dev environment
fetcher --bucket "artifacts-bucket" artifact -e "dev" -f "fund10" -t "vit" -v "1.0.0" ./block0.bin
```

In either case, you can omit the version (`-v`) flag and the CLI will download the "default" (unversioned) artifact.
This is offered to support backwards compatability when using unversioned artifacts.

### Archives

To fetch a specific Jormungandr archive:

```shell
# Fetches an archive with the ID of f41c4470-03dd-4d3f-a325-6f784259b9c5
fetcher --bucket "archives-bucket" archive -e "dev" -i "f41c4470-03dd-4d3f-a325-6f784259b9c5" ./artifact.tar.zstd
```

Artifact IDs can be found using the archiver API (i.e., [the dev API](https://archiver.dev.projectcatalyst.io/api/v1/archives/)).
