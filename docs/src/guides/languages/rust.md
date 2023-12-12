---
icon: simple/rust
title: Rust
tags:
    - Rust
---

<!-- markdownlint-disable single-h1 -->
# :simple-rust: Rust
<!-- markdownlint-enable single-h1 -->

<!-- cspell: words USERARCH TARGETARCH toolsets fmtchk stdcfgs rustfmt nextest testci testdocs depgraph -->

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

    COPY --dir .cargo .config crates .
    COPY Cargo.lock Cargo.toml .
    COPY clippy.toml deny.toml rustfmt.toml .

    DO ./../../earthly/rust+SETUP
```

The first target `builder` is responsible for preparing an already configured Rust environment,
instal all needed tools and dependencies.

The fist step of the `builder` target is to prepare a Rust environment via `+rust-base` target.
Next step is to copy source code of the project.
Note that you need to copy only needed files for Rust build process,
any other irrelevant stuff should omitted.
And finally finalize the build with `+SETUP` UDC target.
The `+SETUP` UDC target requires `rust-toolchain.toml` file,
with the specified `channel` option in it.
This `rust-toolchain.toml` file could be specified
via the `toolchain` argument of the `+SETUP` target like this
with defining the specific location of this file with the specific name.
By default `toolchain` setup to `rust-toolchain.toml`.

### Running checks

```Earthfile
# Test rust build container - Use best architecture host tools.
hosted-check:
    FROM +builder

    DO ./../../earthly/rust+CHECK

# Test which runs check with all supported host tooling.  Needs qemu or rosetta to run.
# Only used to validate tooling is working across host toolsets.
all-hosts-check:    
    BUILD --platform=linux/amd64 --platform=linux/arm64 +hosted-check

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
        BUILD --platform=linux/arm64 +hosted-check
    ELSE
        BUILD --platform=linux/amd64 +hosted-check
    END
```

With prepared environment and all data, we're now ready to start operating with the source code and configuration files.
The `hosted-check` target which actually performs all checks and validation
with the help of `+CHECK` UDC target.
The `+CHECK` UDC target performs static checks of the Rust project as
`cargo fmt`, `cargo machete`, `cargo deny` which will validate formatting,
find unused dependencies and any supply chain issues with dependencies.
Here is the list of steps (look at `./earthly/rust/scripts/std_checks.sh`):

1. `cargo fmtchk` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Rust Code Format.
2. Checking configuration files for consistency.
3. `cargo machete` - Checking for Unused Dependencies.
4. `cargo deny check` - Checking for Supply Chain Issues.

As it was mentioned above it validates configuration files as
`.cargo/config.toml`, `rustfmt.toml`, `.config/nextest.toml`, `clippy.toml`, `deny.toml`
to be the same as defined in `earthly/rust/stdcfgs` directory of the `catalyst-ci` repo.
So when you are going to setup a new Rust project copy these configuration files
described above to the appropriate location of your Rust project.

Another targets as `all-hosts-check` and `check` (running on CI) just invoke `hosted-check`
with the specified `--platform`.
It is important to define a `linux` target platform with a proper cpu architecture
for the Rust project when you are building it inside Docker
and check the build process with different scenarios.
The same approach we will see for the another targets of this guide.

### Build

```Earthfile
# Build the service.
hosted-build:
    FROM +builder
 
    DO ./../../earthly/rust+BUILD --libs="bar" --bins="foo/foo"

    DO ./../../earthly/rust+SMOKE_TEST --bin="foo"

    SAVE ARTIFACT target/$TARGETARCH/doc doc
    SAVE ARTIFACT target/$TARGETARCH/release/foo foo

# Test which runs check with all supported host tooling.  Needs qemu or rosetta to run.
# Only used to validate tooling is working across host toolsets.
all-hosts-build:    
    BUILD --platform=linux/amd64 --platform=linux/arm64 +hosted-build

# Run build using the most efficient host tooling
# CI Automated Entry point.
build:
    FROM busybox
    # This is necessary to pick the correct architecture build to suit the native machine.
    # It primarily ensures that Darwin/Arm builds work as expected without needing x86 emulation.
    # All target implementation of this should follow this pattern.
    ARG USERARCH

    IF [ "$USERARCH" == "arm64" ]
        BUILD --platform=linux/arm64 +hosted-build
    ELSE
        BUILD --platform=linux/amd64 +hosted-build
    END
```

After successful performing checks of the Rust project we can finally build artifacts.
As it was discussed in the previous section, actual job is done with `hosted-build` target,
other targets needs to configure different platform running options.
So we will focus on `hosted-build` target.
Obviously it inherits `builder` target environment and than performs build of the binary.
Important to note that in this particular example we are dealing with the executable Rust project,
so it produces binary as a final artifact.
Another case of the building Rust library we will consider later.
Actual build process is done with `+BUILD` UDC target.
The `+BUILD` UDC have few arguments `libs` and `bins`,
they should be specified to properly generate `cargo-modules` docs (see description below).
The `libs` argument takes a list of library crate's names in your Rust project, e.g.
`--libs="crate1 crate2"`.
The `bins` argument takes a list of binary crate's names and binary names in your Rust project, e.g.
`--bins="crate1/bin1 crate1/bin2 crate2/bin1"`, note that each binary name correspond to each crate
and separated in this list with `/` symbol.
Under this build process we perform different steps of compiling and validating of our Rust project,
here is the list of steps (look at `./earthly/rust/scripts/std_build.sh`):

1. `cargo build` - Building all code in the workspace.
2. `cargo lint` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)
Checking all Clippy Lints in the workspace.
3. `cargo docs` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Documentation can be generated OK.
4. `cargo testci` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Self contained Unit tests all pass.
5. `cargo testdocs` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Documentation tests all pass.
6. `cargo bench` - Checking Benchmarks all run to completion.
7. `cargo depgraph` - Generating dependency graph based on the Rust code.
Generated artifacts are `doc/workspace.dot`, `doc/full.dot`, `doc/all.dot` files.
8. `cargo modules` - Generating modules trees and graphs based on the Rust code.
Generated artifacts are `doc/$crate.$bin.bin.modules.tree`, `doc/$crate.$bin.bin.modules.dot`
for the specified `--bins="crate1/bin1"` argument
and `target/doc/$crate.lib.modules.tree`, `target/doc/$crate.lib.modules.dot`
for the specified `--libs="crate1"` argument of the `+BUILD` UDC.

Next steps is mandatory if you are going to produce a binary as an artifact,
for Rust libraries the are not mandatory and could be omitted.
The `+SMOKE_TEST` UDC target checks that produced binary with the specified name (`--bin` argument)
is executable, isn't a busted mess.

Final step is to provide desired artifacts: docs and binary.

### Test

As you already mentioned that running of unit tests is done during the `build` process,
but if you need some integration tests pls follow how it is done for [PostgreSQL builder](./postgresql.md),
Rust will have the same approach.

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
It is pretty strait forward for this builder process,
because as a part of `+build` target we already creating a docker image.

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/rust/Earthfile)
and any other files in the same directory.
We have learnt how to maintain and setup Rust project, as you can see it is pretty simple.
