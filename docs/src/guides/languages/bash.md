---
icon: material/bash
title: Bash Scripts
tags:
    - Bash
---

<!-- markdownlint-disable single-h1 -->
# :material-bash: Bash Scripts
<!-- markdownlint-enable single-h1 -->

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build projects that include Bash scripts.
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI that can check your Bash scripts.

Bash is not considered a stand alone target,  although bash scripts ar used extensively across multiple targets.
The Bash support consists solely of a single repo wide `check` target which validates:

* Are any of the `bash` shell scripts redundant.
  * This prevent maintenance issues where common scripts are copy/pasted rather than being properly organized.
* Do the bash scripts pass `shellcheck` lints.
  * This forces us to follow a consistent style guide, and also checks for problematic Bash syntax.

To begin, clone the Catalyst CI repository:

## Adding Bash checks to your Repo that is already using Catalyst-CI

Bash script checking is to be added to a repo that is already using Catalyst CI.

All that needs to happen is the following be added to the `Earthfile` in the root of the repo.

```Earthfile
# Internal: shell-check - test all bash files against our shell check rules.
shell-check:
    FROM alpine:3.18

    DO github.com/input-output-hk/catalyst-ci/earthly/bash:vx.y.z+SHELLCHECK --src=.

# check all repo wide checks are run from here
check:
    FROM alpine:3.18

    # Lint all bash files.
    BUILD +shell-check

```

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    It is expected that there may be multiple repo level `checks`.
    This pattern shown above allows for this by separating the individual checks into their own targets.
    The `check` target then just executed `BUILD` once for each check.
<!-- markdownlint-enable max-one-sentence-per-line -->

### Common Scripts

It is not a good practice to copy bash scripts with common functionality.
Accordingly, the *Utility* target `./utilities/scripts+bash-scripts` exists to provide a central location for common scripts.
These are used locally to this repo.

A common pattern is to create a symlink called `include/` with your scripts.
You would then source (or call) the common scripts relative to `include/`.
However as Earthly will not copy files from a symlink, in your Earthfile you will need to correct that with a line similar to:

```Earthfile
    COPY --dir scripts /scripts
    COPY --dir ../../utilities/scripts+bash-scripts/include /scripts/include
```

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    This is just an example, and you would adapt it to your specific requirements.
<!-- markdownlint-enable max-one-sentence-per-line -->

### Running checks

From the root of the repo, you can check all bash scripts within the repo by running:

```sh
earthly +check
```

This will also run all other repo-wide checks that are in use.

### Build and test

Bash scripts should not have a `build` target.
They can form part of the Build of other targets.

### Releasing

Bash scripts should not have a discreet `release` target.
They can form part of the `release` of other targets.

### Publishing

Bash scripts should not have a discreet `publish` target.
They can form part of the `publish` of other targets.

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/Earthfile).

This `Earthfile` will check the quality of the Bash files within the Catalyst-CI repo.
