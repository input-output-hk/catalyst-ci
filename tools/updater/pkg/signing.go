package pkg

import (
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/pem"
	"fmt"
)

// Sign signs a message using a private key.
func Sign(privateKey []byte, message string) ([]byte, error) {
	block, _ := pem.Decode(privateKey)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing private key")
	}

	key, err := x509.ParsePKCS8PrivateKey(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse private key: %v", err)
	}

	hasher := sha256.New()
	hasher.Write([]byte(message))
	hashed := hasher.Sum(nil)

	signature, err := rsa.SignPKCS1v15(rand.Reader, key.(*rsa.PrivateKey), crypto.SHA256, hashed)
	if err != nil {
		return nil, fmt.Errorf("failed to sign message: %v", err)
	}

	return signature, nil
}

// Verify verifies a message using a public key and a signature.
func Verify(publicKey []byte, message string, signature []byte) error {
	block, _ := pem.Decode(publicKey)
	if block == nil {
		return fmt.Errorf("failed to decode PEM block containing public key")
	}

	key, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return fmt.Errorf("failed to parse public key: %v", err)
	}

	hasher := sha256.New()
	hasher.Write([]byte(message))
	hashed := hasher.Sum(nil)

	err = rsa.VerifyPKCS1v15(key.(*rsa.PublicKey), crypto.SHA256, hashed, signature)
	if err != nil {
		return fmt.Errorf("failed to verify signature: %v", err)
	}

	return nil
}
