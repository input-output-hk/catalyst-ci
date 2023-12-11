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
		DescribeTable("when Earthfile contain valid docker targets",
			func(target string) {
				setup(target)
				fScanner := scanners.NewFileScanner([]string{"/test"}, parser, fs)
				earthfiles, err := fScanner.ScanForTarget("docker")
				Expect(err).NotTo(HaveOccurred())
				Expect(earthfiles).To(HaveLen(1))
				Expect(earthfiles[0].Path).To(Equal("/test/Earthfile"))

			},
			Entry("target in file is 'docker'", "docker"),
			Entry("target in file is 'docker-<a-z>'", "docker-test"),
			Entry("target in file is 'docker-<1-9>'", "docker-2test"),
		)
		DescribeTable("when Earthfile contain invalid docker target or no target",
			func(target string) {
				setup(target)
				fScanner := scanners.NewFileScanner([]string{"/test"}, parser, fs)
				earthfiles, err := fScanner.ScanForTarget("docker")
				Expect(err).NotTo(HaveOccurred())
				Expect(earthfiles).To(BeEmpty())

			},
			Entry("target in file doesn't start with docker", "testdocker"),
			Entry("target in file start with docker with hyphen but not followed by one or more lowercase letters or numbers ", "docker-"),
			Entry("target in file start with docker with hyphen followed by special character", "docker-@"),
			Entry("target in file start with docker with hyphen followed capital letter", "docker-TEST"),
			Entry("no match target", "other"),
		)
	})
})
