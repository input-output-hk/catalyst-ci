package pkg

import (
	"fmt"
	"strings"
)

// typeMap maps artifact types to their corresponding file names.
var TypeMap = map[string]string{
	"genesis": "block0-VERSION.bin",
	"vit":     "database-VERSION.sqlite3",
}

// ArtifactFetcher is used to fetch artifacts from a store.
type ArtifactFetcher struct {
	Environment string
	Fund        string
	Store       Store
}

// Fetch fetches the given artifact from the store.
// If id is empty, it will use the base artifact filename with no version suffix.
func (f *ArtifactFetcher) Fetch(artifactType string, version string) ([]byte, error) {
	key := fmt.Sprintf("%s/%s/%s", f.Environment, f.Fund, mkFileName(artifactType, f.Fund, version))
	return f.Store.Fetch(key)
}

// NewArtifactFetcher creates a new ArtifactFetcher.
func NewArtifactFetcher(environment, fund string, store Store) ArtifactFetcher {
	return ArtifactFetcher{
		Environment: environment,
		Fund:        fund,
		Store:       store,
	}
}

func mkFileName(artifactType, fund, version string) string {
	if version == "" {
		return strings.Replace(TypeMap[artifactType], "-VERSION", "", 1)
	}
	return strings.Replace(TypeMap[artifactType], "VERSION", fmt.Sprintf("%s-%s", fund, version), 1)
}
