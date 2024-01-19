package main

// cspell: words alecthomas cuelang cuecontext cuectx existingfile Timoni nolint

import (
	"os"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/format"
	"github.com/alecthomas/kong"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
)

var cli struct {
	BundleFile string `type:"existingfile" short:"b" help:"Path to the Timoni bundle file to modify." required:"true"`
	Path       string `arg:"" help:"A dot separated path to the value to override (must already exist)."`
	Value      string `arg:"" help:"The value to override the value at the path with."`
}

func main() {
	ctx := kong.Parse(&cli,
		kong.Name("updater"),
		kong.Description("A helper tool for modifying CUE files to override arbitrary values. Useful for updating Timoni bundles."))

	cuectx := cuecontext.New()
	v, err := pkg.ReadFile(cuectx, cli.BundleFile)
	ctx.FatalIfErrorf(err)

	if !v.LookupPath(cue.ParsePath(cli.Path)).Exists() {
		ctx.Fatalf("path %q does not exist", cli.Path)
	}

	v, err = pkg.FillPathOverride(cuectx, v, cli.Path, cli.Value)
	ctx.FatalIfErrorf(err)

	node := v.Syntax(cue.Final(), cue.Concrete(true))
	src, err := format.Node(node)
	ctx.FatalIfErrorf(err)

	if err := os.WriteFile(cli.BundleFile, src, 0644); err != nil { //nolint:gosec
		ctx.Fatalf("failed to write file %q: %v", cli.BundleFile, err)
	}

	os.Exit(0)
}
