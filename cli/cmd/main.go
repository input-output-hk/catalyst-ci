package main

// cspell: words alecthomas afero sess tfstate

import (
	"encoding/json"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"strings"
	"text/template"
	"time"

	"github.com/alecthomas/kong"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/input-output-hk/catalyst-ci/cli/pkg"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/executors"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/git"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/parsers"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/providers"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/scanners"
	"github.com/input-output-hk/catalyst-ci/cli/pkg/util"
	"github.com/spf13/afero"
)

// TagTemplate is a template for generating image tags.
type TagTemplate struct {
	Hash      string
	Timestamp string
	Version   string
}

var cli struct {
	Images imagesCmd      `cmd:"" help:"Find the images generated by an Earthfile target."`
	Scan   scanCmd        `cmd:"" help:"Scan for Earthfiles."`
	State  stateCmd       `cmd:"" help:"Fetch outputs from remote Terraform state buckets."`
	Tags   tagsCmd        `cmd:"" help:"Generate image tags with the current git context."`
	Find   findTargetsCmd `cmd:"" help:"Find targets from an Earthfile"`
}

type imagesCmd struct {
	JSONOutput bool   `short:"j" long:"json" help:"Output in JSON format"`
	Path       string `                      help:"path to Earthfile"               arg:"" type:"path"`
	Target     string `short:"t"             help:"The target to search for images"                    required:"true"`
}

func (c *imagesCmd) Run() error {
	parser := parsers.NewEarthlyParser()
	earthfile, err := parser.Parse(c.Path)
	if err != nil {
		return err
	}

	images, err := earthfile.GetImages(c.Target)
	if err != nil {
		return err
	}

	if c.JSONOutput {
		jsonImages, err := json.Marshal(images)
		if err != nil {
			return err
		}
		fmt.Println(string(jsonImages))
		return nil
	}

	for _, image := range images {
		fmt.Println(image)
	}

	return nil
}

type scanCmd struct {
	JSONOutput bool     `short:"j" long:"json"   help:"Output in JSON format"`
	Images     bool     `short:"i" long:"images" help:"Also output images for the target of each Earthfile (requires -t option)"`
	Paths      []string `                        help:"paths to scan for Earthfiles"                                             arg:"" type:"path"`
	Target     string   `short:"t"               help:"filter by Earthfiles that include this target"                                               default:""`
}

func (c *scanCmd) Run() error {
	parser := parsers.NewEarthlyParser()
	scanner := scanners.NewFileScanner(c.Paths, parser, afero.NewOsFs())

	var files []pkg.Earthfile
	var err error
	if c.Target != "" {
		pathToEarthMap, _ := scanner.ScanForTarget(c.Target)

		if err != nil {
			return err
		}
		for _, value := range pathToEarthMap {
			files = append(files, value.Earthfile)
		}

	} else {
		files, err = scanner.Scan()
	}

	if err != nil {
		return err
	}

	if c.Images {
		if c.Target == "" {
			return fmt.Errorf(
				"the --images (-i) option requires the --target (-t) option",
			)
		}

		var output = make(map[string][]string)

		for _, file := range files {
			images, err := file.GetImages(c.Target)
			if err != nil {
				return err
			}

			output[filepath.Dir(file.Path)] = images
		}

		if c.JSONOutput {
			var outFinal []interface{}
			for path, images := range output {
				out := struct {
					Images []string `json:"images"`
					Path   string   `json:"path"`
				}{
					Images: images,
					Path:   path,
				}
				outFinal = append(outFinal, out)
			}
			jsonOutput, err := json.Marshal(outFinal)
			if err != nil {
				return err
			}
			fmt.Println(string(jsonOutput))
		} else {
			for path, images := range output {
				fmt.Printf("%s %s\n", path, strings.Join(images, ","))
			}
		}

		return nil
	}

	if c.JSONOutput {
		paths := make([]string, 0)
		for _, file := range files {
			paths = append(paths, filepath.Dir(file.Path))
		}

		jsonFiles, err := json.Marshal(paths)
		if err != nil {
			return err
		}
		fmt.Println(string(jsonFiles))
	} else {
		for _, file := range files {
			fmt.Println(filepath.Dir(file.Path))
		}
	}

	return nil
}

type stateCmd struct {
	Bucket      string `short:"b" long:"bucket"      help:"S3 bucket that state is stored in"         env:"CI_STATE_BUCKET" required:"true"`
	Environment string `short:"e" long:"environment" help:"The target environment to fetch state for" env:"CI_ENVIRONMENT"  required:"true"`
	Key         string `                             help:"key to fetch"                                                    required:"true" arg:""`
	Output      string `short:"o" long:"output"      help:"The name of the output to return"`
}

func (c *stateCmd) Run() error {
	// Load AWS credentials from the default profile.
	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	provider := providers.NewRemoteStateProvider(sess)
	key := path.Join(c.Environment, c.Key, "terraform.tfstate")

	state, err := provider.Fetch(c.Bucket, key)
	if err != nil {
		return err
	}

	var result string
	if c.Output == "" {
		outputs, err := json.Marshal(state.Outputs)
		if err != nil {
			return err
		}

		result = string(outputs)
	} else {
		if _, ok := state.Outputs[c.Output]; !ok {
			return fmt.Errorf("output %s not found", c.Output)
		}

		outputs, err := json.Marshal(state.Outputs[c.Output])
		if err != nil {
			return err
		}

		result = string(outputs)
	}

	fmt.Println(result)

	return nil
}

type tagsCmd struct {
	TemplateString string `arg:"" help:"template for generating image tags" default:"{{ .Hash }}"`
}

func (c *tagsCmd) Run() error {
	executor := executors.NewLocalExecutor("git")
	client := git.NewExternalGitClient(executor)

	// Collect the highest version from the git tags
	tags, err := client.Tags()
	if err != nil {
		return err
	}
	highest := util.GetHighestVersion(tags)

	// Get the current git commit hash
	hash, err := executor.Run("rev-parse", "HEAD")
	if err != nil {
		return err
	}

	// Get the current timestamp
	timestamp := time.Now().Format("20060102150405")

	// Generate the tag
	tmpl, err := template.New("tag").Parse(c.TemplateString)
	if err != nil {
		return err
	}

	data := TagTemplate{
		Hash:      hash,
		Timestamp: timestamp,
		Version:   highest,
	}
	err = tmpl.Execute(os.Stdout, data)
	if err != nil {
		return err
	}

	return nil
}

type findTargetsCmd struct {
	Paths  string `                        help:"Path of an Earthfile"                                             arg:"" type:"path"`
	Target string `short:"t"             help:"Target pattern to find in Earthfile"                    required:"true"`
}

func (c *findTargetsCmd) Run() error {
	parser := parsers.NewEarthlyParser()
	scanner := scanners.NewFileScanner([]string{c.Paths}, parser, afero.NewOsFs())

	var pathToEarthMap map[string]pkg.EarthTargets
	var err error
	if c.Target != "" {
		pathToEarthMap, err = scanner.ScanForTarget(c.Target)
	}

	if err != nil {
		return err
	}
	jsonOutput, err := json.Marshal(pathToEarthMap[c.Paths].Targets)
	if err != nil {
		return err
	}
	fmt.Println(string(jsonOutput))
	return nil
}

func main() {
	ctx := kong.Parse(&cli)
	err := ctx.Run()
	ctx.FatalIfErrorf(err)
	os.Exit(0)
}
