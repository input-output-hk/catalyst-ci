import * as core from '@actions/core'
import { exec } from 'child_process'
import { quote } from 'shell-quote'

export async function run(): Promise<void> {
  try {
    const parse = core.getBooleanInput('parse_images')
    const paths = quote([core.getInput('paths')])
    const targets = core.getInput('targets')

    const flags = parse ? ['-ji'] : ['-j']
    if (targets.trim() !== '') {
      flags.push(...targets.split(' ').map(t => `-t ${t}`))
    }
    const command = ['ci', 'scan', ...flags, paths].filter(Boolean).join(' ')

    core.info(`Running command: ${command}`)
    const data = await execCommand(command)

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const parsedData = JSON.parse(data)

    const pathsArray = []

    for (const key in parsedData) {
      if (Object.prototype.hasOwnProperty.call(parsedData, key)) {
        pathsArray.push(key)
      }
    }

    core.setOutput('json', data)
    core.setOutput('paths', pathsArray)
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}

async function execCommand(command: string): Promise<string> {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error || stderr) {
        reject(new Error(error ? error.message : stderr))
      } else {
        resolve(stdout)
      }
    })
  })
}
