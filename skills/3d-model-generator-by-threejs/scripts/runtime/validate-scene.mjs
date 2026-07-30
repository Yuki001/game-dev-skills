import * as THREE from 'three';

const TEXTURE_FIELDS = [
  'map',
  'alphaMap',
  'aoMap',
  'bumpMap',
  'clearcoatMap',
  'clearcoatNormalMap',
  'clearcoatRoughnessMap',
  'displacementMap',
  'emissiveMap',
  'envMap',
  'lightMap',
  'metalnessMap',
  'normalMap',
  'roughnessMap',
  'sheenColorMap',
  'sheenRoughnessMap',
  'specularColorMap',
  'specularIntensityMap',
  'thicknessMap',
  'transmissionMap'
];

function isFiniteVector(vector) {
  return vector.toArray().every(Number.isFinite);
}

function inspectAttribute(attribute, objectName, errors) {
  const values = attribute.array;

  for (let index = 0; index < values.length; index += 1) {
    if (!Number.isFinite(values[index])) {
      errors.push(`${objectName}: position attribute contains a non-finite value.`);
      return;
    }
  }
}

export function validateScene(scene, options = {}) {
  const limits = {
    maxObjects: options.maxObjects ?? 10000,
    maxVertices: options.maxVertices ?? 2000000,
    maxTriangles: options.maxTriangles ?? 2000000,
    maxExtent: options.maxExtent ?? 100000
  };

  const errors = [];
  const warnings = [];
  const materials = new Set();
  const textures = new Set();
  const counts = {
    objects: 0,
    meshes: 0,
    vertices: 0,
    triangles: 0,
    materials: 0,
    textures: 0,
    shaderMaterials: 0
  };

  scene.updateMatrixWorld(true);

  scene.traverse((object) => {
    counts.objects += 1;
    const objectName = object.name || object.type || 'unnamed-object';

    if (
      !isFiniteVector(object.position) ||
      !isFiniteVector(object.scale) ||
      !object.quaternion.toArray().every(Number.isFinite)
    ) {
      errors.push(`${objectName}: transform contains a non-finite value.`);
    }

    if (object.scale.x === 0 || object.scale.y === 0 || object.scale.z === 0) {
      errors.push(`${objectName}: transform contains a zero scale component.`);
    }

    if (object.scale.x < 0 || object.scale.y < 0 || object.scale.z < 0) {
      warnings.push(`${objectName}: negative scale may require baked normals.`);
    }

    if (!object.isMesh) return;
    counts.meshes += 1;

    const geometry = object.geometry;

    if (!geometry?.isBufferGeometry) {
      errors.push(`${objectName}: mesh has no BufferGeometry.`);
      return;
    }

    const position = geometry.getAttribute('position');

    if (!position || position.count === 0) {
      errors.push(`${objectName}: geometry has no position vertices.`);
      return;
    }

    inspectAttribute(position, objectName, errors);
    counts.vertices += position.count;

    const elementCount = geometry.index?.count ?? position.count;
    counts.triangles += Math.floor(elementCount / 3);

    if (elementCount % 3 !== 0) {
      warnings.push(`${objectName}: geometry element count is not divisible by three.`);
    }

    if (!geometry.getAttribute('normal')) {
      warnings.push(`${objectName}: geometry has no normal attribute.`);
    }

    const meshMaterials = Array.isArray(object.material)
      ? object.material
      : [object.material];

    for (const material of meshMaterials) {
      if (!material?.isMaterial) {
        errors.push(`${objectName}: mesh has an invalid material.`);
        continue;
      }

      materials.add(material);

      if (material.isShaderMaterial || material.isRawShaderMaterial) {
        counts.shaderMaterials += 1;
        warnings.push(
          `${objectName}: ShaderMaterial is not representable by the GLB exporter.`
        );
      }

      for (const field of TEXTURE_FIELDS) {
        if (material[field]?.isTexture) textures.add(material[field]);
      }
    }
  });

  counts.materials = materials.size;
  counts.textures = textures.size;

  if (counts.meshes === 0) {
    errors.push('Scene contains no meshes.');
  }

  if (counts.objects > limits.maxObjects) {
    errors.push(`Object count ${counts.objects} exceeds limit ${limits.maxObjects}.`);
  }

  if (counts.vertices > limits.maxVertices) {
    errors.push(`Vertex count ${counts.vertices} exceeds limit ${limits.maxVertices}.`);
  }

  if (counts.triangles > limits.maxTriangles) {
    errors.push(
      `Triangle count ${counts.triangles} exceeds limit ${limits.maxTriangles}.`
    );
  }

  const bounds = new THREE.Box3().setFromObject(scene, true);
  const boundsValue = bounds.isEmpty()
    ? null
    : {
        min: bounds.min.toArray(),
        max: bounds.max.toArray(),
        size: bounds.getSize(new THREE.Vector3()).toArray(),
        center: bounds.getCenter(new THREE.Vector3()).toArray()
      };

  if (!boundsValue) {
    errors.push('Scene has empty world-space bounds.');
  } else if (boundsValue.size.some((value) => value > limits.maxExtent)) {
    errors.push(
      `Scene extent exceeds configured maximum ${limits.maxExtent}.`
    );
  }

  if (counts.textures > 0) {
    warnings.push(
      'Scene contains bitmap textures; the default Node GLB/glTF path has no Canvas encoder.'
    );
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    counts,
    bounds: boundsValue,
    limits
  };
}
