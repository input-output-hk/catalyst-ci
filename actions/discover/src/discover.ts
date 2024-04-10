import * as core from '@actions/core'
import { getExecOutput } from '@actions/exec'
import { quote } from 'shell-quote'

export async function run(): Promise<void> {
  try {
    const paths = quote([core.getInput('paths')])
    const targets = core.getInput('targets')

    const flags = ['-j']
    if (targets.trim() !== '') {
      flags.push(...targets.split(' ').map(t => `-t ${t}`))
    }
    const command = ['ci', 'scan', ...flags, paths].filter(Boolean).join(' ')

    core.info(`Running command: ${command}`)
    const { stdout } = await getExecOutput(command)

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const parsedData = JSON.parse(stdout)

    const pathsArray = []

    for (const key in parsedData) {
      if (Object.prototype.hasOwnProperty.call(parsedData, key)) {
        pathsArray.push(key)
      }
    }

    // JSON of path mapping to its filtered list of targets that need to be run
    core.setOutput('json', stdout)
    // List of path that should be run
    core.setOutput('paths', pathsArray)
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}
