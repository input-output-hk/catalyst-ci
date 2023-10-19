# run

> Runs an Earthly target

This Github Action will run a given target from a given Earthfile.
It takes a number of inputs which can augment the way in which the Earthly CLI is being called.
Notably, the action will automatically parse any produced artifacts or images from the target and return them as an action output.

To see a full demonstration of this action, see the [release workflow](../../.github/workflows/release.yml).

## Usage

```yaml
- name: Build
  uses: input-output-hk/catalyst-ci/actions/run@master
  with:
    earthfile: ./project
    target: build
    runner_address: tcp://myrunner:8372
```

## Inputs

| Name           | Description                                                            | Required | Default   |
| -------------- | ---------------------------------------------------------------------- | -------- | --------- |
| artifact       | If true, forces artifacts to be saved locally                          | No       | `"false"` |
| artifact_path  | The path (relative to earthfile) where artifacts will be placed        | No       | `out`     |
| earthfile      | The path to the Earthfile containing the target to ru                  | True     | N/A       |
| flags          | Additional flags to pass to the Earthly CLI                            | No       | `""`      |
| platform       | The platform to execute the earthfile target with (defaults to native) | No       | `""`      |
| runner_address | The address of the remote runner to use                                | No       | `""`      |
| runner_port    | The port to use for connecting to the remote runner                    | No       | `""`      |
| target         | The name of the target to run                                          | No       | `""`      |
| target_flags   | Additional flags to pass to the target                                 | No       | `""`      |

## Outputs

| Name     | Description                                           |
| -------- | ----------------------------------------------------- |
| artifact | The path to the artifact produced by the target       |
| image    | The name and tag of the imaged produced by the target |

## Testing

All tests can be run using Earthly.

```bash
earthly +check
```
