import { OBJExporter } from 'three/addons/exporters/OBJExporter.js';

export function exportObj(scene) {
  const exporter = new OBJExporter();
  return Buffer.from(exporter.parse(scene), 'utf8');
}
