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
        platform: '',
        output: '',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '--flag1 test -f2 test2',
        command: ['./earthfile+target', '--flag1', 'test', '-f2', 'test2'],
        imageOutput: '',
        artifactOutput: ''
      },
      {
        artifact: 'true',
        artifactPath: 'out',
        earthfile: './earthfile',
        flags: '--test',
        platform: '',
        output: 'Artifact +target/artifact output as out\n',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '',
        command: ['--test', '--artifact', './earthfile+target/', 'out'],
        imageOutput: '',
        artifactOutput: 'earthfile/out'
      },
      {
        artifact: '',
        artifactPath: '',
        earthfile: './earthfile',
        flags: '',
        platform: '',
        output: '',
        runnerAddress: 'localhost',
        runnerPort: '8372',
        target: 'target',
        targetFlags: '',
        command: [
          '--buildkit-host',
          'tcp://localhost:8372',
          './earthfile+target'
        ],
        imageOutput: '',
        artifactOutput: ''
      },
      {
        artifact: '',
        artifactPath: '',
        earthfile: './earthfile',
        flags: '--flag1 test -f2 test2',
        platform: 'linux/amd64',
        output: 'Image +docker output as image1:tag1\n',
        runnerAddress: '',
        runnerPort: '',
        target: 'target',
        targetFlags: '',
        command: [
          '--platform',
          'linux/amd64',
          '--flag1',
          'test',
          '-f2',
          'test2',
          './earthfile+target'
        ],
        imageOutput: 'image1:tag1',
        artifactOutput: ''
      }
    ])(
      `should execute the correct command`,
      async ({
        artifact,
        artifactPath,
        earthfile,
        flags,
        platform,
        output,
        runnerAddress,
        runnerPort,
        target,
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
            case 'platform':
              return platform
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

        getBooleanInputMock.mockImplementation((name: string) => {
          switch (name) {
            case 'artifact':
              return artifact === 'true'
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
