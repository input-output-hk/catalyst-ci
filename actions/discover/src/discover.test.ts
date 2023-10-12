import * as core from '@actions/core'
import { exec } from 'child_process'
import { run } from './discover'

jest.mock('@actions/core', () => ({
  getBooleanInput: jest.fn(),
  getInput: jest.fn(),
  setFailed: jest.fn(),
  setOutput: jest.fn(),
  info: jest.fn()
}))
jest.mock('child_process', () => ({
  exec: jest.fn(
    (
      _,
      callback: (_error: Error | null, _stdout: string, _stderr: string) => void
    ) => {
      callback(null, 'mocked output', '')
    }
  )
}))

describe('Discover Action', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('when testing running the ci command', () => {
    const testCases = [
      {
        parseImages: true,
        paths: 'path1 path2',
        targets: 'target1 target2',
        expectedCommand: "ci scan -ji -t target1 -t target2 'path1 path2'"
      },
      {
        parseImages: false,
        paths: 'path1',
        targets: 'target1',
        expectedCommand: 'ci scan -j -t target1 path1'
      },
      {
        parseImages: false,
        paths: '.',
        targets: '',
        expectedCommand: 'ci scan -j .'
      }
    ]

    // actions mocks
    const getBooleanInputMock = core.getBooleanInput as jest.Mock
    const getInputMock = core.getInput as jest.Mock

    it.each(testCases)(
      'should execute the correct command',
      async ({ parseImages, paths, targets, expectedCommand }) => {
        getBooleanInputMock.mockReturnValue(parseImages)
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

        await run()

        expect(exec).toHaveBeenCalledWith(expectedCommand, expect.anything())
        expect(core.setOutput).toHaveBeenCalledWith('json', 'mocked output')
      }
    )
  })
})
