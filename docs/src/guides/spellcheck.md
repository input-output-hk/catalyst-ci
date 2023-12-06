---
icon: material/spellcheck
---

# Spell Checking

## Introduction

Spell checking is integrated into the [`check`](https://input-output-hk.github.io/catalyst-ci/onboarding/#pipeline) pipeline.
This is to ensure the overall health of the project.

This utilizes [`cspell`](cspell.org) under the hood for checking code and other text documents.
It can be used to check for misspelled words, identify potential errors, and suggest corrections.

## Using the spell checking

In an Earthfile in your repo, add the following:

```earthfile
check-spelling:
    DO github.com/input-output-hk/catalyst-ci/earthly/cspell:<tag>+check-spelling
```

Executing `earthly +check-spelling` will automatically run the spell checking to all files in the repository.

## Configuration

Each repo will need a [`cspell.json`](http://cspell.org/configuration/) file in the root of the repo.
This file configures `cspell`.
The file provided in the `Catalyst-CI` repo should be taken as a starting point
for new projects.

## Adding specific words to documents

Words must ONLY be added to document words if they are correctly spelled.

### Project Words

It will be necessary for each project to have a list of custom words.
This list extends the list of valid words accepted by the spellchecker.

These words are added to the file:

```path
<repo root>/.config/dictionaries/project.dic
```

The path can also be configured in the `cspell.json` file.

```json
"dictionaryDefinitions": [
    {
        "name": "project-words",
        "path": ".config/dictionaries/project.dic",
        "description": "Words used in this project.",
        "addWords": true
    }
],
```

### Specific file patterns words

Custom words and dictionaries for specific file patterns can be configured inside `cspell.json` in the root of the repo.
This can be made by adding `overrides` with custom specifications for specific file patterns.

<!-- cspell: disable -->
```json
"overrides": [
    {
        "language": "es,es_ES",
        "filename": "**/*_es.arb",
        "dictionaries": [
            "es-es"
        ]
    },
    {
        "filename": "**/*.pbxproj",
        "allowCompoundWords": true,
        "words": [
            "iphoneos",
            "onone",
            "xcassets",
            "objc",
            "xcconfig",
            "lproj",
            "libc",
            "objc",
            "dsym"
        ]
    }
]
```
<!-- cspell: enable -->

### Inline specific words

It is possible to specify custom words within a file by adding comments.

```
cspell: words <words>
```

Here are some examples for inlining:

- Comments on Earthfiles
```earthly
# cspell: words libgcc freetype lcms openjpeg etag 
```

- Comments on markdown files
```md
<!-- cspell: words healthcheck isready psql --> 
```
