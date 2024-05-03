---
icon: simple/go
title: Go
tags:
    - Go
---

<!-- markdownlint-disable single-h1 -->
# :simple-go: Go
<!-- markdownlint-enable single-h1 -->

## Introduction

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Tip
    If you're just looking for a complete example,
    [click here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/go/Earthfile).
    This guide will provide detailed instructions for how the example was built.
<!-- markdownlint-enable max-one-sentence-per-line -->

This guide will get you started with using the Catalyst CI to build Go-based projects.
By the end of the guide, we'll have an `Earthfile` that utilizes the Catalyst CI to build, release, and publish our Go program.

To begin, clone the Catalyst CI repository:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git
```

Navigate to `examples/go` to find a very basic Go program which prints "Hello, world!" to the terminal screen using `cowsay`.
This folder already has an `Earthfile` in it.
This is the `Earthfile` we will be building in this guide.
You can choose to either delete the file and start from scratch, or read the guide and follow along in the file.

## Building the Earthfile

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    The below sections will walk through building our `Earthfile` step-by-step.
    In each section, only the fragments of the `Earthfile` relative to that section are displayed.
    This means that, as you go through each section, you should be cumulatively building the `Earthfile`.
    If you get stuck at any point, you can always take a look at the
    [example](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/go/Earthfile).
<!-- markdownlint-enable max-one-sentence-per-line -->

### Installing dependencies

```Earthfile
VERSION 0.8

IMPORT ../../earthly/go AS go-ci

deps:
    # This target is used to install external Go dependencies.
    FROM golang:1.21-alpine3.19
    WORKDIR /work
    # Any build dependencies should also be captured in this target.
    RUN apk add --no-cache gcc musl-dev

    # This FUNCTION automatically copies the go.mod and go.sum files and runs
    # `go mod download` to install the dependencies.
    DO go-ci+DEPS --ginkgo="false"
```

The first target we are going to create will be responsible for downloading the external dependencies that our Go program uses.
By design, the only files we need for this are the `go.mod` and `go.sum` files.
By only copying these files, we ensure that this target is cached for most development and only rebuilds when we add new
dependencies.

We are going to be inheriting from an alpine image because we are pushing for a fully static build.
When using example as a starting place, feel free to change the base image.
This image is *only* used during the build steps, so it's not important to minimize its size.
Keep in mind, though, excessively large targets can impact the speed of the caching step (due to lots of I/O).

This target is also going to be responsible for installing external build dependencies.
These are dependencies that are not specific to a language and usually get installed system-wide.
In our case, since we're building a static binary, we need `gcc` and `musl`.

Finally, the actual logic we will be using is encapsulate in a FUNCTION.
This is a very common pattern, as an `Earthfile` can get repetitive across a repository.
In our case, we use the `go-ci+DEPS` FUNCTION that will automatically copy our `go.mod` and `go.sum` files and then execute
`go mod download`.
The FUNCTION will also establish a cache for the Go tooling.
This means that, even if our source code changes, we'll see a substantial speed boost when compiling because the cache is preserved
across Earthly runs.

### Running checks

```Earthfile
src:
    # This target copies the source code into the current build context
    FROM +deps
    COPY --dir cmd .

check:
    # This target checks the overall health of the source code.
    FROM +src

    # This FUNCTION validates the code is formatted according to Go standards.
    DO go-ci+FMT --src="go.mod go.sum cmd"

    # This FUNCTION runs golangci-lint to check for common errors.
    DO go-ci+LINT --src="go.mod go.sum cmd"
```

With our dependencies installed, we're now ready to start operating with the source code.
To do this, we establish a dedicated `src` target that is solely responsible for copying the local source code into the context.
This is a common pattern as it ensures we perform this only once and it makes future changes easier (as we only copy in a single
place).
Any future targets which need access to the source code will inherit from this target.

Now that the source code is available, we can begin performing static checks.
These checks are intended to verify the code is healthy and conforms to a certain standard.
As we did in the previous section, here we rely on FUNCTIONs again to perform these checks.
These two FUNCTIONs, `go-ci+FMT` and `go-ci+LINT` will validate the code formatting is correct and also perform a series of lints to validate code quality.

Note that these checks are fast (compared to later steps) and perform quick feedback on code quality.
Since this is the first target run in CI, we want to fail the CI as quickly as possible if we can easily find code quality issues.
In future targets, we will run tests which can tend to take significantly more time to run than static analysis tools.

### Build and test

```Earthfile
build:
    # This target builds the application.
    FROM +src

    # The below just creates a fully static binary with no CGO dependencies.
    ENV CGO_ENABLED=0
    RUN go build -ldflags="-extldflags=-static" -o bin/hello cmd/main.go

    # We save the artifact here so that future targets can use it.
    SAVE ARTIFACT bin/hello hello

