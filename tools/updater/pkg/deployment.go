package pkg

import (
	"fmt"
	"os"

	"github.com/spf13/afero"
	"gopkg.in/yaml.v3"
)

// Filename is the static name of a deployment configuration file.
const Filename = "deployment.yml"

// DeploymentFile represents a deployment configuration file.
type DeploymentFile struct {
	Overrides []OverrideConfig `json:"overrides" yaml:"overrides"`
}

// OverrideConfig represents configuration for overriding a value in a CUE file.
type OverrideConfig struct {
	App      string `json:"app" yaml:"app"`
	Instance string `json:"instance" yaml:"instance"`
	Path     string `json:"path" yaml:"path"`
	Value    string `json:"value" yaml:"value"`
}

// ScanForDeploymentFiles scans a directory for deployment configuration files.
func ScanForDeploymentFiles(dir string, fs afero.Fs) ([]DeploymentFile, error) {

	files := []DeploymentFile{}
	err := afero.Walk(fs, dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}

		if info.Name() == Filename {
			contents, err := afero.ReadFile(fs, path)
			if err != nil {
				return fmt.Errorf("failed to read deployment file at %q: %v", path, err)
			}

			deploymentFile := DeploymentFile{}
			if err := yaml.Unmarshal(contents, &deploymentFile); err != nil {
				// If we can't unmarshal the file, we assume it's not a deployment file and just log a warning.
				fmt.Fprintf(os.Stderr, "warning: failed to parse deployment file %q: %v", path, err)
				return nil
			}

			files = append(files, deploymentFile)
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	return files, nil
}

// ApplyTemplateValue applies a template value to a list of overrides.
func ApplyTemplateValue(overrides []OverrideConfig, key, value string) {
	for i, override := range overrides {
		if override.Value == key {
			overrides[i].Value = value
		}
	}
}
