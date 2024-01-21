# Rust Standardized Configuration

<!-- cspell: words rustfmt -->

We define RUST Global Cargo Configurations here.
It is applied globally to all Rust Code built by Project Catalyst.

There are many tools in the rust ecosystem, and there is not a single config file which controls them.
This directory contains our standardized configuration for these tools to ensure consistent use.
These files must be consistent with the Rust configs being used to build code in CI.
They are also important to be consistent on a local developers machine to ensure consistent environments.

All configs exists here so that they can be used locally during development, as well as during CI builds.  

They will be checked during CI to ensure they have not been altered from the enforced standard.
The enforced standard can be referenced here: [Catalyst-CI Global Cargo Config](todo)

If a file needs to be updated, please update it in the standard location first, have the PR
approved, and then update the equivalent file in the project repo to match it.

Differences between these files and the enforced standards will prevent CI from accepting your PR.

## `cargo_config.toml`

This is the standard `.cargo/config.toml` file.

Each Project Catalyst Repo that has Rust code must include this file in:

```path
<repo>/.cargo/config.toml
```

## `clippy.toml`

Clippy configuration options.  
Goes in the Rust workspace root folder.

## `nextest.toml`

Configures the `nextest` test runner.  
Goes in `<workspace>/.config/nextest.toml`

## `deny.toml`

Configuration for cargo deny to enforce software supply chain control.
This file goes in `<workspace>/deny.toml`

## `rustfmt.toml`

Configuration for `rustfmt`.
Goes in `<workspace>/rustfmt.toml`
