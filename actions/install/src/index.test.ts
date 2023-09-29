import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'
import { run } from './setup'

jest.mock('@actions/core', () => {
  return {
    getInput: jest.fn(),
    info: jest.fn(),
    setFailed: jest.fn()
  }
})
jest.mock('@actions/tool-cache', () => ({
  downloadTool: jest.fn(),
  extractTar: jest.fn()
}))

describe('Setup Action', () => {
  it('should download and extract the tool', async () => {
    const mockDownloadTool = tc.downloadTool as jest.MockedFunction<
      typeof tc.downloadTool
    >
    const mockExtractTar = tc.extractTar as jest.MockedFunction<
      typeof tc.extractTar
    >
    const mockGetInput = core.getInput as jest.MockedFunction<
      typeof core.getInput
    >
    mockGetInput.mockReturnValueOnce('1.0.0')
    mockDownloadTool.mockResolvedValueOnce(
      '/tmp/omashu-1.0.0-linux_amd64.tar.gz'
    )

    await run()

    const expectedUrl =
      'https://github.com/meigma/omashu/releases/download/v1.0.0/omashu-1.0.0-linux_amd64.tar.gz'
    expect(mockDownloadTool).toHaveBeenCalledWith(expectedUrl)
    expect(mockExtractTar).toHaveBeenCalledWith(
      '/tmp/omashu-1.0.0-linux_amd64.tar.gz',
      '/usr/local/bin'
    )
  })

  it('should handle errors gracefully', async () => {
    const mockDownloadTool = tc.downloadTool as jest.MockedFunction<
      typeof tc.downloadTool
    >
    const mockGetInput = core.getInput as jest.MockedFunction<
      typeof core.getInput
    >
    mockGetInput.mockReturnValueOnce('1.0.0')
    mockDownloadTool.mockRejectedValueOnce(new Error('Download error'))

    await run()

    expect(core.setFailed).toHaveBeenCalledWith('Download error')
  })
})
