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

function drawClosedPath(path, points, label) {
  if (!Array.isArray(points) || points.length < 3) {
    throw new Error(`${label} requires at least three 2D points.`);
  }

  path.moveTo(points[0][0], points[0][1]);

  for (let index = 1; index < points.length; index += 1) {
    path.lineTo(points[index][0], points[index][1]);
  }

  path.closePath();
  return path;
}

function pathFromPoints(points, label) {
  return drawClosedPath(new THREE.Path(), points, label);
}

function shapeFromPoints(points, holes = [], label = 'Extrude geometry') {
  const shape = drawClosedPath(new THREE.Shape(), points, label);

  for (let index = 0; index < holes.length; index += 1) {
    shape.holes.push(
      pathFromPoints(holes[index], `${label} hole ${index + 1}`)
    );
  }

  return shape;
}

function curve3From(value, options, label) {
  if (value instanceof THREE.Curve) return value;

  if (!Array.isArray(value) || value.length < 2) {
    throw new Error(`${label} requires a Curve or at least two 3D path points.`);
  }

  const points = value.map(([x, y, z]) => new THREE.Vector3(x, y, z));
  const closed = options.closed ?? false;

  if (points.length === 2 && !closed) {
    return new THREE.LineCurve3(points[0], points[1]);
  }

  if (points.length < 3) {
    throw new Error(`${label} requires at least three path points when closed.`);
  }

  return new THREE.CatmullRomCurve3(
    points,
    closed,
    options.curveType ?? 'centripetal',
    options.tension ?? 0.5
  );
}

function normalizeHeightGrid(options) {
  const heights = options.heights;

  if (!Array.isArray(heights) && !ArrayBuffer.isView(heights)) {
    throw new Error(
      'builders.heightField() requires heights as a 2D array or flat array-like value.'
    );
  }

  const isNested = Array.isArray(heights) && Array.isArray(heights[0]);
  let columns;
  let rows;
  let values;

  if (isNested) {
    rows = heights.length;
    columns = heights[0]?.length ?? 0;

    if (
      rows < 2 ||
      columns < 2 ||
      heights.some((row) => !Array.isArray(row) || row.length !== columns)
    ) {
      throw new Error(
        'builders.heightField() requires a rectangular heights grid of at least 2x2.'
      );
    }

    values = heights.flat();
  } else {
    const gridSize = options.gridSize;

    if (
      !Array.isArray(gridSize) ||
      gridSize.length !== 2 ||
      !Number.isInteger(gridSize[0]) ||
      !Number.isInteger(gridSize[1]) ||
      gridSize[0] < 2 ||
      gridSize[1] < 2
    ) {
      throw new Error(
        'Flat heights require gridSize: [columns, rows], with both values at least 2.'
      );
    }

    [columns, rows] = gridSize;
    values = heights;

    if (values.length !== columns * rows) {
      throw new Error(
        `Flat heights length ${values.length} does not match gridSize ${columns}x${rows}.`
      );
    }
  }

  for (const value of values) {
    if (!Number.isFinite(value)) {
      throw new Error('builders.heightField() height values must be finite numbers.');
    }
  }

  return { columns, rows, values };
}

