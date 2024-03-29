import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'
import * as github from '@actions/github'

const repoOwner = 'input-output-hk'
const repoName = 'catalyst-ci'

export async function run(
  platform: NodeJS.Process['platform'] = process.platform
): Promise<void> {
  if (platform !== 'linux') {
    core.setFailed('This action only supports Linux runners')
    return
  }

  try {
    const assetName = core.getInput('asset')
    const token = core.getInput('token')
    const version = core.getInput('version')

    const assetFullName = `${assetName}-linux-amd64.tar.gz`

    if (version !== 'latest' && !isSemVer(version)) {
      core.setFailed('Invalid version')
      return
    }

    const octokit = github.getOctokit(token)
    const { data: releases } = await octokit.rest.repos.listReleases({
      owner: repoOwner,
      repo: repoName
    })

    let targetRelease
    if (version === 'latest') {
      targetRelease = releases[0]
    } else {
      targetRelease = releases.find(r => r.tag_name === `v${version}`)
    }

    if (!targetRelease) {
      core.setFailed(`Version ${version} not found`)
      return
    }

    const asset = targetRelease.assets.find(a => a.name === assetFullName)
    if (!asset) {
      core.setFailed(`Asset for version v${version} not found`)
      return
    }

    const finalURL = asset.browser_download_url
    core.info(`Downloading version ${version} from ${finalURL}`)
    const downloadPath = await tc.downloadTool(finalURL)
    const extractPath = await tc.extractTar(downloadPath, '/usr/local/bin')
    core.info(`Installed cli to ${extractPath}`)
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
