version: "1.0"
project: {
	name: "jorm-metrics-server"
	release: {
		docker: {
			on: {
				merge: {}
				tag: {}
			}
			config: {
				tag: _ @forge(name="GIT_COMMIT_HASH")
			}
		}
	}
}
