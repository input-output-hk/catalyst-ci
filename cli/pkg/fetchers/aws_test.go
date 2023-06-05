package fetchers_test

import (
	"errors"

	"github.com/aws/aws-sdk-go/service/secretsmanager"
	"github.com/aws/aws-sdk-go/service/secretsmanager/secretsmanageriface"
	"github.com/input-output-hk/catalyst-ci/cli/pkg"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/fetchers"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"github.com/aws/aws-sdk-go/aws"
)

type mockSecretsManagerAPI struct {
	secretsmanageriface.SecretsManagerAPI
	Response secretsmanager.GetSecretValueOutput
	Error    error
}

func (m *mockSecretsManagerAPI) GetSecretValue(
	_ *secretsmanager.GetSecretValueInput,
) (*secretsmanager.GetSecretValueOutput, error) {
	return &m.Response, m.Error
}

var _ = Describe("Aws", func() {
	Describe("Fetching Certificates", func() {
		It("returns an error when unable to fetch secret", func() {
			mockSvc := &mockSecretsManagerAPI{
				Response: secretsmanager.GetSecretValueOutput{},
				Error:    errors.New("forced error"),
			}

			certFetcher := fetchers.AWSSatelliteCertificatesFetcher{
				API:  mockSvc,
				Path: "fake-path",
			}
			_, err := certFetcher.FetchCertificates()
			Expect(err).To(HaveOccurred())
		})

		It("returns the secret when able to fetch", func() {
			expected := pkg.SatelliteCertificates{
				CACertificate: "fake-ca-certificate",
				Certificate:   "fake-certificate",
				PrivateKey:    "fake-private-key",
			}

			mockSvc := &mockSecretsManagerAPI{
				Response: secretsmanager.GetSecretValueOutput{
					SecretString: aws.String(`
					{
						"ca_certificate": "fake-ca-certificate",
						"certificate": "fake-certificate",
						"private_key": "fake-private-key"
					}
					`),
				},
				Error: nil,
			}

			certFetcher := fetchers.AWSSatelliteCertificatesFetcher{
				API:  mockSvc,
				Path: "fake-path",
			}

			actual, err := certFetcher.FetchCertificates()
			Expect(err).NotTo(HaveOccurred())
			Expect(actual).To(Equal(expected))
		})

		It("returns an error when unable to parse secret", func() {
			mockSvc := &mockSecretsManagerAPI{
				Response: secretsmanager.GetSecretValueOutput{
					SecretString: aws.String(`
					{
						"ca_certificate": "fake-ca-certificate",
						"certificate": "fake-certificate"
					}
					`),
				},
				Error: nil,
			}

			certFetcher := fetchers.AWSSatelliteCertificatesFetcher{
				API:  mockSvc,
				Path: "fake-path",
			}

			_, err := certFetcher.FetchCertificates()
			Expect(err).To(HaveOccurred())
		})
	})
})
