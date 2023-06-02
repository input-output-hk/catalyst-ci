package pkg

// SatelliteCertificates is a struct that contains the certificates required to
// connect to a remote Earthly satellite.
type SatelliteCertificates struct {
	CACertificate string `json:"ca_certificate"`
	Certificate   string `json:"certificate"`
	PrivateKey    string `json:"private_key"`
}

// SatelliteCertificatesFetcher is an interface that allows us to fetch the
// certificates required to connect to a remote Earthly satellite.
type SatelliteCertificatesFetcher interface {
	// FetchCertificates fetches the certificates required to connect to a remote
	// Earthly satellite.
	FetchCertificates() (SatelliteCertificates, error)
}

// SatelliteConfiguration is a struct that contains the partial configuration
// required to connect to a remote Earthly satellite.
type SatelliteConfiguration struct {
	Global SatelliteGlobalConfiguration `json:"global"`
}

// SatelliteGlobalConfiguration is a struct that contains the global
// configuration required to connect to a remote Earthly satellite.
type SatelliteGlobalConfiguration struct {
	TLSCA   string `yaml:"tlsca"`
	TLSCert string `yaml:"tlscert"`
	TLSKey  string `yaml:"tlskey"`
}
