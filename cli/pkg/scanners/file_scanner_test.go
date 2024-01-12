package scanners_test

// cspell: words onsi gomega afero testdocker

import (
	"errors"

	"github.com/earthly/earthly/ast/spec"
	"github.com/input-output-hk/catalyst-ci/cli/pkg"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/scanners"
	"github.com/spf13/afero"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("FileScanner", func() {
	var (
		fs     afero.Fs
		parser pkg.EarthfileParser
	)

	BeforeEach(func() {
		fs = afero.NewMemMapFs()
	})

	Describe("Scan", func() {
		BeforeEach(func() {
			err := afero.WriteFile(
				fs,
				"/test/Earthfile",
				[]byte("target:"),
				0644,
			)
			Expect(err).NotTo(HaveOccurred())

			err = afero.WriteFile(
				fs,
				"/test/pkg/Earthfile",
				[]byte("target:"),
				0644,
			)
			Expect(err).NotTo(HaveOccurred())

			parser = &mockParser{
				earthfile: pkg.Earthfile{},
				err:       nil,
			}
		})

		It("should return Earthfiles", func() {
			fScanner := scanners.NewFileScanner([]string{"/test"}, parser, fs)
			earthfiles, err := fScanner.Scan()
			Expect(err).NotTo(HaveOccurred())
			Expect(earthfiles).To(HaveLen(2))
			Expect(earthfiles[0].Path).To(Equal("/test/Earthfile"))
			Expect(earthfiles[1].Path).To(Equal("/test/pkg/Earthfile"))
		})

		Context("when the parser fails", func() {
			BeforeEach(func() {
				parser = &mockParser{
					earthfile: pkg.Earthfile{},
					err:       errors.New("executor error"),
				}
			})

			It("should return an error", func() {
				fScanner := scanners.NewFileScanner(
					[]string{"/test"},
					parser,
					fs,
				)
				_, err := fScanner.ScanForTarget("docker")
				Expect(err).To(MatchError("executor error"))
			})
		})
	})

	Describe("ScanForTarget", func() {
		setup := func(target string) {
			err := afero.WriteFile(
				fs,
				"/test/Earthfile",
				[]byte(target),
				0644,
			)

			Expect(err).NotTo(HaveOccurred())
			parser = &mockParser{
				earthfile: pkg.Earthfile{
					Targets: []spec.Target{
						{
							Name: target,
						},
					},
				},
			}
		}
		DescribeTable("when Earthfile contain the target",
			func(targetInput string, targetInFile string) {
				setup(targetInFile)
				directory := "/test"
				fScanner := scanners.NewFileScanner([]string{directory}, parser, fs)
				pathToEarthTargets, err := fScanner.ScanForTarget(targetInput)
				Expect(err).NotTo(HaveOccurred())
				Expect(pathToEarthTargets).To(HaveLen(1))
				data := pathToEarthTargets[directory+"/Earthfile"]
				Expect(data).NotTo(BeNil())
				Expect(data.Earthfile.Path).To(Equal(directory + "/Earthfile"))
				Expect(data.Targets).To(Equal([]string{targetInFile}))

			},
			Entry("scanning 'docker', target in file is 'docker'", "docker", "docker"),
			Entry("scanning 'docker-*', target in file is 'docker-test'", "docker-*", "docker-test"),
			Entry("scanning 'docker-*', target in file is 'docker-test-test2'", "docker-*", "docker-test-test2"),
			Entry("scanning 'docker-*', target in file is 'docker-test-test2-test3'", "docker-*", "docker-test-test2-test3"),
		)
		DescribeTable("when Earthfile contain no target",
			func(target string) {
				setup(target)
				fScanner := scanners.NewFileScanner([]string{"/test"}, parser, fs)
				pathToEarthTargets, err := fScanner.ScanForTarget("docker")
				Expect(err).NotTo(HaveOccurred())
				Expect(pathToEarthTargets).To(BeEmpty())

			},
			Entry("scanning 'docker', target in file doesn't match but contain the word docker", "testdocker"),
			Entry("scanning 'docker', no match target", "other"),
		)
	})
})
