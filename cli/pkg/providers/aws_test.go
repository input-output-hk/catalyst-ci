package providers_test

// cspell: words iface onsi gomega

import (
	"bytes"
	"fmt"
	"io"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/providers"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

type mockS3Client struct {
	s3iface.S3API
	Response []byte
	Err      error
}

func (m *mockS3Client) GetObject(
	_ *s3.GetObjectInput,
) (*s3.GetObjectOutput, error) {
	if m.Err != nil {
		return nil, m.Err
	}

	return &s3.GetObjectOutput{
		Body: io.NopCloser(bytes.NewReader(m.Response)),
	}, nil
}

var _ = Describe("Aws", func() {
	Describe("Fetch", func() {
		When("A valid response is returned", func() {
			It("Should return the state", func() {
				fetcher := providers.S3RemoteStateProvider{
					Session: session.Must(session.NewSession()),
					S3: &mockS3Client{
						Response: []byte(
							`{"version":1,"terraform_version":"1.0.0"}`,
						),
						Err: nil,
					},
				}

				state, err := fetcher.Fetch("test-bucket", "test-key")
				Expect(err).ToNot(HaveOccurred())
				Expect(state.Version).To(Equal(uint8(1)))
				Expect(state.TerraformVersion).To(Equal("1.0.0"))
			})
		})

		When("An invalid JSON response is returned", func() {
			It("Should return an error", func() {
				fetcher := providers.S3RemoteStateProvider{
					Session: session.Must(session.NewSession()),
					S3: &mockS3Client{
						Response: []byte(
							`{"version":1,"terraform_version":"1.0.0"`,
						),
						Err: nil,
					},
				}

				_, err := fetcher.Fetch("test-bucket", "test-key")
				Expect(err).To(HaveOccurred())
			})
		})

		When("An error response is returned", func() {
			It("Should return an error", func() {
				fetcher := providers.S3RemoteStateProvider{
					Session: session.Must(session.NewSession()),
					S3: &mockS3Client{
						Response: []byte(""),
						Err:      fmt.Errorf("error"),
					},
				}

				_, err := fetcher.Fetch("test-bucket", "test-key")
				Expect(err).To(HaveOccurred())
			})
		})
	})
})
