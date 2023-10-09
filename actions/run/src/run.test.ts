import * as core from '@actions/core'
import { spawn, SpawnOptionsWithoutStdio } from 'child_process'
import { run } from './run'

jest.mock('@actions/core', () => ({
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
        artifactOutput: '',
        earthfile: 'earthfile',
        flags: '',
        output: '',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '--flag1 test -f2 test2',
        command: ['earthfile+target', '--flag1', 'test', '-f2', 'test2'],
        images: '',
        artifacts: ''
      },
      {
        artifact: 'artifact',
        artifactOutput: 'out',
        earthfile: 'earthfile',
        flags: '',
        output: 'Artifact +target/artifact output as out\n',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '',
        command: ['--artifact', 'earthfile+target/artifact', 'out'],
        images: '',
        artifacts: 'out'
      },
      {
        artifact: '',
        artifactOutput: '',
        earthfile: 'earthfile',
        flags: '',
        output: '',
        runnerAddress: 'localhost',
        runnerPort: '8372',
        target: 'target',
        targetFlags: '',
        command: [
          '--buildkit-host',
          'tcp://localhost:8372',
          'earthfile+target'
        ],
        images: '',
        artifacts: ''
      },
      {
        artifact: '',
        artifactOutput: '',
        earthfile: 'earthfile',
        flags: '--flag1 test -f2 test2',
        output:
          'Image +docker output as image1:tag1\nImage +docker output as image2:tag2\n',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '',
        command: ['--flag1', 'test', '-f2', 'test2', 'earthfile+target'],
        images: 'image1:tag1 image2:tag2',
        artifacts: ''
      }
    ])(
      `should execute the correct command`,
      async ({
        artifact,
        artifactOutput,
        earthfile,
        flags,
        output,
        runnerAddress,
        runnerPort,
        target,
        targetFlags,
        command,
        images,
        artifacts
      }) => {
        const getInputMock = core.getInput as jest.Mock
        getInputMock.mockImplementation((name: string) => {
          switch (name) {
            case 'artifact':
              return artifact
            case 'artifact_output':
              return artifactOutput
            case 'earthfile':
              return earthfile
            case 'flags':
              return flags
            case 'output':
              return output
            case 'runner_address':
              return runnerAddress
            case 'runner_port':
              return runnerPort
            case 'target':
              return target
            case 'target_flags':
              return targetFlags
            default:
              throw new Error('Unknown input')
          }
        })

        const spawnMock = spawn as jest.Mock
        spawnMock.mockImplementation(createSpawnMock('stdout', output, 0))

        await run()

        expect(spawn).toHaveBeenCalledTimes(1)
        expect(spawn).toHaveBeenCalledWith('earthly', command)
        expect(stdoutSpy).toHaveBeenCalledWith('stdout')
        expect(stderrSpy).toHaveBeenCalledWith(output)
        expect(core.setOutput).toHaveBeenCalledWith('images', images)
        expect(core.setOutput).toHaveBeenCalledWith('artifacts', artifacts)
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
