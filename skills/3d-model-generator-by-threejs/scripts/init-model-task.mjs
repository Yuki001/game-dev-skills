import { constants } from 'node:fs';
import { copyFile, mkdir } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

function parseArgs(argv) {
  const options = {};

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--out') options.out = argv[++index];
  }

  return options;
}

export async function initModelTask(outDirectory) {
  if (!outDirectory) {
    throw new Error('Usage: node init-model-task.mjs --out <task-dir>');
  }

  const outputDirectory = resolve(outDirectory);
  const templatePath = fileURLToPath(
    new URL('../assets/model-build.template.mjs', import.meta.url)
  );
  const outputPath = resolve(outputDirectory, 'model-build.mjs');

  await mkdir(outputDirectory, { recursive: true });
  await copyFile(templatePath, outputPath, constants.COPYFILE_EXCL);

  return {
    outputDirectory,
    outputPath
  };
}

const isMain =
  process.argv[1] &&
  basename(fileURLToPath(import.meta.url)) === basename(resolve(process.argv[1]));

if (isMain) {
  try {
    const options = parseArgs(process.argv.slice(2));
    const result = await initModelTask(options.out);
    process.stdout.write(`Created ${result.outputPath}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
