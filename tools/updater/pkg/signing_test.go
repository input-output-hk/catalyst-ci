package pkg_test

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"

	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("Signing", func() {
	var privKey []byte
	var pubKey []byte

	BeforeEach(func() {
		privateKeyRaw, err := rsa.GenerateKey(rand.Reader, 2048)
		Expect(err).ToNot(HaveOccurred())

		privateKeyDer, err := x509.MarshalPKCS8PrivateKey(privateKeyRaw)
		Expect(err).ToNot(HaveOccurred())
		privateKeyBlock := &pem.Block{
			Type:  "RSA PRIVATE KEY",
			Bytes: privateKeyDer,
		}
		privKey = pem.EncodeToMemory(privateKeyBlock)

		publicKey := &privateKeyRaw.PublicKey
		publicKeyDer, err := x509.MarshalPKIXPublicKey(publicKey)
		Expect(err).ToNot(HaveOccurred())

		publicKeyBlock := &pem.Block{
			Type:  "PUBLIC KEY",
			Bytes: publicKeyDer,
		}
		pubKey = pem.EncodeToMemory(publicKeyBlock)
	})

	Describe("Sign", func() {
		When("signing a message", func() {
			When("The private key is valid", func() {
				It("returns a signature", func() {
					signature, err := pkg.Sign(privKey, "message")
					Expect(err).ToNot(HaveOccurred())
					Expect(signature).ToNot(BeNil())
				})
			})

			When("The private key is invalid", func() {
				It("returns an error", func() {
					signature, err := pkg.Sign([]byte("invalid"), "message")
					Expect(err).To(HaveOccurred())
					Expect(signature).To(BeNil())
				})
			})
		})
	})

	Describe("Verify", func() {
		When("verifying a message", func() {
			var message string
			var signature []byte

			BeforeEach(func() {
				message = "message"

				var err error
				signature, err = pkg.Sign(privKey, message)
				Expect(err).ToNot(HaveOccurred())
			})

			When("The public key and signature are valid", func() {
				It("returns nil", func() {
					err := pkg.Verify(pubKey, message, signature)
					Expect(err).ToNot(HaveOccurred())
				})
			})

			When("The public key is invalid", func() {
				It("returns an error", func() {
					err := pkg.Verify([]byte("invalid"), message, signature)
					Expect(err).To(HaveOccurred())
				})
			})

			When("The signature is invalid", func() {
				It("returns an error", func() {
					err := pkg.Verify(pubKey, message, []byte("invalid"))
					Expect(err).To(HaveOccurred())
				})
			})
		})
	})
})
