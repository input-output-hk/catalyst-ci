     _       ____   _____   ___    ___    _   _           ____     ___     ____   ____
    / \     / ___| |_   _| |_ _|  / _ \  | \ | |         |  _ \   / _ \   / ___| / ___|

/ \_ \ | | | | | | | | | | | \| | **\_** | | | | | | | | | | \_** \ / \_** \ |
|**_ | | | | | |_| | | |\ | |\_\_\_**| | |_| | | |_| | | |**\_ \_**) | /\_/ \_\
\_**_| |_| |\_**| \_**/ |\_| \_| |\_\_**/ \_**/ \_\_**| |\_\_\_\_/

## Description

Publishes the given Docker containers.

## Inputs

| parameter         | description                                                     | required | default |
| ----------------- | --------------------------------------------------------------- | -------- | ------- |
| earthfile         | Path to the Earthfile (excluding /Earthfile suffix) to build    | `true`   |         |
| earthly_satellite | The address of the remote Earthly satellite to use              | `true`   |         |
| images            | A space seperated list of images the Earthfile will produce     | `true`   |         |
| registry          | The registry to publish containers images to                    | `true`   |         |
| tags              | A space seperated list of tags to tag the resulting images with | `false`  |         |
| target            | The target to build for the given Earthfile                     | `true`   |         |

## Runs

This action is a `composite` action.
