import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'
import * as github from '@actions/github'
import { exec } from 'child_process'
import { stderr } from 'process'

const assetName = 'cli-linux-amd64.tar.gz'
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
    const token = core.getInput('token')
    const version = core.getInput('version')
    const local = core.getInput('local')

    // Local flag is tagged as true
    if (local === 'true') {
      // Create GOBIN
      // Install cli with commit hash
      // Change the name from cmd to ci
      // export GOBIN=/usr/local/bin/ &&
      // go install -v github.com/input-output-hk/catalyst-ci/cli/cmd@468cdc9e4763b49f639c11186115cd0d782c8dbf &&
      // mv $GOBIN/cmd $GOBIN/ci
      
      await exec(
        `cd cli`,
        (error, stdout, stderr) => {
          if (error || stderr) {
            console.log('> stderr cd', stderr)
            console.log('> errorr cd', error?.message)
          }
          console.log('> outputt cd', stdout)
        }
      )
      await exec(
        `go build -ldflags="-extldflags=-static" -o /usr/local/bin/ci cmd/main.go`,
        (error, stdout, stderr) => {
          if (error || stderr) {
            console.log('> stderr', stderr)
            console.log('> errorr', error?.message)
          }
          console.log('> outputt', stdout)
        }
      )
      return
    }

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

    const asset = targetRelease.assets.find(a => a.name === assetName)
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
