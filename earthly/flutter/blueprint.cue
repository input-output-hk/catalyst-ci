version: "1.0"
project: {
	name: "ci-flutter"
	ci: targets: {
		"test-flutter-base-amd64": {
			platforms: ["linux/amd64"]
		}
		"test-flutter-base-arm64": {
			platforms: ["linux/arm64"]
		}
	}
}
