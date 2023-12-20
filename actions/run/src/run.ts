import * as core from '@actions/core'
import { spawn } from 'child_process'
import * as path from 'path'
import * as fs from 'fs'
import { getExecOutput } from '@actions/exec'

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

  core.info(`>>>>>>> ${earthfile}`)
  core.info(`>>> ${target}`)
  const targets = target.split(' ')
  for (const tg of targets) {
    const { exitCode, stdout, stderr } = await getExecOutput(
      `ci find ${earthfile} -t ${target}`
    )
    core.info(`>>>> ${stdout}`)
  }

  // targets.map(t => {
  //   if (artifact) {
  //     targetsArgs.push('--artifact', `${earthfile}+${t}/`, `${artifactPath}`)
  //   } else {
  //     core.info(`Pushing target ${t}`)
  //     targetsArgs.push(`${earthfile}+${t}`)
  //   }
  // })

  if (targetFlags) {
    args.push(...targetFlags.split(' '))
  }

  core.info(`Running command: ${command} ${args.join(' ')}`)
  return new Promise<void>(resolve =>
    targetsArgs.map(async t => {
      core.info(`Running: ${t}`)
      const spawnArgs = args.concat(t)
      const output = await spawnCommand(command, spawnArgs)
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
      resolve()
    })
  )
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
