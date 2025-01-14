package pkg_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestPkg(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Pkg Suite")
}

type MockStore struct {
	FetchFunc func(key string) ([]byte, error)
}

func (m *MockStore) Fetch(key string) ([]byte, error) {
	return m.FetchFunc(key)
}
