# CSpell Linter

This Earthly Target and UDC enables uniform spell checking of all source and
documentation files.

## How it works

Spellchecking is performed with the [`cspell`](cspell.org) program.

Use the `CSPELL` Earthly UDC to enable uniform and consistent spell checking.

This spellchecker is to be used in preference to tool specific spell checkers,
such as `cargo spellcheck`.
This is because we need to provide uniform and consistent spell checking across
multiple source languages and documentation files.
Tool specific spell checkers are limited in the kinds of files they can check,
and also will use different configurations, dictionaries and project word lists.

## DO NOT RUN AS PART OF A CONTAINER BUILD TARGET

This UDC is **NOT** intended to be used inside container builds.
Its sole purpose is to enforce uniform and consistent spell checking for all files in a repository.
It makes no assumptions about which files may or may not end up inside a container or are part of a build.
This is *INTENTIONAL*.

IF this UDC is used inside a container build, it is **NOT** a bug if it does not do the correct thing.

## Using the spell checking

In an Earthfile in your repo, add the following:

### Spell checking in your repo

```earthfile
spellcheck-lint:
    # Check spelling in this repo.
    LOCALLY

    DO github.com/input-output-hk/catalyst-ci/earthly/cspell:<tag>+CSPELL_LOCALLY --src=$(echo ${PWD})
```

In this use case, the UDC is run Locally, so that the src in the repo can be directly checked.

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

This can be necessary for the following reasons:

* The built-in dictionaries do not contain all possible valid words.
  * This is especially true when using names of Companies, Products or Technology.
* There are identifiers used in the code which are used which fail spell checks.

Words must ONLY be added to project words if they are correctly spelled.

Project words that are added MUST be included in any PR where they became necessary.
PR Review MUST check that the added words are both reasonable and valid.

Before a word is added to the project dictionary, it should be considered if it is a word likely to occur many times.

Some spelling errors may only occur once, or a handful of times.
Or, they may be an artifact of the code itself.
In these cases it is MUCH better to disable the spelling error inline rather than add a word to the project dictionary.
See [In Document Settings](http://cspell.org/configuration/document-settings/#in-document-settings) for details.

## Generated Files

Automatically generated files are likely to contain large amounts of spelling errors.
For these files/paths, exclude them from the spell check by adding their filenames to `"ignorePaths": []` in the `cspell.json` file.

## Editor Integration

`cspell` is integrated into VSCode and may be integrated into other Editors.

The editor integration should pick up the `cspell.json` configuration file and behave exactly the same as the Earthly UDC.
