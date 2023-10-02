package pkg

import (
	"encoding/json"
	"fmt"
)

/*
 * State is an opportunistic representation of the terraform remote state file.
 * It is not guaranteed to be complete, but it is sufficient for the purpose of
 * extracting the outputs from the state file.
 */
type State struct {
	Version          uint8             `json:"version"`
	TerraformVersion string            `json:"terraform_version"`
	Serial           uint64            `json:"serial"`
	Lineage          string            `json:"lineage"`
	Outputs          map[string]Output `json:"outputs"`
	Resources        []any             `json:"resources"`
	CheckResults     []any             `json:"check_results"`
}

// ParseOutput parses the output with the given key into the given value.
func (s State) ParseOutput(key string, v interface{}) error {
	output, ok := s.Outputs[key]
	if !ok {
		return fmt.Errorf("output %s not found in state", key)
	}

	return json.Unmarshal(output.Value, v)
}

// cspell: words unmarshalled

/*
 * Output is a representation of an output from a terraform state file. The
 * value is kept as a json.RawMessage so that it can be unmarshalled into the
 * appropriate type.
 */
type Output struct {
	Value     json.RawMessage `json:"value"`
	Type      string          `json:"type"`
	Sensitive bool            `json:"sensitive,omitempty"`
}

// StateProvider is an interface for managing remote Terraform state files.
type StateProvider interface {
	// FetchState fetches the state file from the remote location.
	Fetch(bucket string, key string) (State, error)
}
