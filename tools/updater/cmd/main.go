package main

// cspell: words afero alecthomas cuelang cuecontext cuectx existingfile mheers Timoni nolint

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path"
	"strings"

	"github.com/alecthomas/kong"
	"github.com/input-output-hk/catalyst-ci/tools/updater/pkg"
	"github.com/spf13/afero"
)

var cli struct {
	Scan   scanCmd   `cmd:"" help:"Scans a directory for deployment files."`
	Update updateCmd `cmd:"" help:"Overrides a target path in a CUE file with the given value."`
}

type updateCmd struct {
	Bundle      updateBundleCmd      `cmd:"" help:"Overrides a target path in a Timoni bundle values field with the given value."`
	Deployments updateDeploymentsCmd `cmd:"" help:"Performs a mass update on Timoni bundle files using given input data."`
	File        updateFileCmd        `cmd:"" help:"Overrides a target path in a CUE file with the given value."`
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

type updateBundleCmd struct {
	BundleFile string `type:"existingfile" short:"f" help:"Path to the bundle file to update." required:"true"`
	Instance   string `short:"i" help:"The instance to update." required:"true"`
	InPlace    bool   `help:"Update the file in place."`
	Path       string `arg:"" help:"A dot separated path to the value to update (must already exist)."`
	Value      string `arg:"" help:"The value to updates the value at the path with."`
}

func (c *updateBundleCmd) Run() error {
	path := fmt.Sprintf("bundle.instances.%s.values.%s", c.Instance, c.Path)

	src, err := pkg.UpdateFile(c.BundleFile, path, c.Value, afero.NewOsFs())
	if err != nil {
		return err
	}

	if c.InPlace {
		if err := os.WriteFile(c.BundleFile, src, 0644); err != nil { //nolint:gosec
			return fmt.Errorf("failed to write file %q: %v", c.BundleFile, err)
		}
	} else {
		fmt.Print(string(src))
	}

	return nil
}

type updateDeploymentsCmd struct {
	RootDir     string `arg:"" type:"existingdir" help:"The root directory where Timoni bundle files are located." required:"true"`
	Environment string `short:"e" help:"The environment to update." required:"true"`
	Input       string `short:"i" help:"The path to the input data file (can be passed via stdin)."`
}

func (c *updateDeploymentsCmd) Run() error {
	var data []byte

	_, err := os.Stat(c.Input)
	if os.IsNotExist(err) {
		data, err = io.ReadAll(os.Stdin)
		if err != nil {
			return fmt.Errorf("failed to read input data: %v", err)
		}
	} else {
		data, err = os.ReadFile(c.Input)
		if err != nil {
			return fmt.Errorf("failed to read input data from %s: %v", c.Input, err)
		}
	}

	overrides := []pkg.OverrideConfig{}
	if err := json.Unmarshal(data, &overrides); err != nil {
		return fmt.Errorf("failed to parse input data: %v", err)
	}

	for _, override := range overrides {
		bundlePath := path.Join(c.RootDir, c.Environment, override.App, "bundle.cue")
		if _, err := os.Stat(bundlePath); os.IsNotExist(err) {
			return fmt.Errorf("bundle file %q does not exist", bundlePath)
		}

		var path string
		if override.Instance == "" {
			path = fmt.Sprintf("bundle.instances.%s.values.%s", override.App, override.Path)
		} else {
			path = fmt.Sprintf("bundle.instances.%s.values.%s", override.Instance, override.Path)
		}

		src, err := pkg.UpdateFile(bundlePath, path, override.Value, afero.NewOsFs())
		if err != nil {
			return fmt.Errorf("failed to update bundle file %q: %v", bundlePath, err)
		}

		if err := os.WriteFile(bundlePath, src, 0644); err != nil { //nolint:gosec
			return fmt.Errorf("failed to write bundle file %q: %v", bundlePath, err)
		}
	}

	return nil
}

type updateFileCmd struct {
	File    string `type:"existingfile" short:"f" help:"Path to the CUE file to update." required:"true"`
	InPlace bool   `help:"Update the file in place."`
	Path    string `arg:"" help:"A dot separated path to the value to update (must already exist)."`
	Value   string `arg:"" help:"The value to updates the value at the path with."`
}

func (c *updateFileCmd) Run() error {
	src, err := pkg.UpdateFile(c.File, c.Path, c.Value, afero.NewOsFs())
	if err != nil {
		return err
	}

	if c.InPlace {
		if err := os.WriteFile(c.File, src, 0644); err != nil { //nolint:gosec
			return fmt.Errorf("failed to write file %q: %v", c.File, err)
		}
	} else {
		fmt.Print(string(src))
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
