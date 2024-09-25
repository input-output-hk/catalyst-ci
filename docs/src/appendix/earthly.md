---
icon: material/earth-plus
tags:
    - Earthly
---

# Earthly

This appendix is designed to get you quickly up and running with [Earthly](https://earthly.dev).
Earthly serves a central role in the CI process and is the primary orchestrator along with Github Actions.

## Getting Started with Earthly

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Warning
    The process described in this section is purely for educational purposes.
    While the CI process does use Earthly, it does so in a very specific and opinionated way.
    Do *not* package your service using the methodology shown below.
    Instead, refer to the onboarding documentation for a description and examples of the proper method.
<!-- markdownlint-enable max-one-sentence-per-line -->

This section will get you started with the basics of Earthly in as little time as possible.
To maximize learning, this section is written with a hands-on approach, and you are highly encouraged to follow along.

### Video

If you prefer to learn visually, a video tutorial has been provided which introduces Earthly using a similar hands-on process.

<!-- markdownlint-disable max-one-sentence-per-line -->
!!!
note
    Before starting the video, check out the setup section below to get your local environment prepared to follow along.
<!-- markdownlint-enable max-one-sentence-per-line -->

<!-- markdownlint-disable MD013 MD033 -->
<div style="position: relative; padding-bottom: 58.63192182410424%; height: 0;">
    <iframe src="https://www.loom.com/embed/bc44ccbee2bb4617a214b9656f93504b?sid=0351889d-f940-4e1e-8e02-ffff5627b88b" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
</iframe>
</div>
<!-- markdownlint-enable MD013 MD033 -->

### Pre-requisites

The only pre-requisite knowledge that is required is experience working with Docker and `Dockerfile`s.
Since Earthly is built on top of Docker, it's assumed you're already familiar with Docker concepts.

### Setup

#### Installation

See the [installation methods](https://earthly.dev/get-earthly) available on the Earthly website.

#### Clone the example

<!-- markdownlint-disable max-one-sentence-per-line -->
!!! Note
    Even though we're using Go, you don't need to be familiar with the language or its tooling.
    The process we will walk through is generic enough that applying it to other languages should be trivial.
<!-- markdownlint-enable max-one-sentence-per-line -->

To demonstrate how to use Earthly, we'll be using a tiny Go program which simply prints "Hello, World!" to the screen.
You can get a local copy by performing the following:

```bash
git clone https://github.com/input-output-hk/catalyst-ci.git && \
    cd examples/onboarding/appendix_earthly
```

### Building an Earthfile

To begin, we are first going to introduce the most fundamental component of Earthly: the `Earthfile`.
The easiest way to think of an `Earthfile` is a mix between a `Dockerfile` and a GNU `makefile`.
Like a `Dockerfile`, only a single `Earthfile` can exist per directory and it *must* be named `Earthfile` in order to be detected.

#### Sample Structure

```Earthfile
VERSION 0.8  # This defines the "schema version" that this Earthfile satisfies

# A target, which is functionally equivalent to a `makefile` target.
deps:
    # A target can be thought of as a group of container image layers (think of Docker multi-stage builds)
    # For this target, we start by deriving from an image which contains the Go tooling we need
    FROM golang:1.22.4-alpine3.20

    # Earthly has a 1:1 relationship with most Dockerfile commands, but there are a few exceptions
    WORKDIR /work
```

Go ahead and copy the contents from above to an `Earthfile` in the local directory you cloned in the previous section.
At a foundational level, an `Earthfile` is *very* similar to a `Dockerfile`.
The commands are in all uppercase letters and there's typically only one command per line.

#### Schema

An `Earthfile` always starts by specifying a schema version which informs Earthly how it should go about parsing the file.
This allows the syntax and format of an Earthfile to evolve while maintaining backwards compatibility.
In our case, we target version `0.8` which is the latest version at the time of this writing.

#### Targets

An `Earthfile` also always has at least one target.
A target can be thought of as a grouping of image layers, similar to the way multi-stage builds work with Docker.
Each target then specifies one or more commands that create the image layers associated with that target.

```Earthfile
VERSION 0.8

deps:
    FROM golang:1.22.4-alpine3.20
    WORKDIR /work

    # These commands work identical to their Dockerfile equivalent
    COPY go.mod go.sum .
    RUN go mod download

src:
    # This target "inherits" from the `deps` target
    FROM +deps

    # The --dir flag is unique to Earthly and just ensures the entire directory
    # is copied (not just the contents inside of it)
    COPY --dir cmd .
```

Like multi-stage builds, targets can inherit from other targets.
In the above case, we now have two targets: the `deps` target downloads our external dependencies, and the `src` target copies the
source files into the image.
The `src` target inherits the `deps` target, meaning the `go.mod`, `go.sum`, and all externally downloaded dependencies will be
present.

#### Artifacts

```Earthfile
# Omitted for brevity

src:
    FROM +deps

    COPY --dir cmd .

build:
    FROM +src

    # This forces go to build a "static" binary with no dependencies
    ENV CGO_ENABLED=0
    RUN go mod tidy
    RUN go build -ldflags="-extldflags=-static" -o bin/hello cmd/main.go

    # This "exports" the built binary as an "output" of this target
    SAVE ARTIFACT bin/hello hello
```

In the above example, we introduce yet another target which is responsible for building our Go binary.
The above invocation is typical for building static Go binaries.
What's new is the usage of `SAVE ARTIFACT`.
This command takes two parameters: the local path inside the container to save, and a name to save it as.
In this case, we are saving our binary (`bin/hello`) as `hello`.
With this in place, other targets may now pull in this binary *without* having to inherit from the image.

Our targets don't produce anything useful yet, but this is a good point to stop and actually invoke earthly:

```bash
earthly +build
```

Earthly provides a CLI which is used for invoking Earthly targets.
The format is similar to GNU Make where you add a `+` followed by the target name.
If everything is working correctly, the Earthly run should succeed.

#### Images

```Earthfile
# Omitted for brevity

build:
    FROM +src

    ENV CGO_ENABLED=0
    RUN go mod tidy
    RUN go build -ldflags="-extldflags=-static" -o bin/hello cmd/main.go

    SAVE ARTIFACT bin/hello hello

docker:
    # Here we inherit from a "fresh" minimal alpine version
    FROM alpine:3.20.3
    WORKDIR /app

    # By default, we'll output this image with the 'latest' tag, but this can be
    # changed
    ARG tag=latest

    # Since we saved the artifact in the previous target, we can now directly
    # copy the
    # binary to this "fresh" image with none of the dependency bloat.
    COPY +build/hello .

    ENTRYPOINT ["/app/hello"]

    # This tells Earthly that this target produces a container image we want to
    # use
    SAVE IMAGE hello:${tag}
```

In the above example, we now add our fourth and final target which is responsible for building the final container image.
Instead of inheriting from `build`, and thereby inheriting all of its bloat, we instead inherit from a "fresh" Alpine image.
We then use `COPY` to pull in our binary that we saved from the `build` target.
This is a special Earthly syntax and is a powerful way to copy single outputs from a target without worrying about inheriting the
entire context.

We also add an `ARG` which allows us to specify the tag of the image when its created by Earthly.
By default, we set it to `latest`, but it can be changed in a number of ways, one of which is via the CLI:

```bash
earthly +docker --tag="foobar"
```

If you run the above command, you should see the image show up in your local Docker registry:

```bash
> docker image ls
REPOSITORY                  TAG       IMAGE ID       CREATED             SIZE
hello                       foobar    61c8a3947c93   About an hour ago   9.95MB
```

The reason Earthly produces an image is because of the `SAVE IMAGE` we included at the very end of the `Earthfile`.
This informs Earthly that this target produces an image we actually want to use by saving it locally.

You'll notice the size of the image is very small (< 10MB).
This is because we started from a base alpine image and *only* copied the binary from our `build` target.
Additionally, the image was saved with the `foobar` tag because we provided an alterative value for the `tag` argument when we
called the Earthly CLI.

#### Conclusion

Congratulations, you've created your first container image using Earthly.
We have only scratched the surface of the features provided by Earthly, and it's highly encouraged that you review the
[official documentation](https://docs.earthly.dev) to learn more.
You should now have enough knowledge to continue on with the onboarding process and learn about how Catalyst CI works using Earthly.
