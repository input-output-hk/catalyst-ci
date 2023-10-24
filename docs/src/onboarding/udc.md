# UDCs

## Overview

The Catalyst CI repository provides a number of Earthly [User Defined Commands](https://docs.earthly.dev/docs/guides/udc) (UDCs).
You can think of a UDC as a reusable snippet of Earthly code that serves the same purpose as functions in a common programming
language.
UDCs are helpful for several reasons:

1. They keep Earthfiles DRY
2. They can encapsulate complex logic into a simple contractual interface
3. They enforce standardization and prevent solving the same problem in multiple different ways

The third reason is particularly useful for Catalyst as we have multiple repositories with dozens of Earthfiles often solving similar
problems.

## Usage

You are highly encouraged to review the currently available UDCs in the
[Catalyst CI repository](https://github.com/input-output-hk/catalyst-ci/tree/master/earthly).
The folder structure is broken out by language/technology and should be relatively easy to navigate.
You can incorporate these UDCs into your Earthfiles by using something like below:

```Earthfile
DO github.com/input-output-hk/catalyst-ci/earthly/<folder>+<UDC_NAME> --arg1=value1
```

Replacing `folder` and `UDC_NAME` respectively.
The passing of an argument is optional, as some UDCs do not require any input arguments.

## Contributing

Please feel encouraged to contribute UDCs to the repository.
If you're seeing the same logic being re-used across multiple Earthfiles in a repository, this is a good candidate for refactoring
into a UDC.
Additionally, for SMEs who are aware of language best practices, encoding those into a UDC will help increase the overall health of
the CI process.
