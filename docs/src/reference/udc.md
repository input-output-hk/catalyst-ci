# Functions

## Overview

The Catalyst CI repository provides a number of Earthly  
[Functions](https://docs.earthly.dev/docs/guides/functions).
You can think of a Function as a reusable snippet of Earthly code that serves the same purpose as functions in a common programming
language.
Functions are helpful for several reasons:

1. They keep Earthfiles DRY
2. They can encapsulate complex logic into a simple contractual interface
3. They enforce standardization and prevent solving the same problem in multiple different ways

The third reason is particularly useful for Catalyst as we have multiple repositories with dozens of Earthfiles often solving
similar problems.

## Usage

You are highly encouraged to review the currently available Functions in the
[Catalyst CI repository](https://github.com/input-output-hk/catalyst-ci/tree/master/earthly).
The folder structure is broken out by language/technology and should be relatively easy to navigate.
You can incorporate these Functions into your Earthfiles by using something like below:

```Earthfile
DO github.com/input-output-hk/catalyst-ci/earthly/<folder>+<Function_NAME> --arg1=value1
```

Replacing `folder` and `Function_NAME` respectively.
The passing of an argument is optional, as some Functions do not require any input arguments.

## Contributing

Please feel encouraged to contribute Functions to the repository.  
If you're seeing the same logic being re-used across multiple Earthfiles in a  
repository, this is a good candidate for refactoring into a Function.  
Additionally, for SMEs who are aware of language best practices, encoding those 
into a Function will help increase the overall health ofthe CI process.
