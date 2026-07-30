import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { materialFrom } from './materials.mjs';

function vec3(value, fallback) {
  const source = value ?? fallback;
  return new THREE.Vector3(source[0], source[1], source[2]);
}

function applyNodeOptions(object, options = {}) {
  if (options.name) object.name = options.name;

  if (options.position) {
    object.position.copy(vec3(options.position, [0, 0, 0]));
  }

  if (options.rotation && options.rotationDeg) {
    throw new Error('Specify rotation or rotationDeg, not both.');
  }

  if (options.rotation) {
    object.rotation.set(...options.rotation);
  }

  if (options.rotationDeg) {
    object.rotation.set(
      THREE.MathUtils.degToRad(options.rotationDeg[0]),
      THREE.MathUtils.degToRad(options.rotationDeg[1]),
      THREE.MathUtils.degToRad(options.rotationDeg[2])
    );
  }

  if (options.scale) {
    object.scale.copy(vec3(options.scale, [1, 1, 1]));
  }

  if (options.castShadow !== undefined) {
    object.castShadow = Boolean(options.castShadow);
  }

  if (options.receiveShadow !== undefined) {
    object.receiveShadow = Boolean(options.receiveShadow);
  }

  if (options.visible !== undefined) {
    object.visible = Boolean(options.visible);
  }

  if (options.userData) {
    Object.assign(object.userData, options.userData);
  }

  return object;
}

function createMesh(geometry, options = {}) {
  const material = materialFrom(options.material);
  return applyNodeOptions(new THREE.Mesh(geometry, material), options);
}

function shapeFromPoints(points) {
  if (!Array.isArray(points) || points.length < 3) {
    throw new Error('Extrude geometry requires at least three 2D points.');
  }

  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);

  for (let index = 1; index < points.length; index += 1) {
    shape.lineTo(points[index][0], points[index][1]);
  }

  shape.closePath();
  return shape;
}

export function createBuilders() {
  return Object.freeze({
    material: materialFrom,

    group(options = {}) {
      const normalized =
        typeof options === 'string' ? { name: options } : options;
      const group = applyNodeOptions(new THREE.Group(), normalized);

      for (const child of normalized.children ?? []) {
        group.add(child);
      }

      return group;
    },

    mesh(options) {
      if (!options?.geometry?.isBufferGeometry) {
        throw new Error('builders.mesh() requires a BufferGeometry.');
      }
      return createMesh(options.geometry, options);
    },

    box(options = {}) {
      const size = options.size ?? [1, 1, 1];
      const segments = options.segments ?? [1, 1, 1];
      const geometry = new THREE.BoxGeometry(
        size[0],
        size[1],
        size[2],
        segments[0],
        segments[1],
        segments[2]
      );
      return createMesh(geometry, options);
    },

    roundedBox(options = {}) {
      const size = options.size ?? [1, 1, 1];
      const geometry = new RoundedBoxGeometry(
        size[0],
        size[1],
        size[2],
        options.segments ?? 2,
        options.radius ?? Math.min(...size) * 0.08
      );
      return createMesh(geometry, options);
    },

    sphere(options = {}) {
      const geometry = new THREE.SphereGeometry(
        options.radius ?? 0.5,
        options.widthSegments ?? 24,
        options.heightSegments ?? 16,
        options.phiStart ?? 0,
        options.phiLength ?? Math.PI * 2,
        options.thetaStart ?? 0,
        options.thetaLength ?? Math.PI
      );
      return createMesh(geometry, options);
    },

    cylinder(options = {}) {
      const radius = options.radius ?? 0.5;
      const geometry = new THREE.CylinderGeometry(
        options.radiusTop ?? radius,
        options.radiusBottom ?? radius,
        options.height ?? 1,
        options.radialSegments ?? 24,
        options.heightSegments ?? 1,
        options.openEnded ?? false,
        options.thetaStart ?? 0,
        options.thetaLength ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    cone(options = {}) {
      const geometry = new THREE.ConeGeometry(
        options.radius ?? 0.5,
        options.height ?? 1,
        options.radialSegments ?? 24,
        options.heightSegments ?? 1,
        options.openEnded ?? false,
        options.thetaStart ?? 0,
        options.thetaLength ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    capsule(options = {}) {
      const geometry = new THREE.CapsuleGeometry(
        options.radius ?? 0.5,
        options.length ?? 1,
        options.capSegments ?? 8,
        options.radialSegments ?? 16
      );
      return createMesh(geometry, options);
    },

    torus(options = {}) {
      const geometry = new THREE.TorusGeometry(
        options.radius ?? 0.75,
        options.tube ?? 0.2,
        options.radialSegments ?? 12,
        options.tubularSegments ?? 36,
        options.arc ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    plane(options = {}) {
      const size = options.size ?? [1, 1];
      const segments = options.segments ?? [1, 1];
      const geometry = new THREE.PlaneGeometry(
        size[0],
        size[1],
        segments[0],
        segments[1]
      );
      return createMesh(geometry, options);
    },

    lathe(options = {}) {
      const points = (options.points ?? []).map(
        ([radius, y]) => new THREE.Vector2(radius, y)
      );

      if (points.length < 2) {
        throw new Error('builders.lathe() requires at least two [radius, y] points.');
      }

      const geometry = new THREE.LatheGeometry(
        points,
        options.segments ?? 24,
        options.phiStart ?? 0,
        options.phiLength ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    extrude(options = {}) {
      const shape = shapeFromPoints(options.points ?? []);
      const geometry = new THREE.ExtrudeGeometry(shape, {
        depth: options.depth ?? 0.25,
        steps: options.steps ?? 1,
        curveSegments: options.curveSegments ?? 12,
        bevelEnabled: options.bevelEnabled ?? false,
        bevelThickness: options.bevelThickness ?? 0.05,
        bevelSize: options.bevelSize ?? 0.05,
        bevelOffset: options.bevelOffset ?? 0,
        bevelSegments: options.bevelSegments ?? 2
      });
      return createMesh(geometry, options);
    },

    tube(options = {}) {
      const points = (options.points ?? []).map(
        ([x, y, z]) => new THREE.Vector3(x, y, z)
      );

      if (points.length < 2) {
        throw new Error('builders.tube() requires at least two 3D points.');
      }

      const curve = new THREE.CatmullRomCurve3(
        points,
        options.closed ?? false,
        options.curveType ?? 'centripetal',
        options.tension ?? 0.5
      );
      const geometry = new THREE.TubeGeometry(
        curve,
        options.tubularSegments ?? 48,
        options.radius ?? 0.1,
        options.radialSegments ?? 10,
        options.closed ?? false
      );
      return createMesh(geometry, options);
    }
  });
}
