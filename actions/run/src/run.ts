import * as core from '@actions/core'
import { exec, spawn } from 'child_process'
import * as path from 'path'
import * as fs from 'fs'

export async function run(): Promise<void> {
  const artifact = core.getBooleanInput('artifact')
  const artifactPath = core.getInput('artifact_path')
  const earthfile = core.getInput('earthfile')
  const flags = core.getInput('flags')
  const platform = core.getInput('platform')
  const privileged = core.getBooleanInput('privileged')
  const runnerAddress = core.getInput('runner_address')
  const runnerPort = core.getInput('runner_port')
  const target = core.getInput('target')
  const targetFlags = core.getInput('target_flags')

  const command = 'earthly'
  const args: string[] = []

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

  core.info(`--artifact  target: ${target}`)
  core.info(`Earhtlfile permissiong ${earthfile}`)

  const targets = getTargetsFromEarthfile(target, earthfile)
  core.info(`>-------- ${targets}`)
  targets.map(t => {
    if (artifact) {
      args.push('--artifact', `${earthfile}+${t}/`, `${artifactPath}`)
    } else {
      core.info(`pushing target ${t}`)
      args.push(`${earthfile}+${t}`)
    }
  })

  if (targetFlags) {
    args.push(...targetFlags.split(' '))
  }

  core.info(`Running command: ${command} ${args.join(' ')}`)
  const output = await spawnCommand(command, args)

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

async function spawnCommand(command: string, args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args)

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

function getTargetsFromEarthfile(
  target: string,
  earthfile: string
): Array<string> {
  core.info('in getTargetsfrom earthfile')
  if (target.endsWith('-*')) {
    core.info('in -*')
    let targets: Array<string> = []
    fs.readFile(earthfile + '/Earthfile', 'utf8', (err, data) => {
      const mainTarget: string = target.slice(0, -2)
      core.info(`main target ${mainTarget}`)
      if (err) {
        console.error(`Error reading Earthfile: ${err.message}`)
        return
      }
      const targetRegex: RegExp = new RegExp(`^${mainTarget}(?:-[a-z0-9]+)?:$`)

      let match
      while ((match = targetRegex.exec(data)) !== null) {
        core.info(`Found ${data}`)
        core.info(`match ${match}`)
        targets.push(match[0]);
      }
    })
    return targets
  }
  return [target]
}
