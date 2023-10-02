package executors_test

// cspell: words onsi gomega

import (
	"errors"
	"os/exec"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"github.com/input-output-hk/catalyst-ci/cli/pkg/executors"
)

var _ = Describe("LocalExecutor", func() {
	Describe("Run", func() {
		It("should execute the command and return the output", func() {
			executor := executors.NewLocalExecutor("echo")
			expectedOutput := "Hello, world!\n"

			output, err := executor.Run("-n", expectedOutput)
			Expect(err).ToNot(HaveOccurred())
			Expect(output).To(Equal(expectedOutput))
		})

		It("should return an error if the command fails", func() {
			executor := executors.NewLocalExecutor("does_not_exist")

			_, err := executor.Run()
			Expect(err).To(HaveOccurred())
			Expect(errors.Is(err, exec.ErrNotFound)).To(BeTrue())
		})
	})
})
