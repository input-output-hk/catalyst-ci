package scanners_test

// cspell: words onsi gomega

import (
	"testing"

	"github.com/input-output-hk/catalyst-ci/cli/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

type mockParser struct {
	earthfile pkg.Earthfile
	err       error
}

func (m *mockParser) Parse(path string) (pkg.Earthfile, error) {
	m.earthfile.Path = path
	return m.earthfile, m.err
}

func TestFileScanner(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "FileScanner Suite")
}
