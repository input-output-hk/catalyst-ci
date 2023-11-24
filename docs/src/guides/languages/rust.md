---
icon: simple/rust
title: Rust
tags:
    - Rust
---

<!-- markdownlint-disable single-h1 -->
# :simple-rust: Rust
<!-- markdownlint-enable single-h1 -->

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/rust/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to work with Rust based projects.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/rust` to find a basic Rust project, with the `Earthfile` in it.
This is the `Earthfile` we will be building in this guide.
You can choose to either delete the file and start from scratch,
or read the guide and follow along in the file.

Also we will take a look how we are setup Rust projects and what configuration is used.

## Building the Earthfile

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    The below sections will walk through building our `Earthfile` step-by-step.
    In each section, only the fragments of the `Earthfile` relative to that section are displayed.
    This means that, as you go through each section, you should be cumulatively building the `Earthfile`.
    If you get stuck at any point, you can always take a look at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/rust/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Prepare base builder


```Earthfile
VERSION 0.7

# Set up our target toolchains, and copy our files.
builder:
    FROM ./../../earthly/rust+rust-base
    
    COPY --dir "*" .
    DO ./../../earthly/rust+SETUP
```

The first target `builder` is responsible for preparing an already configured Rust environment,
instal all needed tools and dependencies.

The fist step of the `builder` target is to prepare a Rust environment via `+rust-base` target.
Next step is to copy source code of the project and finally finalize the build
which is done with `+SETUP` UDC target.
The `+SETUP` UDC target requires to have a `rust-toolchain.toml` file,
with the specified `channel` option in it.

### Running checks

```Earthfile
# Test rust build container - Use best architecture host tools.
check-hosted:
    FROM +builder

    DO ./../../earthly/rust+CHECK

# Test which runs check with all supported host tooling.  Needs qemu or rosetta to run.
# Only used to validate tooling is working across host toolsets.
check-all-hosts:    
    BUILD --platform=linux/amd64 --platform=linux/arm64 +check-hosted

## Standard CI targets.
##
## These targets are discovered and executed automatically by CI.

# Run check using the most efficient host tooling
# CI Automated Entry point.
check:
    FROM busybox
    # This is necessary to pick the correct architecture build to suit the native machine.
    # It primarily ensures that Darwin/Arm builds work as expected without needing x86 emulation.
    # All target implementation of this should follow this pattern.
    ARG USERARCH

    IF [ "$USERARCH" == "arm64" ]
        BUILD --platform=linux/arm64 +check-hosted
    ELSE
        BUILD --platform=linux/amd64 +check-hosted
    END
```

With prepared environment and all data, we're now ready to start operating with the source code and configuration files.
The `check-hosted` target which actually performs all checks and validation
with the help of `+CHECK` UDC target.
The `+CHECK` UDC target performs static checks of the Rust project as `cargo fmt`, `cargo machete`, `cargo deny` which will validate formatting, find unused dependencies and any supply chain issues with dependencies.
Also during it validates configuration files as `.cargo/config.toml`, `rustfmt.toml`, `.config/nextest.toml`, `clippy.toml`, `deny.toml`
to be the same as defined in `earthly/rust/stdcfgs` directory of the `catalyst-ci` repo.

Another targets as `check-all-hosts` and `check` (running on CI) just invoke `check-hosted`
with the specified `--platform`.
It is important to define a `linux` target platform with a proper cpu architecture
for the Rust project when you are building it inside Docker
and check the build process with different scenarios.
The same approach we will see for the another targets of this guide.