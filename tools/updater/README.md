# updater

> A helper tool for updating CUE files, especially [Timoni] bundle files.

The `updater` CLI provides an interface for performing common deployment operations within Project Catalyst.
It has various subcommands centered around supporting GitOps operations by updating CUE files, especially [Timoni] bundle files.
It can be used in tandem with a CI/CD provider to easily update CUE configuration files within an existing repository.

## Usage

The `updater` CLI can be used in various workflows.
This section will provide high-level examples of the different workflows it can be used to support.

### Updating CUE files

By design, CUE files are intended to be immutable.
If a CUE file has a concrete value in a field, it's not possible to easily override it using the CUE CLI.
The `updater` CLI provides a subcommand for easily overriding concrete values within an existing CUE file.
This is especially important for supporting GitOps patterns.

Assuming we have an existing CUE file:

```cue
foo: {
    bar: 1
}
```

We can update the value of `bar` with:

```terminal
$ updater update file -f ./file.cue "foo.bar" "2"  # Pass --in-place to update the file in place
foo: {
    bar: 2
}
```

### Updating Timoni bundle files

A common GitOps flow is to update specific values within a [Timoni bundle file](https://timoni.sh/bundle/).
The `updater` CLI provides a specific subcommand for updating the `values` specified in a bundle.
Given the following bundle file:

```cue
bundle: {
    apiVersion: "v1alpha1"
    name:       "bundle"
    instances: {
        instance: {
            module: {
                url:     "oci://332405224602.dkr.ecr.eu-central-1.amazonaws.com/instance-deployment"
                version: "0.0.1"
            }
            namespace: "default"
            values: {
                server: image: tag: "v0.1.0"
            }
        }
    }
}
```

We can update the value of `server.image.tag` with:

```terminal
$ updater update bundle -f ./bundle.cue -i instance "server.image.tag" "v0.2.0"
# ...
            values: {
                server: image: tag: "v0.2.0"
            }
# ...
```

### Mass updating Timoni bundle files

The primary use of the `updater` CLI is for performing a mass update of Timoni bundle files.
This approach is quite opinionated and requires some additional context.

#### Deployment files

Much like Catalyst CI, the `updater` CLI assumes a mono-repo setup for applications.
Where Catalyst CI expects each application to contain an `Earthfile` describing how to build the application, the `updater` CLI
expects each application to contain a `deployment.yml` file describing how to update the application's associated deployment.
For example:

* `/app1`
  * `Earthfile`
  * `deployment.yml`
* `/app2`
  * `Earthfile`
  * `deployment.yml`

Each deployment file contains a set of override operations that instruct the `updater` CLI on which Timoni bundle files to update.
For example:

```yaml
overrides:
  - app: app1
    instance: app1  # Can be omitted if same as app
    path: server.image.tag
    value: v0.2.0
```

The exact purpose of each of these fields will become more clear later.

#### Deployment repository

The `updater` CLI assumes a mono-repo deployment repository exists containing Timoni bundle files for each environment.
An example structure would look like this:

* `/bundles`
  * `/dev`
    * `/app1`
      * `bundle.cue`
    * `/app2`
      * `bundle.cue`
  * `/staging`
    * `/app1`
      * `bundle.cue`

The root directory (`/bundles`) has subdirectories for each environment and each environment has subdirectories for every
application.
Each application in turn has a dedicated `bundle.cue` that contains the deployment code for the application.

#### Updating files

Given the previous example structure and deployment file, the `updater` CLI can automatically update the correct bundle file.
First, we will use the `scan` subcommand to automatically discover all `deployment.yml` files and parse their respective overrides:

```terminal
$ updater scan .
[{"app":"app1","instance":"app1","path":"server.image.tag","value":"v0.2.0"}]
```

This produces a JSON output containing a list of overrides.
The JSON output can be used stand-alone, however, it can also be passed directly to the `update deployments` subcommand:

```terminal
$ updater scan . | updater update deployments -e dev /path/to/deployment-repo/bundles
# Empty output
```

The above command performs the following for each given override:

* Constructs a path to the bundle file: `<root_path>/<environment>/<app>/bundle.cue`
* Constructs a path to override: `bundle.instances.<instance>.values.<value>`
* Overrides the constructed value path within the constructed file path with the override value

Using the previous examples, it would perform the following:

* Constructs a path to the bundle file: `/path/to/deployment-repo/bundles/dev/app1/bundle.cue`
* Constructs a path to override: `bundle.instances.app1.values.server.image.tag`
* Overrides the constructed value path with `v0.2.0`

This setup allows updating arbitrary bundle files and their respective values by defining a single `deployment.yml` file at the root
of a given application.
In a normal GitOps flow, the changes would then be committed to the deployment repository and picked up by a GitOps operator.

#### Templating

The previous example hardcoded an override value in the `deployment.yml`.
In some cases, the value is only known at runtime (i.e., when the CI/CD system is running).
For these cases, it's possible to override arbitrary "template" literals:

```yaml
overrides:
  - app: app1
    path: server.image.tag
    value: GIT_SHA
```

When the CI/CD is performing an update, it can pass the value for this template literal like so (assuming GitHub Actions):

```terminal
$ updater scan -t "GIT_SHA=${{ github.sha }}" . | updater update deployments -e dev /path/to/deployment-repo/bundles
# Empty output
```

Prior to updating the bundle files, the `updater` CLI will replace all occurrences of `GIT_SHA` with the current commit SHA.
This allows dynamically updating the image tag of the application deployment at runtime if you tag images using the commit SHA

[timoni]: https://timoni.sh/

### Signing Deployments

The `updater` CLI provides some basic functionality for signing and verifying messages using an RSA private/public key pair.
The primary use case for this functionality is for submitting "signed" PRs to a given deployment repository.
To fully understand the use case, some additional context is required.

#### GitOps Deployments

In a typical GitOps repository with branch-protection enabled, it's not possible to commit directly against the default branch.
This complicates the auto-deployment process as the CI/CD system has no automated way with which to apply updates to the repository.
It's possible to work around this limitation by having the CI/CD system submit a PR to the repository and then have that PR
automatically merged via automation in the GitOps repository.

However, this introduces a serious problem: how does the GitOps repository know which PRs to automatically merge and which to
ignore?
To provide security, it's possible to include a signed message within the body of the PR.
As long as the GitOps repository has the necessary public key, it can validate the signature in the PR body and "prove" that the PR
originated from a trusted system.
Furthermore, to prevent abuse, the CI/CD system signs the commit hash of the PR.
This prevents someone from just copying a prior signature and re-using it, as commit hashes are unique across commits.

With this in place, it's possible to verify a given PR is safe to automatically merge.
The CI/CD system submits the PR with the signed commit hash and the GitOps repository validates the signed commit hash prior to
merging the PR.

#### Setup

Prior to using the functionality, you must first establish an RSA private/public key pair.
This can be done using openssl:

```shell
# Generate the private key
openssl genpkey -algorithm RSA -out rsa_private.pem -pkeyopt rsa_keygen_bits:2048

# Extract the public key
openssl rsa -pubout -in rsa_private.pem -out rsa_public.pem
```

#### Sign and verify

To sign and verify a message:

```shell
# Sign the commit hash (assuming it's in $COMMIT_HASH)
SIG=$(updater signing sign -k rsa_private.pem "$COMMIT_HASH")

# Verify the commit hash (should produce: "Signature is valid")
updater signing verify -k rsa_public.pem "$COMMIT_HASH" "$SIG"
```