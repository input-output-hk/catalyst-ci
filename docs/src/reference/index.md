---
icon: material/file-document-multiple-outline
---
# Reference

This section contains in-depth documentation about the various components that make up the Catalyst CI process.
The CI process does provide a useful layer of abstraction for developers to use, however, it's not intended to be a black box.
The full system is built on two simple technologies: Earthly and GitHub Actions.
A combination of these two systems is what ultimately constructs the whole pipeline.

If you need help with troubleshooting the CI process, or have a desire to modify the process to meet a particular need, this section
will prove helpful.
It is broken up into the foundational components of the CI process, with each component getting an in-depth breakdown of how it
works.
