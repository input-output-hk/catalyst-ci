import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'

const baseURL =
  'https://github.com/meigma/omashu/releases/download/v%VER%/omashu-%VER%-linux_amd64.tar.gz'

export async function run(): Promise<void> {
  try {
    const version = core.getInput('version')

    if (!isSemVer(version)) {
      core.setFailed('Invalid version')
      return
    }

    const finalURL = baseURL.replace(/%VER%/g, version)
    core.info(`Downlaoading version ${version} from ${finalURL}`)
    if (process.platform === 'linux') {
      const downloadPath = await tc.downloadTool(finalURL)
      const extractPath = await tc.extractTar(downloadPath, '/usr/local/bin')

      core.info(`Installed omashu to ${extractPath}`)
    } else {
      core.setFailed('Unsupported platform')
    }
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}

function isSemVer(version: string): boolean {
  return /^\d+\.\d+\.\d+$/.test(version)
}

run()
