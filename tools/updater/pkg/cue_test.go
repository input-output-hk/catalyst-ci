package pkg_test

// cspell: words afero cuelang cuecontext

import (
	"cuelang.org/go/cue/cuecontext"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/spf13/afero"
)

var _ = Describe("Cue", func() {
	Describe("ReadFile", func() {
		var os afero.Fs

		BeforeEach(func() {
			os = afero.NewMemMapFs()
		})

		When("the file exists", func() {
			It("returns a cue.Value", func() {
				afero.WriteFile(os, "foo.cue", []byte("foo: 1"), 0644)
				ctx := cuecontext.New()

				v, err := pkg.ReadFile(ctx, "foo.cue", os)
				Expect(err).ToNot(HaveOccurred())
				Expect(v).ToNot(BeNil())
			})
		})

		When("the file does not exist", func() {
			It("returns an error", func() {
				ctx := cuecontext.New()

				_, err := pkg.ReadFile(ctx, "foo.cue", os)
				Expect(err).To(HaveOccurred())
			})
		})
	})
})
