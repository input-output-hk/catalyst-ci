package pkg

import "fmt"

// typeMap maps artifact types to their corresponding file names.
var TypeMap = map[string]string{
	"genesis": "block0.bin",
	"vit":     "database.sqlite3",
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
	var key string
	if version == "" {
		key = fmt.Sprintf("%s/%s/%s", f.Environment, f.Fund, TypeMap[artifactType])
	} else {
		key = fmt.Sprintf("%s/%s/%s-%s", f.Environment, f.Fund, TypeMap[artifactType], version)
	}

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
