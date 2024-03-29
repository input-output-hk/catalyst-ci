import * as core from '@actions/core'
import * as fs from 'fs/promises'
import * as os from 'os'
import * as yaml from 'js-yaml'
import {
  GetSecretValueCommand,
  SecretsManagerClient
} from '@aws-sdk/client-secrets-manager'

// cspell: words camelcase tlskey tlsca tlscert

interface CertificateSecret {
  ca_certificate: string
  certificate: string
  private_key: string
}

export async function run(): Promise<void> {
  try {
    const certWritePath = core.getInput('path')
    const secretName = core.getInput('secret')

    const caPath = `${certWritePath}/ca.pem`
    const certPath = `${certWritePath}/cert.pem`
    const keyPath = `${certWritePath}/key.pem`

    // Check if the directory exists, if not, create it
    try {
      await fs.access(certWritePath)
    } catch (error) {
      try {
        core.info(`Creating directory ${certWritePath}`)
        await fs.mkdir(certWritePath, { recursive: true })
      } catch (_) {
        core.setFailed(`Failed creating directory ${certWritePath}`)
        return
      }
    }

    // Get the secret from AWS Secrets Manager
    core.info(`Getting secret ${secretName}`)
    const client = new SecretsManagerClient()
    const response = await client.send(
      new GetSecretValueCommand({ SecretId: secretName })
    )
    const certSecret = JSON.parse(
      response.SecretString ?? ''
    ) as CertificateSecret

    // Write the certificate files
    core.info(`Writing certificate files to ${certWritePath}`)
    await fs.writeFile(
      caPath,
      certSecret.ca_certificate.replaceAll('\\n', '\n')
    )
    await fs.writeFile(certPath, certSecret.certificate.replaceAll('\\n', '\n'))
    await fs.writeFile(keyPath, certSecret.private_key.replaceAll('\\n', '\n'))

    // Write the earthly config
    core.info(`Writing earthly config to ${os.homedir()}/.earthly/config.yml`)
    const config = {
      global: {
        tlskey: keyPath,
        tlsca: caPath,
        tlscert: certPath
      }
    }

    const yamlConfig = yaml.dump(config)
    await fs.writeFile(`${os.homedir()}/.earthly/config.yml`, yamlConfig)
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}
