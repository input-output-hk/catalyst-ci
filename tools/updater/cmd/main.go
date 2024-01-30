package main

// cspell: words afero alecthomas cuelang cuecontext cuectx existingfile mheers Timoni nolint

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/format"
	"github.com/alecthomas/kong"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	ch "github.com/mheers/cue-helper/pkg/value"
	"github.com/spf13/afero"
)

var cli struct {
	Scan   scanCmd   `cmd:"" help:"Scans a directory for deployment files."`
	Update updateCmd `cmd:"" help:"Overrides a target path in a CUE file with the given value."`
}

type scanCmd struct {
	Path     string   `arg:"" help:"The path to scan for deployment files." type:"existingdir" required:"true"`
	Template []string `short:"t" help:"A key/value pair used to override constant values in deployment configurations."`
}

func (c *scanCmd) Run() error {
	files, err := pkg.ScanForDeploymentFiles(c.Path, afero.NewOsFs())
	if err != nil {
		return err
	}

	overrides := []pkg.OverrideConfig{}
	for _, file := range files {
		overrides = append(overrides, file.Overrides...)
	}

	for _, template := range c.Template {
		pair := strings.Split(template, "=")
		pkg.ApplyTemplateValue(overrides, pair[0], pair[1])
	}

	output, err := json.Marshal(overrides)
	if err != nil {
		return fmt.Errorf("failed to marshal overrides: %v", err)
	}

	fmt.Print(string(output))

	return nil
}

type updateCmd struct {
	BundleFile string `type:"existingfile" short:"b" help:"Path to the Timoni bundle file to modify." required:"true"`
	Path       string `arg:"" help:"A dot separated path to the value to override (must already exist)."`
	Value      string `arg:"" help:"The value to override the value at the path with."`
}

func (c *updateCmd) Run() error {
	cuectx := cuecontext.New()
	v, err := pkg.ReadFile(cuectx, c.BundleFile, afero.NewOsFs())
	if err != nil {
		return err
	}

	if !v.LookupPath(cue.ParsePath(c.Path)).Exists() {
		return fmt.Errorf("path %q does not exist", c.Path)
	}

	v, err = ch.Replace(v, c.Path, c.Value)
	if err != nil {
		return err
	}

	node := v.Syntax(cue.Final(), cue.Concrete(true), cue.Docs(true))
	src, err := format.Node(node)
	if err != nil {
		return err
	}

	if err := os.WriteFile(c.BundleFile, src, 0644); err != nil { //nolint:gosec
		return fmt.Errorf("failed to write file %q: %v", c.BundleFile, err)
	}

	return nil
}

func main() {
	ctx := kong.Parse(&cli,
		kong.Name("updater"),
		kong.Description("A helper tool for modifying CUE files to override arbitrary values. Useful for updating Timoni bundles."))

	err := ctx.Run()
	ctx.FatalIfErrorf(err)
	os.Exit(0)
}
