package store_test

// cspell: words iface onsi gomega

import (
	"bytes"
	"fmt"
	"io"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
	s "github.com/input-output-hk/catalyst-ci/tools/fetcher/pkg/store"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

type mockS3Client struct {
	s3iface.S3API
	Bucket   string
	Key      string
	Response []byte
	Err      error
}

func (m *mockS3Client) GetObject(
	input *s3.GetObjectInput,
) (*s3.GetObjectOutput, error) {
	if m.Err != nil {
		return nil, m.Err
	}

	m.Bucket = *input.Bucket
	m.Key = *input.Key

	return &s3.GetObjectOutput{
		Body: io.NopCloser(bytes.NewReader(m.Response)),
	}, nil
}

var _ = Describe("Aws", func() {
	Describe("Fetch", func() {
		var store s.S3Store

		When("A valid response is returned", func() {
			BeforeEach(func() {
				store = s.S3Store{
					Bucket:  "test-bucket",
					Session: session.Must(session.NewSession()),
					S3: &mockS3Client{
						Response: []byte("test"),
						Err:      nil,
					},
				}
			})

			It("should use the correct bucket", func() {
				_, err := store.Fetch("test-key")
				Expect(err).ToNot(HaveOccurred())
				Expect(store.S3.(*mockS3Client).Bucket).To(Equal("test-bucket"))
			})

			It("should use the correct key", func() {
				_, err := store.Fetch("test-key")
				Expect(err).ToNot(HaveOccurred())
				Expect(store.S3.(*mockS3Client).Key).To(Equal("test-key"))
			})

			It("should return the correct object data", func() {
				data, err := store.Fetch("test-key")
				Expect(err).ToNot(HaveOccurred())
				Expect(data).To(Equal([]byte("test")))
			})
		})

		When("An error response is returned", func() {
			BeforeEach(func() {
				store = s.S3Store{
					Bucket:  "test-bucket",
					Session: session.Must(session.NewSession()),
					S3: &mockS3Client{
						Response: []byte("test"),
						Err:      fmt.Errorf("test error"),
					},
				}
			})

			It("should return an error", func() {
				_, err := store.Fetch("test-key")
				Expect(err).To(HaveOccurred())
			})
		})
	})
})
