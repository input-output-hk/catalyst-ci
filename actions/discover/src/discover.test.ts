import * as core from '@actions/core'
import { getExecOutput } from '@actions/exec'
import { run } from './discover'

jest.mock('@actions/core', () => ({
  getInput: jest.fn(),
  setOutput: jest.fn()
}))

// Reusable function to set up mock for getExecOutput
const mockGetExecOutput = (stdout: string): void => {
  const mock = getExecOutput as jest.Mock
  mock.mockResolvedValueOnce({ stdout })
  return
}

describe('Discover Action', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  const testCases = [
    {
      paths: 'path1 path2',
      targets: 'target1 target2',
      expectedCommand: "ci scan -j -t target1 -t target2 'path1 path2'",
      expectedJson: '{"/path1": ["target1"], "/path2": ["target2"]}',
      expectedPaths: ['/path1', '/path2']
    },
    {
      paths: 'path1',
      targets: 'target1',
      expectedCommand: 'ci scan -j -t target1 path1',
      expectedJson: '{"/path1": ["target1"]}',
      expectedPaths: ['/path1']
    },
    {
      paths: '.',
      targets: '',
      expectedCommand: 'ci scan -j .',
      expectedJson: '{}',
      expectedPaths: []
    },
    {
      paths: '.',
      targets: 'target target-*',
      expectedCommand: 'ci scan -j -t target -t target-* .',
      expectedJson:
        '{"/path1": ["target"], "/path2": ["target", "target-1", "target-2"], "/path3": ["target-1", "target-2"]}',
      expectedPaths: ['/path1', '/path2', '/path3']
    }
  ]

  it.each(testCases)(
    'should execute the correct command',
    async ({
      paths,
      targets,
      expectedCommand,
      expectedJson,
      expectedPaths
    }) => {
      const getInputMock = core.getInput as jest.Mock
      getInputMock.mockImplementation((name: string) => {
        switch (name) {
          case 'paths':
            return paths
          case 'targets':
            return targets
          default:
            return ''
        }
      })

      mockGetExecOutput(expectedJson)
      await run()

      expect(getExecOutput).toHaveBeenCalledWith(expectedCommand)
      expect(core.setOutput).toHaveBeenCalledWith('json', expectedJson)
      expect(core.setOutput).toHaveBeenCalledWith('paths', expectedPaths)
    }
  )
})
