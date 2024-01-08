package pkg_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"github.com/input-output-hk/catalyst-ci/tools/fetcher/pkg"
)

var _ = Describe("Artifact", func() {
	Describe("Fetch", func() {
		When("fetching an artifact", func() {
			var store *MockStore
			var usedKey string

			BeforeEach(func() {
				store = &MockStore{
					FetchFunc: func(key string) ([]byte, error) {
						usedKey = key
						return []byte("artifact"), nil
					},
				}
			})

			It("should use the correct key", func() {
				fetcher := pkg.NewArtifactFetcher("env", "fund", store)
				_, err := fetcher.Fetch("genesis", "1.0.0")
				Expect(err).ToNot(HaveOccurred())
				Expect(usedKey).To(Equal("env/fund/block0.bin-1.0.0"))
			})

			It("should return the artifact", func() {
				fetcher := pkg.NewArtifactFetcher("env", "fund", store)
				artifact, err := fetcher.Fetch("genesis", "1.0.0")
				Expect(err).ToNot(HaveOccurred())
				Expect(artifact).To(Equal([]byte("artifact")))
			})

			When("not specifying a version", func() {
				It("should use the correct key", func() {
					fetcher := pkg.NewArtifactFetcher("env", "fund", store)
					_, err := fetcher.Fetch("genesis", "")
					Expect(err).ToNot(HaveOccurred())
					Expect(usedKey).To(Equal("env/fund/block0.bin"))
				})
			})
		})
	})
})
