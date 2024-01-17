# push

> Tags and pushes an image to the given registries

This Github Action will attach a variable number of tags to a given image and then push all variants to a list of image registries.
This is often useful when a single image needs to be tagged multiple times and pushed to multiple registries.
Note that for the `registries` input, empty lines will be ignored.
As a result, you can pass template variables that may or may not be empty (useful for handling optional registries).

To see a full demonstration of this action, see the [publish workflow](../../.github/workflows/publish.yml).

## Usage

```yaml
- name: Push image
  uses: input-output-hk/catalyst-ci/actions/push@master
  with:
      image: my_image:latest
      registries: |
        registry1
        registry2
      tags:
        tag1
        tag2
```

## Inputs

| Name       | Description                                            | Required | Default |
| ---------- | ------------------------------------------------------ | -------- | ------- |
| image      | The full name of the image to tag and push (image:tag) | Yes      | N/A     |
| registries | A line separated list of registries to push to         | Yes      | N/A     |
| tags       | A line separated list of tags to tag the image with    | Yes      | N/A     |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
