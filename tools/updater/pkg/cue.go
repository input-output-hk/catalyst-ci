package pkg

// cspell: words afero cuelang

import (
	"fmt"

	"cuelang.org/go/cue"
	"github.com/spf13/afero"
)

// ReadFile reads a CUE file and returns a cue.Value.
func ReadFile(ctx *cue.Context, path string, os afero.Fs) (cue.Value, error) {
	contents, err := afero.ReadFile(os, path)
	if err != nil {
		return cue.Value{}, fmt.Errorf("failed to read file %q: %w", path, err)
	}

	v := ctx.CompileBytes(contents)
	if err := v.Err(); err != nil {
		return cue.Value{}, fmt.Errorf("failed to compile CUE file %q: %w", path, err)
	}

	return v, nil
}
