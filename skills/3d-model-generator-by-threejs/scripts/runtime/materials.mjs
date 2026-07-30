import * as THREE from 'three';

const MATERIAL_TYPES = {
  standard: THREE.MeshStandardMaterial,
  physical: THREE.MeshPhysicalMaterial,
  basic: THREE.MeshBasicMaterial,
  lambert: THREE.MeshLambertMaterial,
  phong: THREE.MeshPhongMaterial
};

function resolveSide(side) {
  if (side === 'double') return THREE.DoubleSide;
  if (side === 'back') return THREE.BackSide;
  return THREE.FrontSide;
}

function copyDefined(source, keys) {
  const result = {};

  for (const key of keys) {
    if (source[key] !== undefined) result[key] = source[key];
  }

  return result;
}

export function materialFrom(spec = {}) {
  if (spec?.isMaterial) return spec;

  const normalized =
    typeof spec === 'string' || typeof spec === 'number'
      ? { color: spec }
      : { ...spec };

  const type = normalized.type ?? 'standard';
  const MaterialClass = MATERIAL_TYPES[type];

  if (!MaterialClass) {
    throw new Error(`Unsupported material type: ${type}`);
  }

  const parameters = copyDefined(normalized, [
    'color',
    'emissive',
    'emissiveIntensity',
    'metalness',
    'roughness',
    'opacity',
    'transparent',
    'alphaTest',
    'depthWrite',
    'depthTest',
    'flatShading',
    'wireframe',
    'vertexColors',
    'clearcoat',
    'clearcoatRoughness',
    'ior',
    'reflectivity',
    'sheen',
    'sheenColor',
    'sheenRoughness',
    'specularColor',
    'specularIntensity',
    'transmission',
    'thickness',
    'attenuationColor',
    'attenuationDistance'
  ]);

  parameters.side = resolveSide(normalized.side);

  if (parameters.color === undefined) {
    parameters.color = 0xb8c0cc;
  }

  const material = new MaterialClass(parameters);
  material.name = normalized.name ?? '';

  if (normalized.userData) {
    Object.assign(material.userData, normalized.userData);
  }

  return material;
}
