package main

// cspell: words alecthomas afero sess tfstate

import (
	"fmt"
	"os"

	"github.com/alecthomas/kong"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/input-output-hk/catalyst-ci/tools/fetcher/pkg"
	s "github.com/input-output-hk/catalyst-ci/tools/fetcher/pkg/store"
)

// TagTemplate is a template for generating image tags.
type TagTemplate struct {
	Hash      string
	Timestamp string
	Version   string
}

type CLI struct {
	Backend string `enum:"s3" short:"s" help:"The object store backend to use." default:"s3"`
	Bucket  string `short:"b" help:"The object store bucket to fetch the artifact from." required:"true"`

	Archive  archiveCmd  `cmd:"" help:"Fetch jormungandr blockchain archives."`
	Artifact artifactCmd `cmd:"" help:"Fetch jormungandr or vit-ss artifacts."`
}

type archiveCmd struct {
	Environment string `short:"e" help:"environment to fetch the archive from" required:"true"`
	ID          string `short:"i" help:"id of the archive to fetch"`
	Path        string `help:"path to store the archive" arg:"" type:"path"`
}

func (c *archiveCmd) Run(store pkg.Store) error {
	fetcher := pkg.NewArchiveFetcher(c.Environment, store)
	archive, err := fetcher.Fetch(c.ID)
	if err != nil {
		return fmt.Errorf("failed to fetch archive: %w", err)
	}

	if err := os.WriteFile(c.Path, archive, 0600); err != nil {
		return fmt.Errorf("failed to save archive to disk: %w", err)
	}

	return nil
}

type artifactCmd struct {
	Environment string `short:"e" help:"environment to fetch the artifact from" required:"true"`
	Fund        string `short:"f" help:"fund to fetch the artifact from" required:"true"`
	Path        string `help:"path to store the artifact" arg:"" type:"path"`
	Type        string `enum:"genesis,vit" short:"t" help:"type of artifact to fetch" required:"true"`
	Version     string `short:"v" help:"version of the artifact to fetch"`
}

func (c *artifactCmd) Run(store pkg.Store) error {
	fetcher := pkg.NewArtifactFetcher(c.Environment, c.Fund, store)
	artifact, err := fetcher.Fetch(c.Type, c.Version)
	if err != nil {
		return fmt.Errorf("failed to fetch artifact: %w", err)
	}

	if err := os.WriteFile(c.Path, artifact, 0600); err != nil {
		return fmt.Errorf("failed to save artifact to disk: %w", err)
	}

	return nil
}

func main() {
	cli := &CLI{}
	ctx := kong.Parse(cli)

	var store pkg.Store
	switch cli.Backend {
	case "s3":
		sess := session.Must(session.NewSessionWithOptions(session.Options{
			SharedConfigState: session.SharedConfigEnable,
		}))
		store = s.NewS3Store(cli.Bucket, sess)
	default:
		ctx.Fatalf("unknown backend: %s", cli.Backend)
	}

	ctx.BindTo(store, (*pkg.Store)(nil))
	err := ctx.Run()
	ctx.FatalIfErrorf(err)
	os.Exit(0)
}
