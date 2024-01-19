import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'
import * as github from '@actions/github'
import { run } from './install'

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
jest.mock('@actions/github', () => ({
  getOctokit: jest.fn()
}))

describe('Setup Action', () => {
  const token = 'token'
  const version = '1.0.0'

  // actions core mocks
  const getInputMock = core.getInput as jest.Mock
  const setFailedMock = core.setFailed as jest.Mock

  // actions tool-cache mocks
  const downloadToolMock = tc.downloadTool as jest.Mock
  const extractTarMock = tc.extractTar as jest.Mock

  // actions github mocks
  const getOctokitMock = github.getOctokit as jest.Mock

  describe('when installing the CLI binary', () => {
    describe('when the platform is not linux', () => {
      it('should fail', async () => {
        await run('darwin')

        expect(setFailedMock).toHaveBeenCalledWith(
          'This action only supports Linux runners'
        )
      })
    })

    describe('when the platform is linux', () => {
      const platform = 'linux'

      describe('when the version is invalid', () => {
        beforeAll(() => {
          getInputMock.mockImplementation((name: string) => {
            switch (name) {
              case 'token':
                return token
              case 'version':
                return 'invalid'
              default:
                throw new Error(`Unknown input ${name}`)
            }
          })
        })

        it('should fail', async () => {
          await run(platform)
          expect(setFailedMock).toHaveBeenCalledWith('Invalid version')
        })
      })

      describe('when the version is valid', () => {
        beforeAll(() => {
          getInputMock.mockImplementation((name: string) => {
            switch (name) {
              case 'token':
                return token
              case 'version':
                return version
              default:
                throw new Error(`Unknown input ${name}`)
            }
          })
        })

        describe('when the version does not exist', () => {
          beforeAll(() => {
            getOctokitMock.mockReturnValue({
              rest: {
                repos: {
                  listReleases: jest.fn().mockResolvedValue({
                    data: []
                  })
                }
              }
            })
          })

          it('should fail', async () => {
            await run(platform)
            expect(setFailedMock).toHaveBeenCalledWith(
              `Version ${version} not found`
            )
          })
        })

        describe('when the version exists', () => {
          describe('when the assets is not found', () => {
            beforeAll(() => {
              getOctokitMock.mockReturnValue({
                rest: {
                  repos: {
                    listReleases: jest.fn().mockResolvedValue({
                      data: [
                        {
                          // eslint-disable-next-line camelcase
                          tag_name: `v${version}`,
                          assets: []
                        }
                      ]
                    })
                  }
                }
              })
            })

            it('should fail', async () => {
              await run(platform)
              expect(setFailedMock).toHaveBeenCalledWith(
                `Asset for version v${version} not found`
              )
            })
          })

          describe('when the assets is found', () => {
            beforeAll(() => {
              getOctokitMock.mockReturnValue({
                rest: {
                  repos: {
                    listReleases: jest.fn().mockResolvedValue({
                      data: [
                        {
                          // eslint-disable-next-line camelcase
                          tag_name: `v2.0.0`,
                          assets: [
                            {
                              name: 'cli-linux-amd64.tar.gz',
                              // eslint-disable-next-line camelcase
                              browser_download_url: 'https://example2.com'
                            }
                          ]
                        },
                        {
                          // eslint-disable-next-line camelcase
                          tag_name: `v${version}`,
                          assets: [
                            {
                              name: 'cli-linux-amd64.tar.gz',
                              // eslint-disable-next-line camelcase
                              browser_download_url: 'https://example.com'
                            }
                          ]
                        }
                      ]
                    })
                  }
                }
              })
            })

            it('should download the asset', async () => {
              await run(platform)

              expect(downloadToolMock).toHaveBeenCalledWith(
                'https://example.com'
              )
            })

            it('should extract the asset', async () => {
              downloadToolMock.mockResolvedValue('/tmp/file.tar.gz')
              await run(platform)

              expect(extractTarMock).toHaveBeenCalledWith(
                '/tmp/file.tar.gz',
                '/usr/local/bin'
              )
            })

            describe('when the download fails', () => {
              beforeAll(() => {
                downloadToolMock.mockRejectedValue(new Error('Download error'))
              })

              it('should fail', async () => {
                await run(platform)
                expect(setFailedMock).toHaveBeenCalledWith('Download error')
              })
            })

            describe('when the version is latest', () => {
              beforeAll(() => {
                getInputMock.mockImplementation((name: string) => {
                  switch (name) {
                    case 'token':
                      return token
                    case 'version':
                      return 'latest'
                    default:
                      throw new Error(`Unknown input ${name}`)
                  }
                })
              })

              it('should download the latest version', async () => {
                await run(platform)
                expect(downloadToolMock).toHaveBeenCalledWith(
                  'https://example2.com'
                )
              })
            })
          })
        })
      })
    })
  })
})
