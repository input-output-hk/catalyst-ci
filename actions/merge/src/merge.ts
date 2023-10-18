import * as core from '@actions/core'
import * as fs from 'fs'

type Hashes = { [key: string]: string }

export async function run(): Promise<void> {
  try {
    const hash = core.getInput('tag')
    const hashFile = core.getInput('hash_file')
    const images = core.getInput('images')

    const newHashes = buildHashes(images.split('\n'), hash)
    core.info(`Merging new hashes: ${JSON.stringify(newHashes, null, 2)}`)

    const hashFileContent = await fs.promises.readFile(hashFile, 'utf8')
    const hashFileHashes = JSON.parse(hashFileContent) as Hashes

    const mergedHashes = { ...hashFileHashes, ...newHashes }
    const sortedHashes = Object.keys(mergedHashes)
      .sort()
      .reduce((result, key) => {
        result[key] = mergedHashes[key]
        return result
      }, {} as Hashes)
    core.info(`Merged hashes: ${JSON.stringify(sortedHashes, null, 2)}`)

    await fs.promises.writeFile(
      hashFile,
      `${JSON.stringify(sortedHashes, null, 2)}\n`
    )
    core.info(`Wrote merged hashes to ${hashFile}`)
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message)
    } else {
      core.setFailed('Unknown error')
    }
  }
}

export function buildHashes(images: string[], hash: string): Hashes {
  return images.reduce((acc, image) => {
    acc[image] = hash
    return acc
  }, {} as Hashes)
}
