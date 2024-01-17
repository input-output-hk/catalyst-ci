# discover

> Discover Earthfiles in a repository

This Github Action will recursively scan a repository and return a list of the locations of all discovered Earthfiles.
The scan can be further refined by specifying a target that must be included in scanned Earthfiles.
This allows finding a specific target across an entire repository.

To see a full demonstration of this action, see the [publish workflow](../../.github/workflows/publish.yml).

## Usage

```yaml
discover:
  runs-on: ubuntu-latest
  outputs:
      # The output is a JSON list of fully qualified paths to Earthfiles
      json: ${{ steps.discover.outputs.json }
  steps:
    - name: Install CLI
      uses: input-output-hk/catalyst-ci/actions/install@UDCmigration
    # We discover all Earthfiles that contain a target named "target"
    - name: Discover Earthly files
      uses: input-output-hk/catalyst-ci/actions/discover@UDCmigration
      id: discover
      with:
        targets: target  # You can list more than one target here

build:
  runs-on: ubuntu-latest
  needs: [discover]
  if: needs.discover.outputs.json != '[]'
  strategy:
    fail-fast: false
    matrix:
      # Feed the JSON into a matrix, each run will reference a single Earthfile
      earthfile: ${{ fromJson(needs.discover.outputs.json) }}
  steps:
    # Run the target named "target" from the current Earthfile
    - name: Build
      run: earthly ${{ matrix.earthfile }}+target
```

## Setup

This action assumes the [CLI](../../cli) provided by this repository has been downloaded and is accessible via `$PATH`.
You can use the [install action](../install/) to automate this process.

## Inputs

| Name         | Description                                                       | Required | Default   |
| ------------ | ----------------------------------------------------------------- | -------- | --------- |
| parse_images | Whether the image names from the given targets should be returned | No       | `"false"` |
| paths        | A space separated list of paths to search                         | No       | `.`       |
| targets      | A space separated list of targets to filter against               | No       | `""`      |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
