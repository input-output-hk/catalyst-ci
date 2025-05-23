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

This guide will get you started with using the Catalyst CI to build Flutter-based projects.
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
    COPY --dir . .
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

### Build Flutter app for Web

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

### Running checks

In addition to setting up a Flutter-based project, it is highly recommended to run a check to
ensure the project is clean and well-defined.
The example below illustrates how to implement a
[license_checker](https://pub.dev/packages/license_checker), allowing you to configure the
licenses of dependencies to permit, reject, or approve using the license_checker package.
This configuration can be managed through a `YAML` configuration file.

```Earthfile
check-license:
    FROM flutter-ci+license-checker-base

    COPY . .
    DO flutter-ci+LICENSE_CHECK --license_checker_file=license_checker.yaml
```

To prevent the unintended approval of a package, a template `license_checker.yaml`
is included within the `earthly/flutter/Earthfile`.
This template will be compared with the provided `YAML` file
specified by the `--license_checker_file` argument.
If the files do not match, the program will return an error.

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
It is pretty strait forward for this builder process,
because as a part of `+build` target we already creating a docker image.

## Enhancing Flutter

### Integrating Flutter with Rust using `flutter_rust_bridge`

The `flutter_rust_bridge` allows you to integrate Rust with Flutter app, while maintaining the rest of the app in
Dart.
This can be useful for situations where you need to run complex algorithms, handle data
processing, or interact with low-level system APIs, but still want to leverage the Flutter ecosystem
for UI and app management.

Start by creating a new builder where all the necessary setup is done under the `flutter_rust_bridge+builder`,
then copy the Flutter project that already have `flutter_rust_bridge` setup.
Refer to <https://cjycode.com/flutter_rust_bridge/> for how to setup the project.

```Earthfile
builder-frb:
    FROM flutter_rust_bridge+builder
    COPY . .
```

Then generate a binding between Rust and Flutter

```Earthfile
# Generated necessary files for running Flutter web locally and save it locally.
code-generator-web:
    FROM +builder-frb
    DO flutter_rust_bridge+CODE_GENERATOR_WEB

    SAVE ARTIFACT ./assets/js AS LOCAL ./assets/js
    SAVE ARTIFACT ./rust/src/frb_generated.rs AS LOCAL ./rust/src/frb_generated.rs
    SAVE ARTIFACT ./lib/src AS LOCAL ./lib/src
```

## Conclusion

You can see the final `Earthfile`
[here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/flutter/Earthfile)
and any other files in the same directory.
We have learnt how to maintain and setup Rust project,
as you can see it is pretty simple.
