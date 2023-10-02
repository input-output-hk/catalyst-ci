package parsers_test

// cspell: words onsi gomega

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestParsers(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Parsers Suite")
}
