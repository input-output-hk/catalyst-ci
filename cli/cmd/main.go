package main

// cspell: words alecthomas afero sess tfstate

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"strings"
	"sync"
	"text/template"
	"time"

	"github.com/alecthomas/kong"
	"github.com/aws/aws-sdk-go/aws/session"
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
	Images   imagesCmd   `cmd:"" help:"Find the images generated by an Earthfile target."`
	Scan     scanCmd     `cmd:"" help:"Scan for Earthfiles."`
	State    stateCmd    `cmd:"" help:"Fetch outputs from remote Terraform state buckets."`
	Tags     tagsCmd     `cmd:"" help:"Generate image tags with the current git context."`
	Simulate simulateCmd `cmd:"" help:"Simulate earthly commands."`
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
	Paths      []string `                        help:"paths to scan for Earthfiles"                                             arg:"" type:"path"`
	Target     []string `short:"t"               help:"filter by Earthfiles that include this target"                                               default:""`
}

func (c *scanCmd) Run() error {
	parser := parsers.NewEarthlyParser()
	scanner := scanners.NewFileScanner(c.Paths, parser, afero.NewOsFs())

	var err error
	// Target tag is set.
	if len(c.Target) != 0 {
		var fileMapTarget = make(map[string][]string)
		for _, t := range c.Target {
			pathToEarthMap, err := scanner.ScanForTarget(t)

			if err != nil {
				return err
			}

			for key, value := range pathToEarthMap {
				if existingTargets, ok := fileMapTarget[filepath.Dir(key)]; ok {
					fileMapTarget[filepath.Dir(key)] = append(existingTargets, value.Targets...)
				} else {
					fileMapTarget[filepath.Dir(key)] = value.Targets
				}
			}
		}

		err = c.printOutput(fileMapTarget)
		if err != nil {
			return err
		}

	} else {
		files, err := scanner.Scan()
		if err != nil {
			return err
		}
		paths := make([]string, 0)
		for _, file := range files {
			paths = append(paths, filepath.Dir(file.Path))
		}

		err = c.printOutput(paths)
		if err != nil {
			return err
		}
	}

	return nil
}

func (c *scanCmd) printOutput(data interface{}) error {
	if c.JSONOutput {
		jsonOutput, err := json.Marshal(data)
		if err != nil {
			return err
		}
		fmt.Println(string(jsonOutput))
		return nil
	}
	fmt.Println(data)
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

type simulateCmd struct {
	Path   string   `                      help:"path to Earthfile"               arg:"" type:"path"`
	Target []string `short:"t"               help:"Earthly targets pattern"                                               default:"check check-* build test test-*"`
}

func (c *simulateCmd) Run() error {
	parser := parsers.NewEarthlyParser()
	scanner := scanners.NewFileScanner([]string{c.Path}, parser, afero.NewOsFs())

	fmt.Println("Targets: ", c.Target)
	// Loop through target patterns.
	for _, tp := range strings.Fields(c.Target[0]) {
		fmt.Println(">>>>>>> Detecting", tp, "target")
		pathToEarthMap, err := scanner.ScanForTarget(tp)
		if err != nil {
			return err
		}
		for _, e := range pathToEarthMap {
			var wg sync.WaitGroup
			// Loop through filtered targets.
			for _, tg := range e.Targets {
				target := filepath.Join(filepath.Dir(e.Earthfile.Path), "+"+tg)
				fmt.Println(">>> Running target", target)
				wg.Add(1)
				go runEarthlyTarget(&wg, target)
			}
			// Wait for all goroutines to finish.
			wg.Wait()
		}

		fmt.Println("Command executed successfully.")
	}
	return nil
}

// Run Earthly with target.
func runEarthlyTarget(wg *sync.WaitGroup, earthlyCmd string) {
	defer wg.Done()
	command := "earthly"

	// Create the command
	cmd := exec.Command(command, earthlyCmd)

	var stdoutBuf, stderrBuf bytes.Buffer
	cmd.Stdout = io.MultiWriter(os.Stdout, &stdoutBuf)
	cmd.Stderr = io.MultiWriter(os.Stderr, &stderrBuf)

	err := cmd.Run()
	if err != nil {
		log.Fatalf("cmd.Run() failed with %s\n", err)
	}
	outStr, errStr := stdoutBuf.String(), stderrBuf.String()
	fmt.Printf("\nout:\n%s\nerr:\n%s\n", outStr, errStr)
}

func main() {
	ctx := kong.Parse(&cli)
	err := ctx.Run()
	ctx.FatalIfErrorf(err)
	os.Exit(0)
}
