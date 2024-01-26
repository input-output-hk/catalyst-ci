package pkg

// cspell: words cuelang

import (
	"fmt"
	"os"

	"cuelang.org/go/cue"
)

// ReadFile reads a CUE file and returns a cue.Value.
func ReadFile(ctx *cue.Context, path string) (cue.Value, error) {
	contents, err := os.ReadFile(path)
	if err != nil {
		return cue.Value{}, fmt.Errorf("failed to read file %q: %w", path, err)
	}

	v := ctx.CompileBytes(contents)
	if err := v.Err(); err != nil {
		return cue.Value{}, fmt.Errorf("failed to compile CUE file %q: %w", path, err)
	}

	return v, nil
}
