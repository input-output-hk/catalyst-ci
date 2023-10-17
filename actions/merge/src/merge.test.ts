import * as core from '@actions/core'
import * as fs from 'fs'
import { run } from './merge'

jest.mock('@actions/core', () => {
  return {
    getInput: jest.fn(),
    info: jest.fn(),
    setFailed: jest.fn()
  }
})
jest.mock('fs', () => ({
  promises: {
    readFile: jest.fn(),
    writeFile: jest.fn()
  }
}))

describe('Merge Action', () => {
  // actions mocks
  const getInputMock = core.getInput as jest.Mock
  const setFailedMock = core.setFailed as jest.Mock

  // fs mocks
  const readFileMock = fs.promises.readFile as jest.Mock
  const writeFileMock = fs.promises.writeFile as jest.Mock

  beforeAll(() => {
    getInputMock.mockImplementation((name: string) => {
      switch (name) {
        case 'hash':
          return 'hash'
        case 'hash_file':
          return 'hash_file'
        case 'images':
          return 'image1\nimage2\nimage3'
        default:
          return ''
      }
    })
  })

  describe('when merging hashes', () => {
    beforeAll(() => {
      readFileMock.mockImplementation(() => {
        return JSON.stringify({
          image1: 'old_hash',
          image2: 'old_hash',
          image4: 'old_hash'
        })
      })
    })

    it('should read the hash file', async () => {
      await run()

      expect(readFileMock).toHaveBeenCalledTimes(1)
      expect(readFileMock).toHaveBeenCalledWith('hash_file', 'utf8')
    })

    it('should write the merged hashes', async () => {
      await run()

      expect(writeFileMock).toHaveBeenCalledTimes(1)
      expect(writeFileMock).toHaveBeenCalledWith(
        'hash_file',
        JSON.stringify({
          image1: 'hash',
          image2: 'hash',
          image3: 'hash',
          image4: 'old_hash'
        })
      )
    })
  })

  describe('when reading the hash file fails', () => {
    beforeAll(() => {
      readFileMock.mockImplementation(() => {
        throw new Error('read error')
      })
    })

    it('should fail', async () => {
      await run()

      expect(setFailedMock).toHaveBeenCalledTimes(1)
      expect(setFailedMock).toHaveBeenCalledWith('read error')
    })
  })

  describe('when writing the hash file fails', () => {
    beforeAll(() => {
      readFileMock.mockImplementation(() => {
        return JSON.stringify({
          image1: 'old_hash',
          image2: 'old_hash',
          image4: 'old_hash'
        })
      })
      writeFileMock.mockImplementation(() => {
        throw new Error('write error')
      })
    })

    it('should fail', async () => {
      await run()

      expect(setFailedMock).toHaveBeenCalledTimes(1)
      expect(setFailedMock).toHaveBeenCalledWith('write error')
    })
  })
})
