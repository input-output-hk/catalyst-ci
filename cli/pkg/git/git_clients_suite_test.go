package git_test

// cspell: words onsi gomega

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

type mockExecutor struct {
	commandOutput string
	err           error
}

func (m *mockExecutor) Run(_ ...string) (string, error) {
	return m.commandOutput, m.err
}

func TestGitClients(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "GitClients Suite")
}
