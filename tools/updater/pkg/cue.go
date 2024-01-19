package pkg

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"cuelang.org/go/cue"
)

// FillPathOverride is like cue.Value.FillPath, but it allows you to override concrete values.
// The default behavior of CUE is to support immutable values, so you can't normally override a concrete value.
// This function first converts the cue.Value to JSON, then to a map, and then modifies the map.
// Finally, it converts the map back to JSON and then to a cue.Value.
func FillPathOverride(ctx *cue.Context, v cue.Value, path string, value interface{}) (cue.Value, error) {
	j, err := v.MarshalJSON()
	if err != nil {
		return cue.Value{}, fmt.Errorf("failed to marshal cue.Value to JSON: %w", err)
	}

	var data map[string]interface{}
	if err := json.Unmarshal(j, &data); err != nil {
		return cue.Value{}, fmt.Errorf("failed to unmarshal JSON to map: %w", err)
	}

	if err := setField(data, path, value); err != nil {
		return cue.Value{}, fmt.Errorf("failed to set field %q to value %v: %w", path, value, err)
	}

	modifiedJSON, err := json.Marshal(data)
	if err != nil {
		return cue.Value{}, fmt.Errorf("failed to marshal map to JSON: %w", err)
	}

	return ctx.CompileBytes(modifiedJSON), nil
}

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

// setField sets the value at the given path in a map, creating nested maps as necessary.
func setField(m map[string]interface{}, path string, value interface{}) error {
	parts := strings.Split(path, ".")
	for i, part := range parts {
		if i == len(parts)-1 {
			m[part] = value
		} else {
			if _, ok := m[part]; !ok {
				m[part] = make(map[string]interface{})
			}
			var ok bool
			m, ok = m[part].(map[string]interface{})
			if !ok {
				return fmt.Errorf("invalid path: %s", path)
			}
		}
	}
	return nil
}
