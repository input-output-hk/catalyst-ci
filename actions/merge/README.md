# merge

> Merges new deployments into an existing GitOps structure

This Github Action essentially merges a map of image names to their respective tags into an existing map, overwriting values where
required.
It's intended to automate a GitOps repository where images are deployed from a central file.

## Usage

```yaml
- name: Merge hashes
  uses: input-output-hk/catalyst-ci/actions/merge@fdcDeprecation
  with:
    hash_file: "/path/to/existing/hashes.json"
    images: |
        image1
        image2
    tag: my_tag
```

In the above example, the following JSON format would be generated:

```json
{
  "image1": "my_tag",
  "image2": "my_tag
}
```

This would then be merged, and possibly overwrite, the JSON structure present
in the `hash_file` input. **Note that this process is destructive**.

## Setup

This action has limited usefulness for consumers who are not using the opinionated approach of using GitOps to control service
deployments.
It assumes you have a single "hashes" file per environment that is the source of truth for what images are currently deployed.
When new images are created, for example as part of a CI pipeline, this action can automatically update this "hashes" file with the
newly generated tag.

## Inputs

| Name      | Description                                                              | Required | Default             |
| --------- | ------------------------------------------------------------------------ | -------- | ------------------- |
| hash_file | The relative path to the hash file to update with deployment information | Yes      | N/A                 |
| images    | A newline separated list of images to deploy                             | Yes      | N/A                 |
| tag       | The image tag to deploy                                                  | No       | `${{ github.sha }}` |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
