package pkg

import "fmt"

type ArchiveFetcher struct {
	Environment string
	Store       Store
}

func (f *ArchiveFetcher) Fetch(id string) ([]byte, error) {
	key := fmt.Sprintf("%s/%s", f.Environment, id)
	return f.Store.Fetch(key)
}

func NewArchiveFetcher(environment string, store Store) ArchiveFetcher {
	return ArchiveFetcher{
		Environment: environment,
		Store:       store,
	}
}
