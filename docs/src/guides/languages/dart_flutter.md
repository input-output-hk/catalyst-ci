---
icon: simple/flutter
title: Flutter/Dart
tags:
    - Flutter
    - Dart
---

<!-- markdownlint-disable single-h1 -->
# :simple-flutter: Flutter / :simple-dart: Dart
<!-- markdownlint-enable single-h1 -->

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/dart/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build Go-based projects.
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI to build, release, and publish our Go program.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/go` to find a very basic Go program which prints "Hello, world!" to the terminal screen using `cowsay`.
This folder already has an `Earthfile` in it.
This is the `Earthfile` we will be building in this guide.
You can choose to either delete the file and start from scratch, or read the guide and follow along in the file.

## TODO

* [ ] [Builders](https://github.com/input-output-hk/catalyst-ci/issues/83)
