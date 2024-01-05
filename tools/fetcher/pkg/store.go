package pkg

// Store is an interface for fetching data from an archive/artifact store.
type Store interface {
	// Fetch fetches the given key from the store.
	Fetch(key string) ([]byte, error)
}
