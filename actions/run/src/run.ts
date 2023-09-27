import * as core from '@actions/core'
import { spawn } from 'child_process'

export async function run(): Promise<void> {
  const artifact = core.getInput('artifact')
  const earthfile = core.getInput('earthfile')
  const flags = core.getInput('flags')
  const runnerAddress = core.getInput('runner_address')
  const runnerPort = core.getInput('runner_port')
  const target = core.getInput('target')

  const command = 'earthly'
  let args = artifact
    ? ['--artifact', `${earthfile}+${target}/${artifact}`, `${artifact}`]
    : [`${earthfile}+${target}`]
  args = flags ? args.concat(flags.split(' ')) : args
  args = runnerAddress
    ? args.concat(['--buildkit-host', `tcp://${runnerAddress}:${runnerPort}`])
    : args

  core.info(`Running command: ${command} ${args.join(' ')}`)
  const output = await spawnCommand(command, args)

  // TODO: The newest version of Earthly attaches annotations to the images
  let matches
  const imageRegex = /^Image .*? output as (.*?)$/gm
  const images = []
  while ((matches = imageRegex.exec(output)) !== null) {
    images.push(matches[1])
  }

  const artifactRegex = /^Artifact .*? output as (.*?)$/gm
  const artifacts = []
  while ((matches = artifactRegex.exec(output)) !== null) {
    artifacts.push(matches[1])
  }

  core.info(`Found images: ${images.join(' ')}`)
  core.info(`Found artifacts: ${artifacts.join(' ')}`)

  core.setOutput('images', images.join(' '))
  core.setOutput('artifacts', artifacts.join(' '))
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
