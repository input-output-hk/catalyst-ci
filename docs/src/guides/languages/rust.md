---
icon: simple/rust
title: Rust
tags:
    - Rust
---

<!-- markdownlint-disable single-h1 -->
# :simple-rust: Rust
<!-- markdownlint-enable single-h1 -->

<!-- cspell: words toolsets stdcfgs depgraph -->

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
VERSION 0.8

IMPORT ./../../earthly/rust AS rust-ci

# Set up our target toolchains, and copy our files.
builder:
    DO rust-ci+SETUP

    COPY --dir .cargo .config crates .
    COPY Cargo.toml .
```

The first target `builder` is responsible for preparing configured Rust environments and,
install all needed tools and dependencies.

#### Builder steps

1. First step of `builder` target is to prepare a Rust environment via `+installer` target,
which is called in `SETUP` FUNCTION.
The `installer` target installs necessary tools for `+rust-base` target and copies
common scripts and standardizecd Rust configs.
The `rust-base` provides a base Rustup build environment.
  It installs necessary
packages, including development libraries and tools.
Clippy linter, LLVM tools for generating code coverage, and nightly toolchain are installed.
2. Next step is to copy source code of the project.
Note that you need to copy only needed files for Rust build process,
any other irrelevant stuff should omitted.
3. And finally finalize the build with `+SETUP` FUNCTION.
The `+SETUP` FUNCTION requires `rust-toolchain.toml` file,
with the specified `channel` option in it.
This `rust-toolchain.toml` file could be specified
via the `toolchain` argument of the `+SETUP` target like this
with defining the specific location of this file with the specific name.
By default `toolchain` setup to `rust-toolchain.toml`.

### Running checks

```Earthfile
# Run check using the most efficient host tooling
# CI Automated Entry point.
check:
    FROM +builder

    DO rust-ci+EXECUTE --cmd="/scripts/std_checks.py"

# Test which runs check with all supported host tooling.  Needs qemu or rosetta to run.
# Only used to validate tooling is working across host toolsets.
all-hosts-check:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +check
```

With prepared environment and all data, we're now ready to start operating with the source code and configuration files.
The `check` target performs all checks and validation procedures
using the help of `std_checks.py` script.
This script performs static checks of the Rust project as
`cargo fmt`, `cargo machete`, `cargo deny` which will validate formatting,
find unused dependencies and any supply chain issues with dependencies.
Here is the list of steps (look at `./earthly/rust/scripts/std_checks.py`):

1. `cargo fmtchk` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/cargo_config.toml`)Checking Rust Code Format.
2. Checking configuration files for consistency.
3. `cargo machete` - Checking for Unused Dependencies.
4. `cargo deny check` - Checking for Supply Chain Issues.

As it was mentioned above, it validates configuration files as
`.cargo/config.toml`, `rustfmt.toml`, `.config/nextest.toml`, `clippy.toml`, `deny.toml`
to be the same as defined in `earthly/rust/stdcfgs` directory of the `catalyst-ci` repo.
So when you are going to setup a new Rust project, copy these configuration files
described above to the appropriate location of your Rust project.

Another target as `all-hosts-check` just invokes `check` with the specified `--platform`.
It is needed for the local development to double check that everything works for different platforms.
It is important to define a `linux` target platform with a proper CPU architecture
for the Rust project when you are building it inside Docker
and check the build process with different scenarios.
The same approach will be seen in other targets throughout this guide.

### Build

```Earthfile
# Run build using the most efficient host tooling
# CI Automated Entry point.
build:
    FROM +builder

    # This WILL save the junit and coverage reports even if it fails.
    DO rust-ci+EXECUTE \
        --cmd="/scripts/std_build.py --cov_report=$HOME/coverage-report.info --libs=bar --bins=foo/foo" \
        --junit="example.junit-report.xml" \
        --coverage="example.coverage-report.info" \
        --output="release/[^\./]+" \
        --docs="true"

    SAVE ARTIFACT target/release/foo foo

# Test which runs check with all supported host tooling.  Needs qemu or rosetta to run.
# Only used to validate tooling is working across host toolsets.
all-hosts-build:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +build
```

After successful performing checks of the Rust project we can finally `build` artifacts.
Obviously it inherits `builder` target environment and then performs build of the binary.
Important to note that in this particular example we are dealing with the executable Rust project,
so it produces binary as a final artifact.
We will discuss another scenario of building a Rust library later.
Actual build process is done with the `std_build.py` script.
Here is the full list of configuration of this script:

```bash
 usage: std_build.py [-h] [--build_flags BUILD_FLAGS]
                     [--doctest_flags DOCTEST_FLAGS] [--test_flags TEST_FLAGS]
                     [--bench_flags BENCH_FLAGS] [--with_test]
                     [--cov_report COV_REPORT] [--with_bench] [--libs LIBS]
                     [--bins BINS]

 Rust build processing.

 options:
   -h, --help            show this help message and exit
   --build_flags BUILD_FLAGS
                         Additional command-line flags that can be passed to
                         the `cargo build` command.
   --lint_flags LINT_FLAGS
                         Additional command-line flags that can be passed to
                         the `cargo lint` command.
   --doctest_flags DOCTEST_FLAGS
                         Additional command-line flags that can be passed to
                         the `cargo testdocs` command.
   --test_flags TEST_FLAGS
                         Additional command-line flags that can be passed to
                         the `cargo testunit` command.
   --bench_flags BENCH_FLAGS
                         Additional command-line flags that can be passed to
                         the `cargo bench` command.
   --cov_report COV_REPORT
                         The output coverage report file path. If omitted,
                         coverage will not be run.
   --disable_tests       Flag to disable to run tests (including unit tests and
                         doc tests).
   --disable_benches     Flag to disable to run benchmarks.
   --disable_docs        Flag to disable docs building (including graphs, trees
                         etc.) or not.
   --libs LIBS           The list of lib crates `cargo-modules` docs to build
                         separated by comma.
   --bins BINS           The list of binaries `cargo-modules` docs to build and
                         make a smoke tests on them.
```

