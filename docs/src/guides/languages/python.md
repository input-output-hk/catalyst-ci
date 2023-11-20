---
icon: simple/python
title: Python
tags: 
    - Python
---

<!-- markdownlint-disable single-h1 -->
# :simple-python: Python
<!-- markdownlint-enable single-h1 -->

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/python/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to work with Python based projects.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/python` to find a basic Python project, with the `Earthfile` in it.
This is the `Earthfile` we will be building in this guide.
You can choose to either delete the file and start from scratch,
or read the guide and follow along in the file.

## Building the Earthfile

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    The below sections will walk through building our `Earthfile` step-by-step.
    In each section, only the fragments of the `Earthfile` relative to that section are displayed.
    This means that, as you go through each section, you should be cumulatively building the `Earthfile`.
    If you get stuck at any point, you can always take a look at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/python/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Prepare base builder

```Earthfile
VERSION 0.7

builder:
    FROM ./../../earthly/python+python-base

    COPY --dir ./src .
    DO ./../../earthly/python+BUILDER
```

The first target `builder` is responsible to prepare an already configured Python environment,
instal all needed tools and dependencies.
Every Python project must be a [poetry](https://python-poetry.org) based project,
so it is mandatory to have `pyproject.toml` file in the root dir of the project.

The fist step of the `builder` target is prepare a Python environment
with poetry via `+python-base` target.
Next step is to copy source code of the project and finally finalize the build
with some poetry project setup which is done with `+BUILDER` UDC target.

### Running checks

[TODO](https://github.com/input-output-hk/catalyst-ci/issues/98)

### Test

```Earthfile
test:
    FROM +builder

    RUN poetry run pytest
```

As the final step, after proper setup of the Python project we can run tests,
to do so
inherit from the already discussed `+builder` target and just run `poetry run pytest`
or with any other way which are suitable for your project setup.
And that's it!

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
The only things you need is too define `release` and `publish` Earthly targets
with the proper configuration of the artifacts for your project.

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/python/Earthfile)
and any other files in the same directory.
We have learnt how to maintain and setup Python project, as you can see it is pretty simple.