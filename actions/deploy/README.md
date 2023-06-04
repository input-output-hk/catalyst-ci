     _       ____   _____   ___    ___    _   _           ____     ___     ____   ____
    / \     / ___| |_   _| |_ _|  / _ \  | \ | |         |  _ \   / _ \   / ___| / ___|

/ \_ \ | | | | | | | | | | | \| | **\_** | | | | | | | | | | \_** \ / \_** \ |
|**_ | | | | | |_| | | |\ | |\_\_\_**| | |_| | | |_| | | |**\_ \_**) | /\_/ \_\
\_**_| |_| |\_**| \_**/ |\_| \_| |\_\_**/ \_**/ \_\_**| |\_\_\_\_/

## Description

Deploys the published images to the remote cluster.

## Inputs

| parameter       | description                       | required | default |
| --------------- | --------------------------------- | -------- | ------- |
| discover_output | The output from the discover step | `true`   |         |
| tag             | The image tag to deploy           | `true`   |         |

## Runs

This action is a `composite` action.
