import * as core from '@actions/core'
import { spawn } from 'child_process'
import * as path from 'path'

export async function run(): Promise<void> {
  const artifact = core.getBooleanInput('artifact')
  const artifactPath = core.getInput('artifact_path')
  const earthfile = core.getInput('earthfile')
  const flags = core.getInput('flags')
  const github_token = core.getInput('github_token')
  const platform = core.getInput('platform')
  const privileged = core.getBooleanInput('privileged')
  const runnerAddress = core.getInput('runner_address')
  const runnerPort = core.getInput('runner_port')
  const targetFlags = core.getInput('target_flags')
  const targets = core.getInput('targets')

  const command = 'earthly'
  const args: string[] = []
  const targetsArgs: string[] = []

  if (privileged) {
    args.push('-P')
  }

  if (runnerAddress) {
    args.push('--buildkit-host', `tcp://${runnerAddress}:${runnerPort}`)
  }

  if (platform) {
    args.push('--platform', platform)
  }

  if (flags) {
    args.push(...flags.split(' '))
  }

  core.info(`Filtered targets >> ${targets}`)

  targets.split(' ').map(tg => {
    // Get the filtered targets associated with the pattern target and earthfile.
    core.info(`Pushing target ${tg}`)
    targetsArgs.push(`${earthfile}+${tg}`)
  })

  // Running each target command in different process.
  for (const t of targetsArgs) {
    core.info(`Running target: ${t}`)
    const argsSpawn = [...args]
    // Artifact is set
    if (artifact) {
      core.info(
        `Running --artifact with target ${t}, output to ${artifactPath}`
      )
      argsSpawn.push('--artifact', `${t}/`, `${artifactPath}`)
    } else {
      argsSpawn.push(t)
    }

    if (targetFlags) {
      argsSpawn.push(...targetFlags.split(' '))
    }

    core.info(`Running command: ${command} ${argsSpawn.join(' ')}`)
    const output = await spawnCommand(command, argsSpawn, github_token)
    const imageOutput = parseImage(output)
    if (imageOutput) {
      core.info(`Found image: ${imageOutput}`)
      core.setOutput('image', imageOutput)
    }

    const artifactOutput = path.join(earthfile, parseArtifact(output))
    if (artifactOutput !== earthfile) {
      core.info(`Found artifact: ${artifactOutput}`)
      core.setOutput('artifact', artifactOutput)
    }
  }
}

function parseArtifact(output: string): string {
  const regex = /^Artifact .*? output as (.*?)$/gm
  const match = regex.exec(output)
  if (match) {
    return match[1]
  }

  return ''
}

function parseImage(output: string): string {
  const regex = /^Image .*? output as (.*?)$/gm
  const match = regex.exec(output)
  if (match) {
    return match[1]
  }

  return ''
}

async function spawnCommand(
  command: string,
  args: string[],
  token: string
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      env: {
        GITHUB_TOKEN: token
      }
    })

    let output = ''

    child.stdout.on('data', (data: string) => {
      process.stdout.write(data)
    })

    child.stderr.on('data', (data: string) => {
      process.stderr.write(data)
      output += data
    })

    child.on('close', code => {
      if (code !== 0) {
        reject(new Error(`child process exited with code: ${code}`))
      } else {
        resolve(output)
      }
    })
  })
}
