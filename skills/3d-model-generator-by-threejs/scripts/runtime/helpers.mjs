import * as THREE from 'three';

const AXES = ['x', 'y', 'z'];
const ANCHORS = ['min', 'center', 'max'];

function toVector3(value) {
  if (value?.isVector3) return value.clone();

  if (
    !Array.isArray(value) ||
    value.length !== 3 ||
    value.some((component) => !Number.isFinite(component))
  ) {
    throw new Error('Expected a finite [x, y, z] value.');
  }

  return new THREE.Vector3(value[0], value[1], value[2]);
}

function worldBounds(object) {
  object.updateMatrixWorld(true);
  return new THREE.Box3().setFromObject(object, true);
}

function boundsDetails(object) {
  const box = worldBounds(object);
  if (box.isEmpty()) return null;

  return {
    box,
    min: box.min.clone(),
    max: box.max.clone(),
    size: box.getSize(new THREE.Vector3()),
    center: box.getCenter(new THREE.Vector3())
  };
}

function normalizeAxes(value) {
  const axes = value ?? AXES;

  if (
    !Array.isArray(axes) ||
    axes.length === 0 ||
    axes.some((axis) => !AXES.includes(axis))
  ) {
    throw new Error('Axes must be a non-empty array containing x, y, or z.');
  }

  return [...new Set(axes)];
}

function anchorForAxis(value, axis, fallback = 'center') {
  const anchor =
    typeof value === 'string' ? value : value?.[axis] ?? fallback;

  if (!ANCHORS.includes(anchor)) {
    throw new Error(`Unsupported ${axis}-axis anchor: ${anchor}`);
  }

  return anchor;
}

function boundCoordinate(bounds, axis, anchor) {
  if (anchor === 'min') return bounds.min[axis];
  if (anchor === 'max') return bounds.max[axis];
  return (bounds.min[axis] + bounds.max[axis]) * 0.5;
}

function translateInWorld(object, delta) {
  object.updateWorldMatrix(true, false);
  const worldPosition = object.getWorldPosition(new THREE.Vector3()).add(delta);

  if (object.parent) {
    object.parent.worldToLocal(worldPosition);
  }

  object.position.copy(worldPosition);
  object.updateMatrixWorld(true);
}

function swapAttributeVertices(attribute, first, second) {
  for (let component = 0; component < attribute.itemSize; component += 1) {
    const value = attribute.getComponent(first, component);
    attribute.setComponent(
      first,
      component,
      attribute.getComponent(second, component)
    );
    attribute.setComponent(second, component, value);
  }

  attribute.needsUpdate = true;
}

function reverseTriangleWinding(geometry) {
  if (geometry.index) {
    for (let index = 0; index < geometry.index.count; index += 3) {
      const second = geometry.index.getX(index + 1);
      geometry.index.setX(index + 1, geometry.index.getX(index + 2));
      geometry.index.setX(index + 2, second);
    }

    geometry.index.needsUpdate = true;
    return;
  }

  const attributes = [
    ...Object.values(geometry.attributes),
    ...Object.values(geometry.morphAttributes).flat()
  ];

  for (let index = 0; index < geometry.getAttribute('position').count; index += 3) {
    for (const attribute of attributes) {
      swapAttributeVertices(attribute, index + 1, index + 2);
    }
  }
}

function bakeObjectTransforms(source, options = {}) {
  if (!source?.isObject3D) {
    throw new Error('helpers.bakeTransforms() requires an Object3D.');
  }

  const result = options.clone === false ? source : source.clone(true);
  result.updateMatrixWorld(true);

  result.traverse((object) => {
    if (object.isSkinnedMesh) {
      throw new Error('helpers.bakeTransforms() does not support SkinnedMesh.');
    }

    if (!object.isMesh || !object.geometry?.isBufferGeometry) return;

    const transform = object.matrixWorld.clone();
    const geometry = object.geometry.clone();
    geometry.applyMatrix4(transform);

    if (transform.determinant() < 0) {
      reverseTriangleWinding(geometry);
    }

    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    object.geometry = geometry;
  });

  result.traverse((object) => {
    object.position.set(0, 0, 0);
    object.quaternion.identity();
    object.scale.set(1, 1, 1);
    object.updateMatrix();
  });
  result.updateMatrixWorld(true);
  return result;
}