function createHeightField(options = {}) {
  const { columns, rows, values } = normalizeHeightGrid(options);
  const size = options.size ?? [columns - 1, rows - 1];
  const heightScale = options.heightScale ?? 1;
  const heightOffset = options.heightOffset ?? 0;

  if (
    !Array.isArray(size) ||
    size.length !== 2 ||
    !Number.isFinite(size[0]) ||
    !Number.isFinite(size[1]) ||
    size[0] <= 0 ||
    size[1] <= 0
  ) {
    throw new Error('builders.heightField() size must be [width, depth] with positive values.');
  }

  if (!Number.isFinite(heightScale) || !Number.isFinite(heightOffset)) {
    throw new Error('builders.heightField() heightScale and heightOffset must be finite.');
  }

  const vertexCount = columns * rows;
  const positions = new Float32Array(vertexCount * 3);
  const uvs = new Float32Array(vertexCount * 2);
  const indexCount = (columns - 1) * (rows - 1) * 6;
  const indices =
    vertexCount > 65535
      ? new Uint32Array(indexCount)
      : new Uint16Array(indexCount);
  let vertexOffset = 0;
  let uvOffset = 0;

  for (let row = 0; row < rows; row += 1) {
    const v = row / (rows - 1);
    const z = (v - 0.5) * size[1];

    for (let column = 0; column < columns; column += 1) {
      const u = column / (columns - 1);
      positions[vertexOffset] = (u - 0.5) * size[0];
      positions[vertexOffset + 1] =
        values[row * columns + column] * heightScale + heightOffset;
      positions[vertexOffset + 2] = z;
      uvs[uvOffset] = u;
      uvs[uvOffset + 1] = v;
      vertexOffset += 3;
      uvOffset += 2;
    }
  }

  let indexOffset = 0;

  for (let row = 0; row < rows - 1; row += 1) {
    for (let column = 0; column < columns - 1; column += 1) {
      const topLeft = row * columns + column;
      const topRight = topLeft + 1;
      const bottomLeft = topLeft + columns;
      const bottomRight = bottomLeft + 1;

      indices[indexOffset] = topLeft;
      indices[indexOffset + 1] = bottomLeft;
      indices[indexOffset + 2] = topRight;
      indices[indexOffset + 3] = topRight;
      indices[indexOffset + 4] = bottomLeft;
      indices[indexOffset + 5] = bottomRight;
      indexOffset += 6;
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex(new THREE.BufferAttribute(indices, 1));
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return createMesh(geometry, options);
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

    torusKnot(options = {}) {
      const geometry = new THREE.TorusKnotGeometry(
        options.radius ?? 0.75,
        options.tube ?? 0.2,
        options.tubularSegments ?? 96,
        options.radialSegments ?? 12,
        options.p ?? 2,
        options.q ?? 3
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

    disc(options = {}) {
      const geometry = new THREE.CircleGeometry(
        options.radius ?? 0.5,
        options.segments ?? 32,
        options.thetaStart ?? 0,
        options.thetaLength ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    ring(options = {}) {
      const geometry = new THREE.RingGeometry(
        options.innerRadius ?? 0.25,
        options.outerRadius ?? 0.5,
        options.thetaSegments ?? 32,
        options.phiSegments ?? 1,
        options.thetaStart ?? 0,
        options.thetaLength ?? Math.PI * 2
      );
      return createMesh(geometry, options);
    },

    polyhedron(options = {}) {
      const vertices = options.vertices ?? [];
      const indices = options.indices ?? [];
      const verticesAreArrayLike =
        Array.isArray(vertices) || ArrayBuffer.isView(vertices);
      const indicesAreArrayLike =
        Array.isArray(indices) || ArrayBuffer.isView(indices);

      if (
        !verticesAreArrayLike ||
        vertices.length < 9 ||
        vertices.length % 3 !== 0 ||
        Array.from(vertices).some((value) => !Number.isFinite(value))
      ) {
        throw new Error(
          'builders.polyhedron() vertices must be a flat array of at least three 3D points.'
        );
      }

      if (
        !indicesAreArrayLike ||
        indices.length < 3 ||
        indices.length % 3 !== 0 ||
        Array.from(indices).some(
          (value) =>
            !Number.isInteger(value) ||
            value < 0 ||
            value >= vertices.length / 3
        )
      ) {
        throw new Error(
          'builders.polyhedron() indices must be a flat triangle-index array.'
        );
      }

      const geometry = new THREE.PolyhedronGeometry(
        vertices,
        indices,
        options.radius ?? 0.5,
        options.detail ?? 0
      );
      return createMesh(geometry, options);
    },

    heightField(options = {}) {
      return createHeightField(options);
    },

    terrain(options = {}) {
      return createHeightField(options);
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
      const shape = shapeFromPoints(
        options.points ?? [],
        options.holes ?? [],
        'builders.extrude()'
      );
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

    sweep(options = {}) {
      const shape = shapeFromPoints(
        options.profile ?? [],
        options.holes ?? [],
        'builders.sweep() profile'
      );
      const path = curve3From(
        options.path,
        options,
        'builders.sweep()'
      );
      const geometry = new THREE.ExtrudeGeometry(shape, {
        steps: options.steps ?? 48,
        curveSegments: options.curveSegments ?? 12,
        bevelEnabled: false,
        extrudePath: path
      });
      return createMesh(geometry, options);
    },

    tube(options = {}) {
      const curve = curve3From(
        options.path ?? options.points,
        options,
        'builders.tube()'
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
