     _       ____   _____   ___    ___    _   _           ____     ___     ____   ____
    / \     / ___| |_   _| |_ _|  / _ \  | \ | |         |  _ \   / _ \   / ___| / ___|

/ \_ \ | | | | | | | | | | | \| | **\_** | | | | | | | | | | \_** \ / \_** \ |
|**_ | | | | | |_| | | |\ | |\_\_\_**| | |_| | | |_| | | |**\_ \_**) | /\_/ \_\
\_**_| |_| |\_**| \_**/ |\_| \_| |\_\_**/ \_**/ \_\_**| |\_\_\_\_/

## Description

Discovers Earthfiles in the given paths and compiles data about them.

## Inputs

| parameter    | description                                                                                     | required | default |
| ------------ | ----------------------------------------------------------------------------------------------- | -------- | ------- |
| parse_images | Whether the image names from the given targets should be returnd (requires at least one target) | `false`  | false   |
| paths        | A space separated list of paths to search                                                       | `false`  | .       |
| targets      | A space seperated list of targets to filter against                                             | `false`  |         |

## Outputs

| parameter | description                                                    |
| --------- | -------------------------------------------------------------- |
| json      | JSON object containing information about discovered Earthfiles |

## Runs

This action is a `composite` action.
