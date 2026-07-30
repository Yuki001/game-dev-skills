import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { installNodeFileReader } from '../runtime/node-file-reader.mjs';

export async function exportGltf(scene, options = {}) {
  installNodeFileReader();

  const exporter = new GLTFExporter();
  const result = await exporter.parseAsync(scene, {
    binary: options.binary ?? true,
    onlyVisible: options.onlyVisible ?? true,
    trs: options.trs ?? false,
    animations: options.animations ?? [],
    includeCustomExtensions: options.includeCustomExtensions ?? false,
    maxTextureSize: options.maxTextureSize ?? Infinity
  });

  if (options.binary ?? true) {
    return Buffer.from(result);
  }

  return Buffer.from(
    typeof result === 'string' ? result : JSON.stringify(result, null, 2),
    'utf8'
  );
}
