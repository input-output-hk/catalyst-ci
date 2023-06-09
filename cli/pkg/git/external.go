package git

import (
	"strings"

	"github.com/input-output-hk/catalyst-ci/cli/pkg"
)

type ExternalGitClient struct {
	exec pkg.Executor
}

func (e ExternalGitClient) Tags() ([]string, error) {
	output, err := e.exec.Run("tag", "-l")
	if err != nil {
		return nil, err
	}

	return strings.Split(output, "\n"), nil
}

func NewExternalGitClient(executor pkg.Executor) ExternalGitClient {
	return ExternalGitClient{
		exec: executor,
	}
}
