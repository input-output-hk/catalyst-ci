# Rust Earthly Build Containers and UDCs

<!-- cspell: words rustup -->

This repo defines common rust targets and UDCs for use with rust.

## User Defined Commands

### RUST_SETUP

This FUNCTION sets up a rust build environment.

#### Invocation

In an `Earthfile` in your source repository add:

```Earthfile
example_rust_builder:
    DO +SETUP
```

This builder can then be used to build the projects source.
