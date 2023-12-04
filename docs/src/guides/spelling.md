---
icon: material/spellcheck
---

# Spell Checking

## Introduction

Spell checking is integrated into the [`check`](https://input-output-hk.github.io/catalyst-ci/onboarding/#pipeline) pipeline to ensure the overall health of the project.

This utilizes [`cspell`](cspell.org) under the hood for checking code and other text documents. It can be used to check for misspelled words, identify potential errors, and suggest corrections.

## Configuration

Each repo will need a [`cspell.json`](http://cspell.org/configuration/) file in the root of the repo.
This file configures `cspell`.
The file provided in the `Catalyst-CI` repo should be taken as a starting point
for new projects.

## Project Words

It will be necessary for each project to have a list of custom words.
This list extends the list of valid words accepted by the spellchecker.

These words are added to the file:

```path
<repo root>/.config/dictionaries/project.dic
```

Words must ONLY be added to project words if they are correctly spelled.

## How it works

### Locally

#### Running check

Executing `earthly +check` will automatically run all checks, including the verification of markdown files in the repository.
To view the specific checks performed during the `check` stage, use the command `earthly doc`.
