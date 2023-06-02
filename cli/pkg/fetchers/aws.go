package fetchers

import (
	"encoding/json"
	"fmt"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/secretsmanager"
	"github.com/aws/aws-sdk-go/service/secretsmanager/secretsmanageriface"
	"github.com/input-output-hk/catalyst-ci/cli/pkg"
)

// AWSSatelliteCertificatesFetcher fetches the certificates required to connect
// to a remote Earthly satellite from AWS Secrets Manager.
type AWSSatelliteCertificatesFetcher struct {
	Api  secretsmanageriface.SecretsManagerAPI
	Path string
}

func (a AWSSatelliteCertificatesFetcher) FetchCertificates() (pkg.SatelliteCertificates, error) {
	input := &secretsmanager.GetSecretValueInput{
		SecretId: aws.String(a.Path),
	}

	result, err := a.Api.GetSecretValue(input)
	if err != nil {
		return pkg.SatelliteCertificates{}, err
	}

	var certs pkg.SatelliteCertificates
	if result.SecretString != nil {
		if err := json.Unmarshal([]byte(*result.SecretString), &certs); err != nil {
			return pkg.SatelliteCertificates{}, nil
		}

		if certs.CACertificate == "" || certs.Certificate == "" ||
			certs.PrivateKey == "" {
			return pkg.SatelliteCertificates{}, fmt.Errorf(
				"Failed parsing secret: %s",
				a.Path,
			)
		}

		return certs, nil
	} else {
		return pkg.SatelliteCertificates{}, fmt.Errorf("Invalid secret name: %s", a.Path)
	}
}

func NewAWSSatelliteCertificatesFetcher(
	path string,
	session *session.Session,
) *AWSSatelliteCertificatesFetcher {
	return &AWSSatelliteCertificatesFetcher{
		Api:  secretsmanager.New(session),
		Path: path,
	}
}
