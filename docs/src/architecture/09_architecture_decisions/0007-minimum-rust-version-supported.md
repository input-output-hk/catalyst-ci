---
    title: 0007 Rust Version configuration in `cargo.toml`
    adr:
        author: Steven Johnson
        created: 21-Jan-2024
        status:  accepted
        extends:
            - 0005-rust
    tags:
        - Rust
---

## Context

In the Rust`cargo.toml` it is possible to specify a minimum version of Rust supported by a Crate/Application.
This rust projects which consume crates to ensure they or on a supported version.
There should be a policy about How many old versions of Rust is supported by our project.

## Assumptions

This ADR is deliberately limited to the initial bring up phase of our projects, and subject to review.

## Decision

We will not use the `rust-version` feature of `cargo.toml` during initial bring up.
We have not defined a maximum range of valid Rust versions, and always build ONLY with the version defined in `rust-toolchain.toml`.

Currently the ONLY supported rust version is the one specified by `rust-toolchain.toml`.

If at a later time, a range of rust versions is decided to be supported then:

* This ADR will be obsoleted by a new one which defines that range of supported versions.
* The allowable range will need to be enforced in CI to ensure a `Cargo.toml` file does not specify the wrong thing.
* All Rust versions in that range will need to be tested in CI to ensure they are properly supported.

## Risks

None, this decision is subject to review at any time.

## Consequences

Development should be easier, and CI faster as we are specifically locked to a single Rust toolchain version.

## Scope

This ADR applies to all projects which consume `Catalyst-CI` unless they define an ADR specific to that project.

## More Information

* [`rust-version` field](https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field)