test:
    # This target runs unit tests.
    FROM +build

    RUN go test ./...
```

With the basic checks out of the way, it's finally time to compile our Go program.
Since we need the source code to do this, we'll inherit from the `src` target.
The actual build process is fairly straight-forward, and the additional flags are simply there to ensure a fully static output is
created.

It's important we use `SAVE ARTIFACT` at the end of the build to make the compiled binary available to other targets.
Remember that targets can reference other targets, even ones in another `Earthfile`.
So by `SAVE ARTIFACT` here, we're making this binary available to any other `Earthfile` which may need to use it.

Finally, after building the binary, we will run our tests.
In the case of this example, there are no actual tests to run, so the target will complete very quickly.
However, we would expect a more complex project to contain many tests.

Notice that we inherit from the `build` target: this is because in most cases there will be a layer of compilation before actually
running tests.
By choosing to make our `test` target inherit from `build`, we ensure that we can maximize reusing the cached binary that was
created in the previous target.
This is a good pattern to observe and follow where practical, as it can dramatically improve CI times.

### Releasing

```Earthfile
release:
    # This target is called by the CI when performing a release. It should use
    # `SAVE ARTIFACT` to save the release artifact which is then picked up by
    # the CI.
    FROM +build

    SAVE ARTIFACT bin/hello hello
```

With our source code checked, binary built, and tests passed, we're now ready to release.
The release target will instruct the CI to take whatever artifact we save in this target and automatically include it as part of a
GitHub Release when a new release is created (i.e., a new git tag is created).
In some cases, it makes sense to skip this step, like for projects which produce artifacts that are only usable in a container.
For our case, since our example program prints something to the terminal (and it's statically built), it makes sense to release the
binary by itself.

The actual logic used in this target is minimal.
Since we already built the binary in the `build` target, we can simply inherit from it and do another `SAVE ARTIFACT`.
This may seem redundant, but the CI sees the `build` and `release` targets as two separate steps.

Note that we could have also sourced from a new image and used `COPY +build/hello .` with `SAVE ARTIFACT`.
However, if we did this, we would be needlessly adding time to the CI by creating a new image with a single layer.
It's much faster to simply inherit from the target and then use `SAVE ARTIFACT`.

### Publishing

```Earthfile
publish-example:
    # This target is called by CI when publishing images. It should use the
    # `SAVE IMAGE` command to save the image which is then picked up by the CI.
    # Note that we start from a "fresh" base image.
    FROM alpine:3.19
    WORKDIR /app
    ARG tag=latest  # Prefer to use `latest` by default, the CI will override this.

    COPY +build/hello .  # Use the cached artifact from the build target.

    ENTRYPOINT ["/app/hello"]
    SAVE IMAGE hello:${tag}
```

Now we want to publish a container image that runs our binary.
While the actual use-case for a container is a bit vague, we create one here for demonstration purposes.
It also serves as a natural way to use our program without having to rely on a package manager (i.e. `docker run ...`).

In this target, it's important we start with a "fresh" image by using `FROM`.
Unlike the previous targets, here the size of the image matters as the resulting image will be published to a registry.
In our case, we just take a plain `alpine` image as we don't need any of the Go tooling we used previously (since the binary has
already been built for us).

We add a `tag` argument out of convention.
During local testing, it's sometimes helpful to call `earthly +publish` and specify a different tag to test different versions of
the container image.
However, the CI will *not* pass this argument when it executes the target, so it's important to always set a default value.
Instead, the CI will re-tag the image with the appropriate tags after building it.

Since the binary has already been built, we can simply `COPY` it from the `build` target.
As in the `release` target, this ensures we use the cache as much as possible.
It also meets the best practice of having a single place where artifacts are built and copied from.

Finally, we set the appropriate entrypoint and use `SAVE IMAGE` to instruct Earthly to save the final container image.
When the CI executes this target, it will automatically detect the saved image and publish it to the configured container
registries.

## Conclusion

You can see the final `Earthfile` [here](https://github.com/input-output-hk/catalyst-ci/blob/master/examples/go/Earthfile).
This `Earthfile` will check the health of our source code, build and test our binary, and then finally release it to GitHub and
publish it to one or more container registries.
At this point, please feel free to experiment more and run each target individually.
Once you're ready, you can copy this example and modify it for your specific context.
