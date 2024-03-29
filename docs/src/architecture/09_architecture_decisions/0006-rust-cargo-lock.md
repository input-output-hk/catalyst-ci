---
    title: 0006 Rust Cargo Lock
    adr:
        author: Steven Johnson
        created: 09-Jan-2024
        status:  accepted
        extends:
            - 0005-rust
    tags:
        - Rust
---

## Context

Rust has an optional `cargo.lock` file which can lock the dependencies of a project.
There are [pros and cons][Cargo/toml vs Cargo.lock] to using the `lock` file.

## Assumptions

This ADR is deliberately limited to the initial bring up phase of our projects, and subject to review.

## Decision

Rust will [not][Why have Cargo.lock in Version Control] use `cargo.lock` when consuming  libraries.
It will ONLY respect it for building binaries.

As we are in the initial stages of a number of projects, it is easier to iterate without
worrying about `cargo.lock` being up-to-date.

Accordingly, until the binaries we would publish approach releasable state we will not
use the `cargo.lock` file.

## Risks

We forget to introduce `cargo.lock` on our binaries when we approach release.

## Consequences

This should make it a little easier to iterate with less issues caused by out of date `cargo.lock` files finding there way into CI.

## Scope

This ADR applies to all projects which consume `Catalyst-CI` unless they define an ADR specific to that project.

## More Information

* [Cargo/toml vs Cargo.lock]
* [Why have Cargo.lock in Version Control]

[Cargo/toml vs Cargo.lock]: https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
[Why have Cargo.lock in Version Control]: https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control
