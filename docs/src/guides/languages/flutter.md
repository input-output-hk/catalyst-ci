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
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI to build, release, and publish our Go program.

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

TODO: