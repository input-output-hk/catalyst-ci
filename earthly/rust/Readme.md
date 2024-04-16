# Rust Earthly Build Containers and UDCs

<!-- cspell: words rustup -->

This repo defines common rust targets and UDCs for use with rust.

## User Defined Commands

### RUST_SETUP

This FUNCTION sets up a rust build environment.

Rust build environments are locked to the `rust-toolchain.toml` file in the repo.
This ensures that the version of the toolchain used is locked with the dependencies.

#### Invocation

In an `Earthfile` in your source repository add:

```Earthfile
example_rust_builder:
    FROM +rustup

    DO +RUST_SETUP --toolchain=./rust-toolchain.toml
```

This builder can then be used to build the projects source.