export const helpers = Object.freeze({
  deg(value) {
    return THREE.MathUtils.degToRad(value);
  },

  getBounds(object) {
    return boundsDetails(object);
  },

  placeOnGround(object, groundY = 0) {
    const bounds = worldBounds(object);
    if (bounds.isEmpty()) return object;
    object.position.y += groundY - bounds.min.y;
    object.updateMatrixWorld(true);
    return object;
  },

  centerAtOrigin(object, options = {}) {
    const axes = new Set(options.axes ?? ['x', 'y', 'z']);
    const bounds = worldBounds(object);
    if (bounds.isEmpty()) return object;

    const center = bounds.getCenter(new THREE.Vector3());
    if (axes.has('x')) object.position.x -= center.x;
    if (axes.has('y')) object.position.y -= center.y;
    if (axes.has('z')) object.position.z -= center.z;
    object.updateMatrixWorld(true);
    return object;
  },

  align(object, target, options = {}) {
    const sourceBounds = worldBounds(object);
    if (sourceBounds.isEmpty()) return object;

    const axes = normalizeAxes(options.axes);
    const offset = toVector3(options.offset ?? [0, 0, 0]);
    const targetBounds = target?.isObject3D ? worldBounds(target) : null;
    const targetPoint = targetBounds ? null : toVector3(target);

    if (targetBounds?.isEmpty()) {
      throw new Error('helpers.align() target has empty bounds.');
    }

    const delta = new THREE.Vector3();

    for (const axis of axes) {
      const sourceAnchor = anchorForAxis(options.sourceAnchor, axis);
      const targetAnchor = anchorForAxis(
        options.targetAnchor,
        axis,
        sourceAnchor
      );
      const sourceCoordinate = boundCoordinate(
        sourceBounds,
        axis,
        sourceAnchor
      );
      const targetCoordinate = targetBounds
        ? boundCoordinate(targetBounds, axis, targetAnchor)
        : targetPoint[axis];
      delta[axis] = targetCoordinate - sourceCoordinate + offset[axis];
    }

    translateInWorld(object, delta);
    return object;
  },

  fitToSize(object, targetSize, options = {}) {
    const bounds = boundsDetails(object);
    if (!bounds) return object;

    if (
      typeof targetSize === 'number' &&
      (!Number.isFinite(targetSize) || targetSize <= 0)
    ) {
      throw new Error('helpers.fitToSize() target dimensions must be positive.');
    }

    if (
      options.mode !== undefined &&
      !['contain', 'cover'].includes(options.mode)
    ) {
      throw new Error(`Unsupported fit mode: ${options.mode}`);
    }

    const target =
      typeof targetSize === 'number'
        ? new THREE.Vector3(targetSize, targetSize, targetSize)
        : toVector3(targetSize);
    const axes = normalizeAxes(options.axes);
    const ratios = axes.map((axis) => {
      if (target[axis] <= 0) {
        throw new Error('helpers.fitToSize() target dimensions must be positive.');
      }

      if (bounds.size[axis] === 0) {
        throw new Error(
          `helpers.fitToSize() cannot fit a zero-size ${axis} dimension.`
        );
      }

      return { axis, value: target[axis] / bounds.size[axis] };
    });

    if (options.uniform ?? true) {
      const values = ratios.map(({ value }) => value);
      const factor =
        options.mode === 'cover' ? Math.max(...values) : Math.min(...values);
      object.scale.multiplyScalar(factor);
    } else {
      for (const { axis, value } of ratios) {
        object.scale[axis] *= value;
      }
    }

    object.updateMatrixWorld(true);
    return object;
  },

  repeatLinear(source, options = {}) {
    const count = Math.max(0, Math.floor(options.count ?? 1));
    const step = toVector3(options.step ?? [1, 0, 0]);
    const group = new THREE.Group();
    group.name = options.name ?? `${source.name || 'object'}-linear-array`;

    for (let index = 0; index < count; index += 1) {
      const clone = source.clone(true);
      clone.position.addScaledVector(step, index);
      clone.name = source.name ? `${source.name}-${index + 1}` : `item-${index + 1}`;
      group.add(clone);
    }

    return group;
  },

  repeatRadial(source, options = {}) {
    const count = Math.max(0, Math.floor(options.count ?? 1));
    const radius = options.radius ?? 1;
    const axis = options.axis ?? 'y';
    const startAngle = options.startAngle ?? 0;
    const angleStep = options.angleStep ?? (count > 0 ? Math.PI * 2 / count : 0);
    const rotateWithArray = options.rotateWithArray ?? true;
    const basePosition = source.position.clone();
    const group = new THREE.Group();
    group.name = options.name ?? `${source.name || 'object'}-radial-array`;

    for (let index = 0; index < count; index += 1) {
      const angle = startAngle + index * angleStep;
      const clone = source.clone(true);

      if (axis === 'x') {
        clone.position.set(
          basePosition.x,
          basePosition.y + Math.cos(angle) * radius,
          basePosition.z + Math.sin(angle) * radius
        );
        if (rotateWithArray) clone.rotation.x += angle;
      } else if (axis === 'z') {
        clone.position.set(
          basePosition.x + Math.cos(angle) * radius,
          basePosition.y + Math.sin(angle) * radius,
          basePosition.z
        );
        if (rotateWithArray) clone.rotation.z += angle;
      } else {
        clone.position.set(
          basePosition.x + Math.cos(angle) * radius,
          basePosition.y,
          basePosition.z + Math.sin(angle) * radius
        );
        if (rotateWithArray) clone.rotation.y -= angle;
      }

      clone.name = source.name ? `${source.name}-${index + 1}` : `item-${index + 1}`;
      group.add(clone);
    }

    return group;
  },

  mirror(source, options = {}) {
    const axis = options.axis ?? 'x';
    const offset = options.offset ?? 0;
    const clone = source.clone(true);
    clone.name = options.name ?? `${source.name || 'object'}-mirrored`;

    if (!['x', 'y', 'z'].includes(axis)) {
      throw new Error(`Unsupported mirror axis: ${axis}`);
    }

    clone.position[axis] = 2 * offset - clone.position[axis];
    clone.scale[axis] *= -1;
    return clone;
  },

  bakeTransforms(source, options = {}) {
    return bakeObjectTransforms(source, options);
  },

  mirrorBaked(source, options = {}) {
    const axis = options.axis ?? 'x';
    const offset = options.offset ?? 0;

    if (!source?.isObject3D) {
      throw new Error('helpers.mirrorBaked() requires an Object3D.');
    }

    if (!AXES.includes(axis)) {
      throw new Error(`Unsupported mirror axis: ${axis}`);
    }

    const clone = source.clone(true);
    clone.name = options.name ?? `${source.name || 'object'}-mirrored`;
    clone.position[axis] = 2 * offset - clone.position[axis];
    clone.scale[axis] *= -1;
    return bakeObjectTransforms(clone, { clone: false });
  },

  orientBetween(object, startValue, endValue, options = {}) {
    const start = toVector3(startValue);
    const end = toVector3(endValue);
    const direction = end.clone().sub(start);
    const distance = direction.length();

    if (distance === 0) {
      throw new Error('helpers.orientBetween() requires distinct points.');
    }

    const axisName = options.stretchAxis ?? 'y';
    const localAxis =
      axisName === 'x'
        ? new THREE.Vector3(1, 0, 0)
        : axisName === 'z'
          ? new THREE.Vector3(0, 0, 1)
          : new THREE.Vector3(0, 1, 0);

    object.position.copy(start).add(end).multiplyScalar(0.5);
    object.quaternion.setFromUnitVectors(localAxis, direction.normalize());

    if (options.stretch !== false) {
      object.scale[axisName] = distance;
    }

    object.updateMatrixWorld(true);
    return object;
  },

  setShadowRecursive(object, castShadow = true, receiveShadow = true) {
    object.traverse((child) => {
      if (!child.isMesh) return;
      child.castShadow = castShadow;
      child.receiveShadow = receiveShadow;
    });
    return object;
  }
});
