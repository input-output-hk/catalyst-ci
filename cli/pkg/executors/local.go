package executors

import "os/exec"

type LocalExecutor struct {
	Path string
}

func (l LocalExecutor) Run(args ...string) (string, error) {
	// #nosec G204 - We are not using user input here.
	cmd := exec.Command(l.Path, args...)
	out, err := cmd.Output()
	return string(out), err
}

func NewLocalExecutor(path string) LocalExecutor {
	return LocalExecutor{
		Path: path,
	}
}
