package pkg_test

import (
	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("Cue", func() {
	Describe("FillPathOverride", func() {
		var path, str string

		When("given a nested CUE source", func() {
			When("the path exists", func() {
				BeforeEach(func() {
					path = "bundles.instances.module.values.image.tag"
					str = `
					bundle: {
						instances: {
							module: {
								values: {
									image: tag: "test"
								}
							}
						}
					}
				`
				})

				It("should override the value at the given path", func() {
					ctx := cuecontext.New()
					v := ctx.CompileString(str)

					v, err := pkg.FillPathOverride(ctx, v, path, "test1")
					Expect(err).ToNot(HaveOccurred())

					result, err := v.LookupPath(cue.ParsePath(path)).String()
					Expect(err).ToNot(HaveOccurred())
					Expect(result).To(Equal("test1"))
				})
			})

			When("the path does not include structs", func() {
				BeforeEach(func() {
					path = "bundles.instances.module.values.image.tag"
					str = `
					bundles: {
						instances: {
							module: "test"
						}
					}
				`
				})

				It("should return an error", func() {
					ctx := cuecontext.New()
					v := ctx.CompileString(str)

					_, err := pkg.FillPathOverride(ctx, v, path, "test1")
					Expect(err).To(HaveOccurred())
				})
			})
		})
	})
})
