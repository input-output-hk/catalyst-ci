package parsers_test

// cspell: words onsi gomega

import (
	"context"
	"errors"

	"github.com/earthly/earthly/ast/spec"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/parsers"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

type mockAstParser struct {
	ef  spec.Earthfile
	err error
}

func (m mockAstParser) Parse(
	_ context.Context,
	_ string,
	_ bool,
) (spec.Earthfile, error) {
	return m.ef, m.err
}

var _ = Describe("EarthlyParser", func() {
	Describe("Parse", func() {
		It("should parse the Earthfile and return the pkg.Earthfile", func() {
			mock := mockAstParser{
				ef: spec.Earthfile{Targets: []spec.Target{{Name: "target"}}},
			}
			parser := parsers.EarthlyParser{AstParser: mock}
			expectedPath := "/path/to/Earthfile"

			earthfile, err := parser.Parse(expectedPath)

			Expect(err).ToNot(HaveOccurred())
			Expect(earthfile.Path).To(Equal(expectedPath))
			Expect(earthfile.Targets).To(HaveLen(1))
			Expect(earthfile.Targets[0].Name).To(Equal("target"))
		})

		It("should return an error if the ast parser fails", func() {
			mock := mockAstParser{err: errors.New("parse error")}
			parser := parsers.EarthlyParser{AstParser: mock}

			_, err := parser.Parse("/path/to/Earthfile")

			Expect(err).To(HaveOccurred())
			Expect(err.Error()).To(Equal("parse error"))
		})
	})
})
