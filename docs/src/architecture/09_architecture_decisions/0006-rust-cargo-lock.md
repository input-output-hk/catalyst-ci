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

Rust will not use `cargo.lock` when building libraries.  
It will ONLY respect it for building binaries.

As we are in the initial stages of a number of projects, it is easier to iterate without
worrying about `cargo.lock` being up-to-date.

Accordingly, until the binaries we would publish approach releasable state we will not
use the `cargo.lock` file.

## Risks

We forget to introduce `cargo.lock` on our binaries when we approach release.

## Consequences

This should make it a little easier to iterate with less issues caused by out of date `cargo.lock` files finding there way into CI.

## More Information

* [Cargo/toml vs Cargo.lock]

[Cargo/toml vs Cargo.lock]: https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
