---
icon: material/star-check-outline
---

<!-- cspell: words OWASP -->

# Spectral / JSON and YAML Linter

JSON and YAML files can be linted with custom rules
using [Spectral](https://github.com/stoplightio/spectral).
The goal of using this linter is to ensure that best practice is followed.

## Configuration

Each repo will need one configuration file in the root of the repository.

* `.spectral.yml` - Configures rules, which can be
used to lint the JSON or YAML files.

There are rules available to be used or customization is possible too.
For more information, please visit [Spectral Document](https://meta.stoplight.io/docs/spectral/e5b9616d6d50c-rulesets)

## Usage

The linter can be used in different purpose,
so a `FUNCTION` named `BUILD_SPECTRAL` is implemented
to make it suit the purpose.

`BUILD_SPECTRAL` contains four main arguments

* `file_type`: the file type that will be lint.
If it is set to `json`, minifying the JSON files will be performed.
JSON and YAML linting are not allowed simultaneously to prevent conflicts.
  Enforcing separate linting
ensures accurate analysis for each file type in a folder, avoiding errors.
* `dir`: A directory that contains files to be lint.
* `src`: The root directory
* `rule_set`: Rules set that is used

## Example

The example of using the linter can be found in [link](/Earthfile).
The target `check-lint-openapi` is used for linting OpenAPI JSON file.
The current rules set that is being used are:

* [OWASP TOP 10](https://apistylebook.stoplight.io/docs/owasp-top-10)
* [Spectral Documentation](https://github.com/stoplightio/spectral-documentation)
* [OpenAPI](https://docs.stoplight.io/docs/spectral/4dec24461f3af-open-api-rules#openapi-rules)
