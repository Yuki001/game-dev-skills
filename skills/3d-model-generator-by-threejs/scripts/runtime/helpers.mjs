import * as THREE from 'three';

function toVector3(value) {
  if (value?.isVector3) return value.clone();
  return new THREE.Vector3(value[0], value[1], value[2]);
}

function worldBounds(object) {
  object.updateMatrixWorld(true);
  return new THREE.Box3().setFromObject(object, true);
}

export const helpers = Object.freeze({
  deg(value) {
    return THREE.MathUtils.degToRad(value);
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
