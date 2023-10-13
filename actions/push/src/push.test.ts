import * as core from '@actions/core'
import * as exec from '@actions/exec'
import { run } from './push'

jest.mock('@actions/core', () => ({
  getInput: jest.fn(),
  info: jest.fn(),
  setFailed: jest.fn()
}))
jest.mock('@actions/exec', () => ({
  exec: jest.fn()
}))

describe('Discover Action', () => {
  // actions mocks
  const getInputMock = core.getInput as jest.Mock
  const setFailedMock = core.setFailed as jest.Mock
  const execMock = exec.exec as jest.Mock

  describe('when pushing to multiple registries with multiple tags', () => {
    beforeAll(() => {
      getInputMock.mockImplementation((name: string) => {
        switch (name) {
          case 'image':
            return 'image:latest'
          case 'registries':
            return 'registry1\nregistry2'
          case 'tags':
            return 'tag1\ntag2'
          default:
            return ''
        }
      })
    })

    it('should push to all registries with all tags', async () => {
      await run()

      expect(execMock).toHaveBeenCalledTimes(8)
      expect(execMock).toHaveBeenNthCalledWith(1, 'docker', [
        'tag',
        'image:latest',
        'registry1/image:tag1'
      ])
      expect(execMock).toHaveBeenNthCalledWith(2, 'docker', [
        'push',
        'registry1/image:tag1'
      ])
      expect(execMock).toHaveBeenNthCalledWith(3, 'docker', [
        'tag',
        'image:latest',
        'registry1/image:tag2'
      ])
      expect(execMock).toHaveBeenNthCalledWith(4, 'docker', [
        'push',
        'registry1/image:tag2'
      ])
      expect(execMock).toHaveBeenNthCalledWith(5, 'docker', [
        'tag',
        'image:latest',
        'registry2/image:tag1'
      ])
      expect(execMock).toHaveBeenNthCalledWith(6, 'docker', [
        'push',
        'registry2/image:tag1'
      ])
      expect(execMock).toHaveBeenNthCalledWith(7, 'docker', [
        'tag',
        'image:latest',
        'registry2/image:tag2'
      ])
      expect(execMock).toHaveBeenNthCalledWith(8, 'docker', [
        'push',
        'registry2/image:tag2'
      ])
    })

    describe('when exec fails', () => {
      beforeAll(() => {
        execMock.mockImplementation(() => {
          throw new Error('exec error')
        })
      })

      it('should set failed', async () => {
        await run()

        expect(setFailedMock).toHaveBeenCalledTimes(1)
        expect(setFailedMock).toHaveBeenCalledWith('exec error')
      })
    })
  })
})
