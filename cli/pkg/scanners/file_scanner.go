package scanners

// cspell: words afero

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/input-output-hk/catalyst-ci/cli/pkg"
	"github.com/spf13/afero"
)

// FileScanner is an interface that can scan for Earthfiles at the given paths.
type FileScanner struct {
	fs     afero.Fs
	parser pkg.EarthfileParser
	paths  []string
}

func (f *FileScanner) Scan() ([]pkg.Earthfile, error) {
	earthfiles, err := f.scan(func(e pkg.Earthfile) (bool, error) {
		return true, nil
	})
	if err != nil {
		return nil, err
	}

	return earthfiles, nil
}

func (f *FileScanner) ScanForTarget(target string) (map[string]pkg.EarthTargets, error) {
	regexPattern := getTargetRegex(target)
	r, err := regexp.Compile(regexPattern)

	if err != nil {
		return nil, err
	}

	earthfileToTargets := make(map[string]pkg.EarthTargets)

	_, err = f.scan(func(e pkg.Earthfile) (bool, error) {
		var targets []string
		for _, t := range e.Targets {
			// Matched target is added to a list.
			if r.MatchString(t.Name) {
				targets = append(targets, t.Name)
			}
		}
		// If there are filtered targets, add to a map.
		if len(targets) != 0 {
			earthfileToTargets[e.Path] = pkg.EarthTargets{
				Earthfile: e,
				Targets:   targets,
			}
			return true, nil
		}
		return false, nil
	})

	if err != nil {
		return nil, err
	}

	return earthfileToTargets, nil
}

func getTargetRegex(target string) string {
	// If target ends with -*
	if strings.HasSuffix(target, "-*") {
		// Should start with given target
		// followed by hyphen and followed by one or more lowercase letters or numbers
		return fmt.Sprintf("^%s-(?:[a-z0-9]+)?$", regexp.QuoteMeta(target[:len(target)-2]))
	}

	// Match the exact target
	return fmt.Sprintf("^%s$", regexp.QuoteMeta(target))
}

func (f *FileScanner) scan(
	filter func(pkg.Earthfile) (bool, error),
) ([]pkg.Earthfile, error) {
	var earthfiles []pkg.Earthfile
	for _, path := range f.paths {
		if walkErr := afero.Walk(f.fs, path, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}

			// Filter to Earthfiles
			if filepath.Base(path) != "Earthfile" {
				return nil
			}

			earthfile, parseErr := f.parser.Parse(path)
			if parseErr != nil {
				return parseErr
			}

			include, filterErr := filter(earthfile)
			if filterErr != nil {
				return filterErr
			}
			if include {
				earthfiles = append(earthfiles, earthfile)
			}

			return nil
		}); walkErr != nil {
			return nil, walkErr
		}
	}

	return earthfiles, nil
}

// NewFileScanner creates a new FileScanner.
func NewFileScanner(
	paths []string,
	parser pkg.EarthfileParser,
	fs afero.Fs,
) *FileScanner {
	return &FileScanner{
		fs:     fs,
		parser: parser,
		paths:  paths,
	}
}
