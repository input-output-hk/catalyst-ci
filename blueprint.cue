global: {
	ci: {
		local: [
			"^check(-.*)?$",
			"^build(-.*)?$",
			"^package(-.*)?$",
			"^test(-.*)?$",
		]
		registries: [
			ci.providers.aws.ecr.registry,
		]
		providers: {
			aws: {
				ecr: registry: "332405224602.dkr.ecr.eu-central-1.amazonaws.com"
				region: "eu-central-1"
				role:   "arn:aws:iam::332405224602:role/ci"
			}

			docker: credentials: {
				provider: "aws"
				path:     "global/ci/docker"
			}

			git: credentials: {
				provider: "aws"
				path:     "global/ci/deploy"
			}

			earthly: {
				satellite: credentials: {
					provider: "aws"
					path:     "global/ci/ci-tls"
				}
				version: "0.8.15"
			}

			github: registry: "ghcr.io"

			tailscale: {
				credentials: {
					provider: "aws"
					path:     "global/ci/tailscale"
				}
				tags:    "tag:cat-github"
				version: "latest"
			}
		}
		secrets: [
			{
				name:     "GITHUB_TOKEN"
				optional: true
				provider: "env"
				path:     "GITHUB_TOKEN"
			},
		]
	}
	deployment: {
		registries: {
			containers: "ghcr.io/input-output-hk/catalyst-forge"
			modules:    ci.providers.aws.ecr.registry + "/catalyst-deployments"
		}
		repo: {
			url: "https://github.com/input-output-hk/catalyst-world"
			ref: "master"
		}
		root: "k8s"
	}
	repo: {
		defaultBranch: "master"
		name:          "input-output-hk/catalyst-ci"
	}
}
