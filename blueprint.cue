version: "1.0"
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
				credentials: {
					provider: "aws"
					path:     "global/ci/earthly"
				}
				org:       "Catalyst"
				satellite: "ci"
				version:   "0.8.15"
			}

			github: registry: "ghcr.io"
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
		registry: ci.providers.aws.ecr.registry
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
