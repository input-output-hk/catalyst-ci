import * as core from '@actions/core'
import { spawn, SpawnOptionsWithoutStdio } from 'child_process'
import { run } from './run'

jest.mock('@actions/core', () => ({
  getBooleanInput: jest.fn(),
  getInput: jest.fn(),
  info: jest.fn(),
  setOutput: jest.fn()
}))
jest.mock('child_process', () => ({
  spawn: jest.fn()
}))
const stdoutSpy = jest
  .spyOn(process.stdout, 'write')
  .mockImplementation(() => true)
const stderrSpy = jest
  .spyOn(process.stderr, 'write')
  .mockImplementation(() => true)

describe('Run Action', () => {
  describe('when testing running the earthly command', () => {
    it.each([
      {
        artifact: '',
        artifactPath: '',
        earthfile: './earthfile',
        flags: '',
        githubToken: 'token',
        platform: '',
        privileged: '',
        output: '',
        runnerAddress: '',
        runnerPort: '',
        targets: 'target',
        targetFlags: '--flag1 test -f2 test2',
        command: [['./earthfile+target', '--flag1', 'test', '-f2', 'test2']],
        imageOutput: '',
        artifactOutput: ''
      },
      {
        artifact: 'true',
        artifactPath: 'out',
        earthfile: './earthfile',
        flags: '--test',
        githubToken: 'token',
        platform: '',
        privileged: '',
        output: 'Artifact +target/artifact output as out\n',
        runnerAddress: '',
        runnerPort: '',
        targets: 'target',
        targetFlags: '',
        command: [['--test', '--artifact', './earthfile+target/', 'out']],
        imageOutput: '',
        artifactOutput: 'earthfile/out'
      },
      {
        artifact: '',
        artifactPath: '',
        earthfile: './earthfile',
        flags: '',
        githubToken: 'token',
        platform: '',
        privileged: '',
        output: '',
        runnerAddress: 'localhost',
        runnerPort: '8372',
        targets: 'target',
        targetFlags: '',
        command: [
          ['--buildkit-host', 'tcp://localhost:8372', './earthfile+target']
        ],
        imageOutput: '',
        artifactOutput: ''
      },
      {
        artifact: '',
        artifactPath: '',
        earthfile: './earthfile',
        flags: '--flag1 test -f2 test2',
        githubToken: 'token',
        platform: 'linux/amd64',
        privileged: 'true',
        output: 'Image +docker output as image1:tag1\n',
        runnerAddress: '',
        runnerPort: '',
        targets: 'target',
        targetFlags: '',
        command: [
          [
            '-P',
            '--platform',
            'linux/amd64',
            '--flag1',
            'test',
            '-f2',
            'test2',
            './earthfile+target'
          ]
        ],
        imageOutput: 'image1:tag1',
        artifactOutput: ''
      },
      {
        artifact: '',
        artifactPath: '',
        earthfile: './targets/earthfile',
        flags: '',
        githubToken: 'token',
        platform: 'linux/amd64',
        privileged: 'true',
        output: '',
        runnerAddress: '',
        runnerPort: '',
        targets: 'target target-test',
        targetFlags: '',
        command: [
          ['-P', '--platform', 'linux/amd64', './targets/earthfile+target'],
          ['-P', '--platform', 'linux/amd64', './targets/earthfile+target-test']
        ],
        imageOutput: '',
        artifactOutput: ''
      }
    ])(
      `should execute the correct command`,
      async ({
        artifact,
        artifactPath,
        earthfile,
        flags,
        githubToken,
        platform,
        privileged,
        output,
        runnerAddress,
        runnerPort,
        targets,
        targetFlags,
        command,
        imageOutput,
        artifactOutput
      }) => {
        const getInputMock = core.getInput as jest.Mock
        const getBooleanInputMock = core.getBooleanInput as jest.Mock
        getInputMock.mockImplementation((name: string) => {
          switch (name) {
            case 'artifact_path':
              return artifactPath
            case 'earthfile':
              return earthfile
            case 'flags':
              return flags
            case 'githubToken':
              return githubToken
            case 'platform':
              return platform
            case 'privileged':
              return privileged
            case 'output':
              return output
            case 'runner_address':
              return runnerAddress
            case 'runner_port':
              return runnerPort
            case 'targets':
              return targets
            case 'target_flags':
              return targetFlags
            default:
              throw new Error('Unknown input')
          }
        })

        getBooleanInputMock.mockImplementation((name: string) => {
          switch (name) {
            case 'artifact':
              return artifact === 'true'
            case 'privileged':
              return privileged === 'true'
            default:
              throw new Error('Unknown input')
          }
        })

        const spawnMock = spawn as jest.Mock
        spawnMock.mockImplementation(createSpawnMock('stdout', output, 0))

        await run()

        expect(spawn).toHaveBeenCalledTimes(command.length)
        command.map(cmd => {
          expect(spawn).toHaveBeenCalledWith('earthly', cmd, {
            env: {
              GITHUB_TOKEN: githubToken
            }
          })
        })
        expect(stdoutSpy).toHaveBeenCalledWith('stdout')
        expect(stderrSpy).toHaveBeenCalledWith(output)

        if (imageOutput) {
          // eslint-disable-next-line jest/no-conditional-expect
          expect(core.setOutput).toHaveBeenCalledWith('image', imageOutput)
        }

        if (artifact === 'true') {
          // eslint-disable-next-line jest/no-conditional-expect
          expect(core.setOutput).toHaveBeenCalledWith(
            'artifact',
            artifactOutput
          )
        }
      }
    )
  })
})

function createSpawnMock(stdout: string, stderr: string, code: number) {
  return (
    _command: string,
    _args?: readonly string[] | undefined,
    _options?: SpawnOptionsWithoutStdio | undefined
  ) => {
    return {
      stdout: {
        on: (event: string, listener: (_data: string) => void) => {
          listener(stdout)
        }
      },
      stderr: {
        on: (event: string, listener: (_data: string) => void) => {
          listener(stderr)
        }
      },
      on: jest.fn(
        (
          event: 'close',
          listener: (
            _code: number | null,
            _signal: NodeJS.Signals | null
          ) => void
        ) => {
          listener(code, null)
        }
      )
    }
  }
}
