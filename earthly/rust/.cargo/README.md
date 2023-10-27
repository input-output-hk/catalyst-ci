# Rust Cargo Configuration

We define RUST Global Cargo Configurations here.
It is applied globaly to all Rust Code built by Project Catalyst.

Each Project Catalyst Repo that has Rust code must include this file in:

```path
<repo>/.cargo/config.toml
```

This config exists here so that it can be used locally during development, as well as during CI builds.  

It will be checked during CI that it has not been altered from the enforced standard.
The enforced standard can be referenced here: [Catalyst-CI Global Cargo Config](todo)

If this file needs to be updated, please update it in the standard location first, have the PR
approved, and then update this file to match.

Differences between these files and the enforced standards will prevent CI from accepting your PR.
