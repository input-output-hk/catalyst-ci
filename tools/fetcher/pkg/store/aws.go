package store

import (
	"fmt"
	"io"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3iface"
)

// S3Store is an implementation of the Store interface for fetching data from
// AWS S3.
type S3Store struct {
	Bucket  string
	S3      s3iface.S3API
	Session *session.Session
}

func (s *S3Store) Fetch(key string) ([]byte, error) {
	resp, err := s.S3.GetObject(&s3.GetObjectInput{
		Bucket: aws.String(s.Bucket),
		Key:    aws.String(key),
	})

	if err != nil {
		return nil, fmt.Errorf("failed to fetch S3 object: %w", err)
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read S3 object: %w", err)
	}

	return data, nil
}

// NewS3Store creates a new S3Store.
func NewS3Store(bucket string, session *session.Session) *S3Store {
	return &S3Store{
		Bucket:  bucket,
		Session: session,
		S3:      s3.New(session),
	}
}
