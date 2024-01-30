package pkg_test

// cspell: words afero cuelang cuecontext

import (
	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/spf13/afero"
)

var _ = Describe("Cue", func() {
	Describe("ReadFile", func() {
		var fs afero.Fs

		BeforeEach(func() {
			fs = afero.NewMemMapFs()
		})

		When("the file exists", func() {
			It("returns a cue.Value", func() {
				err := afero.WriteFile(fs, "foo.cue", []byte("foo: 1"), 0644)
				Expect(err).ToNot(HaveOccurred())

				ctx := cuecontext.New()
				v, err := pkg.ReadFile(ctx, "foo.cue", fs)
				Expect(err).ToNot(HaveOccurred())
				Expect(v).ToNot(BeNil())
			})
		})

		When("the file does not exist", func() {
			It("returns an error", func() {
				ctx := cuecontext.New()

				_, err := pkg.ReadFile(ctx, "foo.cue", fs)
				Expect(err).To(HaveOccurred())
			})
		})
	})

	Describe("UpdateFile", func() {
		var fs afero.Fs

		When("updating a file", func() {
			BeforeEach(func() {
				fs = afero.NewMemMapFs()
			})

			When("the file exists", func() {
				BeforeEach(func() {
					err := afero.WriteFile(fs, "foo.cue", []byte("foo: 1"), 0644)
					Expect(err).ToNot(HaveOccurred())
				})

				When("the path exists", func() {
					It("updates the file", func() {
						src, err := pkg.UpdateFile("foo.cue", "foo", 2, fs)
						Expect(err).ToNot(HaveOccurred())

						ctx := cuecontext.New()
						v := ctx.CompileBytes(src)
						Expect(v.LookupPath(cue.ParsePath("foo")).Int64()).To(Equal(int64(2)))
					})
				})

				When("the path does not exist", func() {
					It("returns an error", func() {
						_, err := pkg.UpdateFile("foo.cue", "bar", 2, fs)
						Expect(err).To(HaveOccurred())
					})
				})
			})

			When("the file does not exist", func() {
				It("returns an error", func() {
					_, err := pkg.UpdateFile("foo.cue", "foo", 2, fs)
					Expect(err).To(HaveOccurred())
				})
			})
		})
	})
})
