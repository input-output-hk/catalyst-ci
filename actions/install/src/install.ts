import * as core from '@actions/core'
import * as tc from '@actions/tool-cache'
import * as github from '@actions/github'
import { exec } from 'child_process'

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

  return new Promise((_, reject) => {
    exec(
      'go install -v github.com/input-output-hk/catalyst-ci/cli/cmd@468cdc9e4763b49f639c11186115cd0d782c8dbf && ls /usr/local/bin/',
      (err, stdout, stderr) => {
        if (err || stderr) {
          reject(new Error(err ? err.message : stderr))
        }
        console.log(`> ${stdout}`)
      }
    )
  })
  // try {
  //   const token = core.getInput('token')
  //   const version = core.getInput('version')
  //   const local = core.getInput('local')

  //   core.info(`> local ${local}`)
  //   if (local === 'true') {
  //     core.info('Local flag is used')
      // await exec('cd cli && go build -ldflags="-extldflags=-static" -o bin/ci cli/cmd/main.go', (error, stdout, stderr) => {
      //   if (error || stderr) {
      //     console.log(">", error ? error.message : stderr)
      //     console.log(new Error(error ? error.message : stderr))
      //   } else {
      //     console.log(stdout)
      //   }
      // })

      // return new Promise((_, reject) => {
      //   exec(
      //     'go install -v github.com/input-output-hk/catalyst-ci/cli/cmd@468cdc9e4763b49f639c11186115cd0d782c8dbf && ls /usr/local/bin/',
      //     (err, stdout, stderr) => {
      //       if (err || stderr) {
      //         reject(new Error(err ? err.message : stderr))
      //       }
      //       console.log(`> ${stdout}`)
      //     }
      //   )
      // })
    }

    // if (version !== 'latest' && !isSemVer(version)) {
    //   core.setFailed('Invalid version')
    //   return
    // }

    // const octokit = github.getOctokit(token)
    // const { data: releases } = await octokit.rest.repos.listReleases({
    //   owner: repoOwner,
    //   repo: repoName
    // })

    // let targetRelease
    // if (version === 'latest') {
    //   targetRelease = releases[0]
    // } else {
    //   targetRelease = releases.find(r => r.tag_name === `v${version}`)
    // }

    // if (!targetRelease) {
    //   core.setFailed(`Version ${version} not found`)
    //   return
    // }

    // const asset = targetRelease.assets.find(a => a.name === assetName)
    // if (!asset) {
    //   core.setFailed(`Asset for version v${version} not found`)
    //   return
    // }

    // const finalURL = asset.browser_download_url
    // core.info(`Downloading version ${version} from ${finalURL}`)
    // const downloadPath = await tc.downloadTool(finalURL)
    // const extractPath = await tc.extractTar(downloadPath, '/usr/local/bin')
    // core.info(`Installed cli to ${extractPath}`)
  // } catch (error) {
  //   if (error instanceof Error) {
  //     core.setFailed(error.message)
  //   } else {
  //     core.setFailed('Unknown error')
  //   }
  // }
// }

function isSemVer(version: string): boolean {
  return /^\d+\.\d+\.\d+$/.test(version)
}
