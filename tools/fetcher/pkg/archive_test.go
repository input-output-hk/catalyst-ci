package pkg_test

import (
	"github.com/input-output-hk/catalyst-ci/tools/fetcher/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("Archive", func() {
	Describe("Fetch", func() {
		When("fetching an archive", func() {
			var store *MockStore
			var usedKey string

			BeforeEach(func() {
				store = &MockStore{
					FetchFunc: func(key string) ([]byte, error) {
						usedKey = key
						return []byte("archive"), nil
					},
				}
			})

			It("should use the correct key and ID", func() {
				fetcher := pkg.NewArchiveFetcher("test", store)
				_, err := fetcher.Fetch("id")
				Expect(err).ToNot(HaveOccurred())
				Expect(usedKey).To(Equal("test/id"))
			})

			It("should return the archive", func() {
				fetcher := pkg.NewArchiveFetcher("test", store)
				archive, err := fetcher.Fetch("id")
				Expect(err).ToNot(HaveOccurred())
				Expect(archive).To(Equal([]byte("archive")))
			})
		})
	})
})
