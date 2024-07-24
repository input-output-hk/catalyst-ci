# catalyst-ci

Common CI workflows for Project Catalyst.

## Documentation

The Documentation for how to use this repo are found here:

* [Documentation](https://input-output-hk.github.io/catalyst-ci/)

## Authentication

Many services used by CI need authentication.

1. Make sure you use `docker login` for dockerhub.com
2. Copy `.secret.template` to `.secret` and provide the required secrets 
   for access to the specified services.

Failure todo these things could cause your builds to fail due to rate limiting,
or inaccessible services.  