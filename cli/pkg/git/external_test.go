package git_test

import (
	"errors"

	"github.com/input-output-hk/catalyst-ci/cli/pkg/git"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("Tags", func() {
	It("should return a list of tags", func() {
		ex := &mockExecutor{
			commandOutput: "v1.0.0\nv1.1.0\nv1.2.0",
		}
		c := git.NewExternalGitClient(ex)

		tags, err := c.Tags()
		Expect(err).ToNot(HaveOccurred())
		Expect(tags).To(Equal([]string{"v1.0.0", "v1.1.0", "v1.2.0"}))
	})

	It("should return an error if the executor returns an error", func() {
		ex := &mockExecutor{
			commandOutput: "",
			err:           errors.New("failed to run command"),
		}
		c := git.NewExternalGitClient(ex)

		tags, err := c.Tags()
		Expect(err).To(HaveOccurred())
		Expect(tags).To(BeNil())
	})
})
