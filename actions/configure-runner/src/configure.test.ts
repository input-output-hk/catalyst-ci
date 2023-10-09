import * as core from '@actions/core'
import * as fs from 'fs/promises'
import * as os from 'os'
import * as yaml from 'js-yaml'
import { GetSecretValueCommand } from '@aws-sdk/client-secrets-manager'
import { run } from './configure'

// cspell: words camelcase tlskey tlsca tlscert

jest.mock('@actions/core', () => ({
  getInput: jest.fn(),
  info: jest.fn(),
  setFailed: jest.fn()
}))

jest.mock('fs/promises', () => ({
  access: jest.fn(),
  mkdir: jest.fn(),
  writeFile: jest.fn()
}))

jest.mock('os', () => ({
  homedir: jest.fn()
}))

const mockedSecretsManagerClient = {
  send: jest.fn()
}
jest.mock('@aws-sdk/client-secrets-manager', () => ({
  SecretsManagerClient: jest.fn(() => mockedSecretsManagerClient),
  GetSecretValueCommand: jest.fn()
}))

describe('Configure Action', () => {
  const certWritePath = '/tmp/certs'
  const secretName = 'some/secret'

  // actions mocks
  const getInputMock = core.getInput as jest.Mock

  // fs mocks
  const accessMock = fs.access as jest.Mock
  const mkdirMock = fs.mkdir as jest.Mock
  const writeFileMock = fs.writeFile as jest.Mock

  // os mocks
  const homedirMock = os.homedir as jest.Mock

  beforeAll(() => {
    getInputMock.mockImplementation((name: string) => {
      switch (name) {
        case 'path':
          return certWritePath
        case 'secret':
          return secretName
        default:
          throw new Error(`Unknown input ${name}`)
      }
    })
  })

  describe('when configuring the runner', () => {
    beforeEach(() => {
      accessMock.mockResolvedValue(undefined)
      writeFileMock.mockResolvedValue(undefined)
      homedirMock.mockReturnValue('/home/runner')
      mockedSecretsManagerClient.send.mockResolvedValue({
        SecretString: JSON.stringify({
          ca_certificate: 'ca', // eslint-disable-line camelcase
          certificate: 'cert',
          private_key: 'key' // eslint-disable-line camelcase
        })
      })
    })

    describe('when creating the certificate folder', () => {
      describe('when the folder exists', () => {
        it('should not create the folder', async () => {
          await run()
          expect(mkdirMock).not.toHaveBeenCalled()
        })
      })

      describe('when the folder does not exist', () => {
        it('should create the folder', async () => {
          accessMock.mockRejectedValue(undefined)
          await run()
          expect(mkdirMock).toHaveBeenCalledWith(certWritePath, {
            recursive: true
          })
        })
      })

      describe("when the folder can't be created", () => {
        it('should fail the action', async () => {
          accessMock.mockRejectedValue(undefined)
          mkdirMock.mockRejectedValue(undefined)
          await run()
          expect(core.setFailed).toHaveBeenCalledWith(
            `Failed creating directory ${certWritePath}`
          )
        })
      })
    })

    describe('when getting the secret', () => {
      it('should fetch the correct secret', async () => {
        await run()
        expect(mockedSecretsManagerClient.send).toHaveBeenCalledWith(
          new GetSecretValueCommand({ SecretId: secretName })
        )
      })

      describe('when the secret is unavailable', () => {
        it('should fail the action', async () => {
          mockedSecretsManagerClient.send.mockRejectedValue(
            new Error('Invalid secret')
          )
          await run()
          expect(core.setFailed).toHaveBeenCalledWith('Invalid secret')
        })
      })

      describe('when the secret value is invalid', () => {
        it('should fail the action', async () => {
          mockedSecretsManagerClient.send.mockResolvedValue({
            SecretString: 'invalid'
          })
          await run()
          expect(core.setFailed).toHaveBeenCalledWith(
            `Unexpected token 'i', "invalid" is not valid JSON`
          )
        })
      })
    })

    describe('when writing the certificate files', () => {
      it('should write them to the correct location', async () => {
        await run()
        expect(writeFileMock).toHaveBeenCalledWith(
          `${certWritePath}/ca.pem`,
          'ca'
        )
        expect(writeFileMock).toHaveBeenCalledWith(
          `${certWritePath}/cert.pem`,
          'cert'
        )
        expect(writeFileMock).toHaveBeenCalledWith(
          `${certWritePath}/key.pem`,
          'key'
        )
      })

      describe('when the files cannot be written', () => {
        it('should fail the action', async () => {
          writeFileMock.mockRejectedValue(new Error('Failed writing files'))
          await run()
          expect(core.setFailed).toHaveBeenCalledWith('Failed writing files')
        })
      })
    })

    describe('when writing the earthly config', () => {
      it('should write it to the correct location', async () => {
        await run()
        expect(writeFileMock).toHaveBeenCalledWith(
          `/home/runner/.earthly/config.yml`,
          yaml.dump({
            global: {
              tlskey: `${certWritePath}/key.pem`,
              tlsca: `${certWritePath}/ca.pem`,
              tlscert: `${certWritePath}/cert.pem`
            }
          })
        )
      })

      describe('when the config cannot be written', () => {
        it('should fail the action', async () => {
          writeFileMock.mockRejectedValue(new Error('Failed writing config'))
          await run()
          expect(core.setFailed).toHaveBeenCalledWith('Failed writing config')
        })
      })
    })
  })
})
