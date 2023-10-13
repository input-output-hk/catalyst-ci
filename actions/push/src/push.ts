import * as core from '@actions/core'
import * as exec from '@actions/exec'

export async function run(): Promise<void> {
  try {
    const image = core.getInput('image')
    const registries = core.getInput('registries').split('\n')
    const tags = core.getInput('tags').split('\n')

    const imageName = image.split(':')[0]

    for (const registry of registries) {
      for (const tag of tags) {
        const fullImage = `${registry}/${imageName}:${tag}`

        core.info(`Tagging ${image} as ${fullImage}`)
        await exec.exec('docker', ['tag', image, fullImage])

        core.info(`Pushing ${fullImage}`)
        await exec.exec('docker', ['push', fullImage])
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}