Note that the `libs` argument takes a list of library crate's names in your Rust project, e.g.
`--libs="crate1 crate2"`.
The `bins` argument takes a list of binary crate's names and binary names in your Rust project, e.g.
`--bins="crate1/bin1 crate1/bin2 crate2/bin1"`, note that each binary name correspond to each crate
and separated in this list with `/` symbol.
Under this build process we perform different steps of compiling and validating of our Rust project,
here is the list of steps (look at `./earthly/rust/scripts/std_build.py` and `./earthly/rust/scripts/std_docs.py`):

1. `cargo build` - Building all code in the workspace.
2. `cargo lint` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)
Checking all Clippy Lints in the workspace.
3. `cargo docs` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Documentation can be generated OK.
4. `cargo testunit` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Self contained Unit tests all pass.
5. `cargo testdocs` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Documentation tests all pass.
6. `cargo testcov` ([cargo alias](https://doc.rust-lang.org/cargo/reference/config.html#alias),
look at `./earthly/rust/stdcfgs/config.toml`)Checking Self contained Unit tests all pass and collect coverage.
7. `cargo bench` - Checking Benchmarks all run to completion.
8. `cargo depgraph` - Generating dependency graph based on the Rust code.
Generated artifacts are `doc/workspace.dot`, `doc/full.dot`, `doc/all.dot` files.
9. `cargo modules` - Generating modules trees and graphs based on the Rust code.
Generated artifacts are `doc/$crate.$bin.bin.modules.tree`, `doc/$crate.$bin.bin.modules.dot`
for the specified `--bins="crate1/bin1"` argument
and `target/doc/$crate.lib.modules.tree`, `target/doc/$crate.lib.modules.dot`
for the specified `--libs="crate1"` argument.
10. Running smoke tests on provided binary names (`--bins` argument).

Final step is to provide desired artifacts: docs and binary.

### Test

As you already mentioned that running of unit tests is done during the `build` process,
but if you need some integration tests please follow this [PostgreSQL builder](./postgresql.md),
Rust will have the same approach.

### Release and publish

To prepare a release artifact and publish it to some external container registries
please follow this [guide](./../../onboarding/index.md).
It is pretty strait forward for this builder process,
because as a part of `+build` target we already creating a docker image.

## Rust `nightly` channel

Be aware that we are running some tools in the `nightly` channel, such as `cargo fmt` and `cargo docs`.
It is highly likely that the `nightly` toolchain version on the CI machines differs from what you have locally.
Unfortunately, Rust tooling does not have the capability to preserve and maintain consistency between
`stable` and `nightly` toolchains simultaneously.
In our builds, we only preserve the `stable` toolchain version (`rust-toolchain.toml` file).

## Rust FUNCTIONs

While leveraging the [Earthly lib/rust](https://github.com/earthly/lib/tree/main/rust),
the following Rust FUNCTIONs are customize to align with our specific requirements
that our project needed.

* `EXECUTE` : This FUNCTION, adapted from the [Earthly lib/rust](https://github.com/earthly/lib/tree/main/rust),
  is tailored to execute commands according to user specifications.
  It serves a pivotal role in managing Rust project builds, handling outputs, and supporting features
  such as `JUnit` reporting and code coverage.
  Our modifications ensure that the command
  executed utilize the cache efficiently, which result in a faster compilation time.

```Earthfile
    # Example of using `EXECUTE` with a simple copy command
    DO +EXECUTE --cmd="cp $CARGO_INSTALL_ROOT/config.toml $CARGO_HOME/config.toml"
```

* `CARGO` : This FUNCTION serves as a shim of the original lib/rust `CARGO` FUNCTION
  to guarantee consistent usage of the appropriate upsteam Rust library.

```Earthfile
    # Example of using `CARGO` to install a Rust tool
    DO rust-ci+CARGO --args="install cargo-nextest --version=0.9.70 --locked"
```

* `COPY_OUTPUT` : This FUNCTION serves as a shim of the original lib/rust `COPY_OUTPUT`
  to facilitate the SAVE of ARTIFACT from the target folder (mounted cache) into the image layer.
  This FUNCTION will always trying to minimize the total size of the copued fileset,
  which result in a faster copy.

```Earthfile
    # Example of using `COPY_OUTPUT` where `SAVE ARTIFACT` is used
    # The `COPY_OUTPUT` will copy the output to `target` folder 
    DO rust+COPY_OUTPUT --output="nextest/ci/junit.xml"
    SAVE ARTIFACT target/nextest/ci/junit.xml AS LOCAL "$junit"
```

**Note that in order to called the above FUNCTIONs, `rust+INIT` should be called first.**

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/rust/Earthfile)
and any other files in the same directory.
We have learnt how to maintain and setup Rust project, as you can see it is pretty simple.
