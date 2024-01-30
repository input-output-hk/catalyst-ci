package pkg

// cspell: words afero cuectx cuelang mheers

import (
	"fmt"

	"cuelang.org/go/cue"
	"cuelang.org/go/cue/cuecontext"
	"cuelang.org/go/cue/format"
	ch "github.com/mheers/cue-helper/pkg/value"
	"github.com/spf13/afero"
)

// ReadFile reads a CUE file and returns a cue.Value.
func ReadFile(ctx *cue.Context, path string, fs afero.Fs) (cue.Value, error) {
	contents, err := afero.ReadFile(fs, path)
	if err != nil {
		return cue.Value{}, fmt.Errorf("failed to read file %q: %w", path, err)
	}

	v := ctx.CompileBytes(contents)
	if err := v.Err(); err != nil {
		return cue.Value{}, fmt.Errorf("failed to compile CUE file %q: %w", path, err)
	}

	return v, nil
}

// UpdateFile updates a CUE file at the given path with the given value and returns the updated file contents.
func UpdateFile(filePath, path string, value interface{}, fs afero.Fs) ([]byte, error) {
	v, err := ReadFile(cuecontext.New(), filePath, fs)
	if err != nil {
		return nil, err
	}

	if !v.LookupPath(cue.ParsePath(path)).Exists() {
		return nil, fmt.Errorf("path %q does not exist", path)
	}

	v, err = ch.Replace(v, path, value)
	if err != nil {
		return nil, fmt.Errorf("failed to replace value at path %q: %w", path, err)
	}

	node := v.Syntax(cue.Final(), cue.Concrete(true), cue.Docs(true))
	src, err := format.Node(node)
	if err != nil {
		return nil, fmt.Errorf("failed to format CUE file: %w", err)
	}

	return src, nil
}
