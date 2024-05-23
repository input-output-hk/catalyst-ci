---
icon: simple/flutter
title: Flutter
tags:
    - Flutter
    - Dart
---

<!-- markdownlint-disable single-h1 -->
# :simple-flutter: Flutter
<!-- markdownlint-enable single-h1 -->

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/flutter/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build Go-based projects.
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI to build,
release, and publish our Flutter app.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/flutter` to find a very basic Flutter program.
This folder already has an `Earthfile` in it.
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
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/flutter/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Prepare base builder

The first target `builder` is responsible for preparing configured Flutter environments,
and install all needed tools and dependencies.

```Earthfile
VERSION 0.8

IMPORT github.com/input-output-hk/catalyst-ci/earthly/flutter:3.0.3 AS flutter-ci

# Set up the CI environment for Flutter app.
builder:
    DO flutter-ci+SETUP
```

### Running Bootstrap

In case your project use [Melos](https://melos.invertase.dev/~melos-latest)
for monorepo management, you can configure the `bootstrap` target
to call BOOTSTRAP function.

```Earthfile
bootstrap:
    FROM +builder

    DO flutter-ci+BOOTSTRAP
```

### Running analyze

The next step we run `analyze` target, which will run `flutter analyze` or
`melos analyze` command.

```Earthfile
analyze:
    FROM +builder

    DO flutter-ci+ANALYZE
```

### Running format

After that we check if the code format is correct.

```Earthfile
format:
    FROM +builder

    DO flutter-ci+FORMAT
```

### Running Unit Tests

In case you have unit tests in your project, you can run them with `unit-tests` target.

```Earthfile
unit-tests:
    FROM +builder

    DO flutter-ci+UNIT_TEST
```

### Build FLutter app for Web

An finally we build the Flutter app for Web (atm the only supported platform by Catalyst).

```Earthfile
build-web:
    FROM +builder

    ARG --required WORKDIR
    ARG --required TARGET

    DO flutter-ci+BUILD_WEB --WORKDIR=$WORKDIR --TARGET=$TARGET
```

You can run it like this:

```sh
earthly +build-web --WORKDIR=path/to/flutter/app/ --TARGET=lib/main.dart
```

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
It is pretty strait forward for this builder process,
because as a part of `+build` target we already creating a docker image.

## Conclusion

You can see the final `Earthfile`
[here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/flutter/Earthfile)
and any other files in the same directory.
We have learnt how to maintain and setup Rust project,
as you can see it is pretty simple.
