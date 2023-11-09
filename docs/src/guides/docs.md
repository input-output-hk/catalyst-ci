---
icon: material/book-open-page-variant-outline
---

# Docs

[TODO](https://github.com/input-output-hk/catalyst-ci/issues/81)

* Documentation Guide

When a PR is raised the documentation for that PR is built and published.
Branch docs are published to `<pages>/branch/<branch_name>`.
`<branch_name>` is the name of the branch with all non alpha-numeric characters replaced by underscore (`_`).

When the branch is finally merged, the branch documentation is removed.
This allows us to easily validate what any PR will do to the published documentation before its published officially.

All PR's documentation should be checked as part of PR review.
Not just the contents of the PR itself.
