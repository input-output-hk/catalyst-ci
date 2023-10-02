package providers

// cspell: words iface

import (
	"encoding/json"
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
	"github.com/input-output-hk/catalyst-ci/cli/pkg"
)

// S3RemoteStateProvider implements the RemoteStateProvider interface and is
// used to manage remote Terraform state on S3.
type S3RemoteStateProvider struct {
	S3      s3iface.S3API
	Session *session.Session
}

// FetchState fetches the state file at the given key from the S3 bucket.
func (s *S3RemoteStateProvider) Fetch(
	bucket string,
	key string,
) (pkg.State, error) {
	resp, err := s.S3.GetObject(&s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})

	if err != nil {
		return pkg.State{}, err
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return pkg.State{}, err
	}

	terraformState := pkg.State{}
	err = json.Unmarshal(data, &terraformState)

	if err != nil {
		return pkg.State{}, err
	}

	return terraformState, nil
}

func NewRemoteStateProvider(session *session.Session) S3RemoteStateProvider {
	return S3RemoteStateProvider{
		Session: session,
		S3:      s3.New(session),
	}
}
