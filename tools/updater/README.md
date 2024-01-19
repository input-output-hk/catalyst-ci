# updater

> A helper tool for modifying CUE files to override arbitrary values.
> Useful for updating Timoni bundles.

The `updater` CLI provides an interface for overriding existing concrete values in a given CUE file.
Normally, concrete values in CUE files are immutable and thus not possible to override using the CUE CLI.
However, in some cases, it may be desirable to override an existing concrete value.
This is especially true in GitOps scenarios where a source of truth needs to be updated.

## Usage

The `updater` CLI is most commonly used to update Timoni bundle image tags.
Assuming you have a `bundle.cue` file like this:

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
                server: image: tag: "ed2951cf049e779bba8d97413653bb06d4c28144"
            }
        }
    }
}
```

You can update the value of `server.image.tag` like so:

```shell
updater -b bundle.cue "bundle.instances.instance.values.server.image.tag" "0fe74bf77739a3ef78de5fcc81c5c7a8dcae6199"
```

The `updater` CLI will overwrite the image tag with the provided one and update the `bundle.cue` file in place.
Note that the CLI uses the CUE API underneath the hood which may format the existing CUE syntax slightly differently.
In some cases, the resulting syntax might be a bit unsightly, so it's recommended to run `cue fmt` on the file after processing.
