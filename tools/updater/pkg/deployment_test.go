package pkg_test

import (
	"fmt"

	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/spf13/afero"
	"gopkg.in/yaml.v3"
)

var _ = Describe("Deployment", func() {
	Describe("ScanForDeploymentFiles", func() {
		var fs afero.Fs

		When("scanning a directory with valid deployment files", func() {
			BeforeEach(func() {
				fs = afero.NewMemMapFs()

				Expect(fs.MkdirAll("files", 0755)).To(Succeed())
				for i := range []int{1, 2, 3} {
					DeploymentFile := pkg.DeploymentFile{
						Overrides: []pkg.OverrideConfig{
							{
								App:   "foo",
								Path:  "bar",
								Value: "baz",
							},
						},
					}

					contents, err := yaml.Marshal(DeploymentFile)
					Expect(err).NotTo(HaveOccurred())

					Expect(fs.MkdirAll(fmt.Sprintf("files/%d", i), 0755)).To(Succeed())
					Expect(afero.WriteFile(fs, fmt.Sprintf("files/%d/deployment.yml", i), contents, 0644)).To(Succeed())
				}
			})

			It("should return a list of all deployment files", func() {
				files, err := pkg.ScanForDeploymentFiles("files", fs)
				Expect(err).NotTo(HaveOccurred())
				Expect(files).To(HaveLen(3))
			})

			It("should correctly parse the deployment files", func() {
				files, err := pkg.ScanForDeploymentFiles("files", fs)
				Expect(err).NotTo(HaveOccurred())

				for _, file := range files {
					Expect(file.Overrides).To(HaveLen(1))
					Expect(file.Overrides[0].App).To(Equal("foo"))
					Expect(file.Overrides[0].Path).To(Equal("bar"))
					Expect(file.Overrides[0].Value).To(Equal("baz"))
				}
			})
		})

		When("scanning a directory with an invalid deployment file", func() {
			BeforeEach(func() {
				fs = afero.NewMemMapFs()

				Expect(fs.MkdirAll("files", 0755)).To(Succeed())
				for i := range []int{1, 2} {
					DeploymentFile := pkg.DeploymentFile{
						Overrides: []pkg.OverrideConfig{
							{
								App:   "foo",
								Path:  "bar",
								Value: "baz",
							},
						},
					}

					contents, err := yaml.Marshal(DeploymentFile)
					Expect(err).NotTo(HaveOccurred())

					Expect(fs.MkdirAll(fmt.Sprintf("files/%d", i), 0755)).To(Succeed())
					Expect(afero.WriteFile(fs, fmt.Sprintf("files/%d/deployment.yml", i), contents, 0644)).To(Succeed())
				}

				Expect(afero.WriteFile(fs, "files/deployment.yml", []byte("invalid"), 0644)).To(Succeed())
			})

			It("should ignore the invalid file", func() {
				files, err := pkg.ScanForDeploymentFiles("files", fs)
				Expect(err).NotTo(HaveOccurred())
				Expect(files).To(HaveLen(2))
			})
		})
	})

	Describe("ApplyTemplateValue", func() {
		var overrides []pkg.OverrideConfig
		When("applying a template value to a list of overrides", func() {
			BeforeEach(func() {
				overrides = []pkg.OverrideConfig{
					{
						App:   "foo",
						Path:  "bar",
						Value: "baz",
					},
					{
						App:   "foo",
						Path:  "bar",
						Value: "qux",
					},
				}
			})

			It("should update the value of the override with the given key", func() {
				pkg.ApplyTemplateValue(overrides, "baz", "qux")
				Expect(overrides[0].Value).To(Equal("qux"))
				Expect(overrides[1].Value).To(Equal("qux"))
			})
		})
	})
})
