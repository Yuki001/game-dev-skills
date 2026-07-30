import { STLExporter } from 'three/addons/exporters/STLExporter.js';

export function exportStl(scene, options = {}) {
  const binary = options.binary ?? true;
  const exporter = new STLExporter();
  const result = exporter.parse(scene, { binary });

  if (!binary) {
    return Buffer.from(result, 'utf8');
  }

  return Buffer.from(result.buffer, result.byteOffset, result.byteLength);
}
