import { mkdir, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { normalizeBuildResult } from './runtime/build-result.mjs';
import { createBuildContext } from './runtime/context.mjs';
import { loadModelBuild } from './runtime/load-model-build.mjs';
import { validateScene } from './runtime/validate-scene.mjs';
import { exportGltf } from './exporters/export-gltf.mjs';
import { exportObj } from './exporters/export-obj.mjs';
import { exportStl } from './exporters/export-stl.mjs';

const SUPPORTED_FORMATS = new Set(['glb', 'gltf', 'obj', 'stl']);

function parseInteger(value, label) {
  const number = Number.parseInt(value, 10);
  if (!Number.isFinite(number) || number <= 0) {
    throw new Error(`${label} must be a positive integer.`);
  }
  return number;
}

function parseArgs(argv) {
  const options = {
    formats: ['glb'],
    seed: 1,
    timeoutMs: 15000
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === '--build') options.build = argv[++index];
    else if (token === '--out') options.out = argv[++index];
    else if (token === '--name') options.name = argv[++index];
    else if (token === '--formats') {
      options.formats = argv[++index].split(',').map((value) => value.trim());
    } else if (token === '--seed') {
      options.seed = parseInteger(argv[++index], '--seed');
    } else if (token === '--timeout-ms') {
      options.timeoutMs = parseInteger(argv[++index], '--timeout-ms');
    } else if (token === '--max-objects') {
      options.maxObjects = parseInteger(argv[++index], '--max-objects');
    } else if (token === '--max-vertices') {
      options.maxVertices = parseInteger(argv[++index], '--max-vertices');
    } else if (token === '--max-triangles') {
      options.maxTriangles = parseInteger(argv[++index], '--max-triangles');
    } else if (token === '--max-extent') {
      options.maxExtent = parseInteger(argv[++index], '--max-extent');
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  return options;
}

function sanitizeBasename(value) {
  const sanitized = String(value ?? 'model')
    .trim()
    .replace(/[^a-zA-Z0-9_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return sanitized || 'model';
}

async function withTimeout(promise, timeoutMs) {
  let timer;

  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(
          () => reject(new Error(`buildModel() exceeded ${timeoutMs} ms.`)),
          timeoutMs
        );
      })
    ]);
  } finally {
    clearTimeout(timer);
  }
}

function validateFormats(formats) {
  const unique = [...new Set(formats.map((format) => format.toLowerCase()))];

  for (const format of unique) {
    if (!SUPPORTED_FORMATS.has(format)) {
      throw new Error(`Unsupported format: ${format}`);
    }
  }

  if (unique.length === 0) {
    throw new Error('At least one export format is required.');
  }

  return unique;
}

export async function buildAndExport(options) {
  if (!options.build || !options.out) {
    throw new Error(
      'Usage: node build-and-export.mjs --build <model-build.mjs> --out <dir> [--formats glb,obj,stl]'
    );
  }

  const formats = validateFormats(options.formats ?? ['glb']);
  const outputDirectory = resolve(options.out);
  const seed = options.seed ?? 1;
  const timeoutMs = options.timeoutMs ?? 15000;
  const loaded = await loadModelBuild(options.build);
  const context = createBuildContext({ seed });
  const rawResult = await withTimeout(
    Promise.resolve(loaded.buildModel(context)),
    timeoutMs
  );
  const normalized = normalizeBuildResult(rawResult, { seed });
  const validation = validateScene(normalized.scene, {
    maxObjects: options.maxObjects,
    maxVertices: options.maxVertices,
    maxTriangles: options.maxTriangles,
    maxExtent: options.maxExtent
  });

  if (
    validation.counts.textures > 0 &&
    formats.some((format) => format === 'glb' || format === 'gltf')
  ) {
    validation.errors.push(
      'GLB/glTF export with bitmap textures requires a browser or image-capable Canvas runtime.'
    );
    validation.valid = false;
  }

  if (
    validation.counts.shaderMaterials > 0 &&
    formats.some((format) => format === 'glb' || format === 'gltf')
  ) {
    validation.errors.push(
      'GLB/glTF export cannot preserve ShaderMaterial or RawShaderMaterial.'
    );
    validation.valid = false;
  }

  await mkdir(outputDirectory, { recursive: true });
  await writeFile(
    resolve(outputDirectory, 'validation.json'),
    JSON.stringify(
      {
        ...validation,
        buildModule: loaded.absolutePath,
        metadata: normalized.metadata
      },
      null,
      2
    ),
    'utf8'
  );

  if (!validation.valid) {
    throw new Error(
      `Scene validation failed:\n${validation.errors.map((value) => `- ${value}`).join('\n')}`
    );
  }

  const outputName = sanitizeBasename(options.name ?? 'model');
  const files = [];

  for (const format of formats) {
    const outputPath = resolve(outputDirectory, `${outputName}.${format}`);
    let data;

    if (format === 'glb') {
      data = await exportGltf(normalized.scene, {
        binary: true,
        animations: normalized.animations
      });
    } else if (format === 'gltf') {
      data = await exportGltf(normalized.scene, {
        binary: false,
        animations: normalized.animations
      });
    } else if (format === 'obj') {
      data = exportObj(normalized.scene);
    } else {
      data = exportStl(normalized.scene, { binary: true });
    }

    await writeFile(outputPath, data);
    files.push({
      format,
      path: outputPath,
      bytes: data.byteLength
    });
  }

  const manifest = {
    apiVersion: 1,
    seed,
    buildModule: loaded.absolutePath,
    metadata: normalized.metadata,
    validation: {
      counts: validation.counts,
      bounds: validation.bounds,
      warnings: validation.warnings
    },
    files
  };

  await writeFile(
    resolve(outputDirectory, 'model.manifest.json'),
    JSON.stringify(manifest, null, 2),
    'utf8'
  );

  return manifest;
}

const isMain =
  process.argv[1] &&
  basename(fileURLToPath(import.meta.url)) === basename(resolve(process.argv[1]));

if (isMain) {
  try {
    const options = parseArgs(process.argv.slice(2));
    const manifest = await buildAndExport(options);
    process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error.stack ?? error.message}\n`);
    process.exitCode = 1;
  }
}
