import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { buildAndExport } from '../build-and-export.mjs';
import { createBuildContext } from '../runtime/context.mjs';
import { inspectBuildSource } from '../runtime/load-model-build.mjs';
import { validateScene } from '../runtime/validate-scene.mjs';

function assertSafeTempPath(path) {
  const tempRoot = resolve(tmpdir());
  const target = resolve(path);
  assert.ok(
    target.startsWith(`${tempRoot}${sep}`),
    `Refusing to remove non-temporary test path: ${target}`
  );
}

function assertVectorClose(actual, expected, epsilon = 1e-6) {
  assert.equal(actual.length, expected.length);

  for (let index = 0; index < actual.length; index += 1) {
    assert.ok(
      Math.abs(actual[index] - expected[index]) <= epsilon,
      `${actual[index]} is not within ${epsilon} of ${expected[index]}`
    );
  }
}

function assertNormalsMatchWinding(mesh) {
  const position = mesh.geometry.getAttribute('position');
  const normal = mesh.geometry.getAttribute('normal');
  const index = mesh.geometry.index;
  const a = mesh.position.clone();
  const b = a.clone();
  const c = a.clone();
  const faceNormal = a.clone();
  const vertexNormal = a.clone();
  const secondNormal = a.clone();
  const thirdNormal = a.clone();
  const elementCount = index?.count ?? position.count;

  for (let offset = 0; offset < elementCount; offset += 3) {
    const first = index ? index.getX(offset) : offset;
    const second = index ? index.getX(offset + 1) : offset + 1;
    const third = index ? index.getX(offset + 2) : offset + 2;
    a.fromBufferAttribute(position, first);
    b.fromBufferAttribute(position, second);
    c.fromBufferAttribute(position, third);
    faceNormal.subVectors(b, a).cross(c.clone().sub(a)).normalize();
    vertexNormal
      .fromBufferAttribute(normal, first)
      .add(secondNormal.fromBufferAttribute(normal, second))
      .add(thirdNormal.fromBufferAttribute(normal, third))
      .normalize();
    assert.ok(faceNormal.dot(vertexNormal) > 0.99);
  }
}

test('source inspection rejects arbitrary capabilities', () => {
  assert.deepEqual(inspectBuildSource('export function buildModel() {}'), []);
  assert.ok(
    inspectBuildSource("import { readFile } from 'node:fs';").includes(
      'static imports'
    )
  );
  assert.ok(
    inspectBuildSource('Math.random()').includes(
      'non-deterministic random values'
    )
  );
});

test('builders and helpers create deterministic valid arrays', () => {
  const firstContext = createBuildContext({ seed: 'array-test' });
  const secondContext = createBuildContext({ seed: 'array-test' });

  assert.equal(firstContext.rng.next(), secondContext.rng.next());

  const source = firstContext.builders.box({
    name: 'spoke',
    size: [0.1, 0.1, 0.8],
    position: [0, 0.5, 0]
  });
  const radial = firstContext.helpers.repeatRadial(source, {
    count: 8,
    radius: 1.2,
    axis: 'y'
  });
  const root = firstContext.builders.group({
    name: 'array-root',
    children: [radial]
  });

  firstContext.helpers.placeOnGround(root);
  const scene = new firstContext.THREE.Scene();
  scene.add(root);
  const validation = validateScene(scene);

  assert.equal(radial.children.length, 8);
  assert.equal(validation.valid, true);
  assert.equal(validation.counts.meshes, 8);
  assert.equal(validation.counts.triangles, 96);
  assert.equal(validation.bounds.min[1], 0);
});

test('height-field builders create indexed Y-up surfaces', () => {
  const context = createBuildContext();
  const heightField = context.builders.heightField({
    name: 'height-field',
    heights: [
      [0, 1, 0],
      [1, 2, 1]
    ],
    size: [4, 2]
  });
  const position = heightField.geometry.getAttribute('position');
  const normal = heightField.geometry.getAttribute('normal');
  const uv = heightField.geometry.getAttribute('uv');

  assert.equal(position.count, 6);
  assert.equal(normal.count, 6);
  assert.equal(uv.count, 6);
  assert.equal(heightField.geometry.index.count, 12);
  assert.deepEqual(Array.from(position.array.slice(0, 3)), [-2, 0, -1]);
  assert.ok(normal.getY(0) > 0);

  const terrain = context.builders.terrain({
    heights: new Float32Array([0, 1, 2, 3]),
    gridSize: [2, 2],
    heightScale: 2,
    heightOffset: 1
  });
  const terrainPosition = terrain.geometry.getAttribute('position');
  assert.equal(terrainPosition.getY(0), 1);
  assert.equal(terrainPosition.getY(3), 7);

  const scene = new context.THREE.Scene();
  scene.add(heightField, terrain);
  const validation = validateScene(scene);

  assert.equal(validation.valid, true);
  assert.equal(validation.counts.meshes, 2);
  assert.equal(validation.counts.triangles, 6);
  assert.throws(
    () => context.builders.heightField({ heights: [[0, 1], [2]] }),
    /rectangular heights grid/
  );
});

test('extended primitive builders create valid geometry', () => {
  const context = createBuildContext();
  const disc = context.builders.disc({ radius: 1, segments: 12 });
  const ring = context.builders.ring({
    innerRadius: 0.5,
    outerRadius: 1,
    thetaSegments: 12
  });
  const knot = context.builders.torusKnot({
    radius: 0.75,
    tube: 0.15,
    tubularSegments: 32,
    radialSegments: 8
  });
  const polyhedron = context.builders.polyhedron({
    vertices: [
      1, 1, 1,
      -1, -1, 1,
      -1, 1, -1,
      1, -1, -1
    ],
    indices: [
      2, 1, 0,
      0, 3, 2,
      1, 3, 0,
      2, 3, 1
    ],
    radius: 1
  });
  const scene = new context.THREE.Scene();
  scene.add(disc, ring, knot, polyhedron);
  const validation = validateScene(scene);

  assert.equal(disc.geometry.type, 'CircleGeometry');
  assert.equal(ring.geometry.type, 'RingGeometry');
  assert.equal(knot.geometry.type, 'TorusKnotGeometry');
  assert.equal(polyhedron.geometry.type, 'PolyhedronGeometry');
  assert.equal(validation.valid, true);
  assert.equal(validation.counts.meshes, 4);
});

test('profile builders support holes and path sweeps', () => {
  const context = createBuildContext();
  const extruded = context.builders.extrude({
    points: [[-2, -2], [2, -2], [2, 2], [-2, 2]],
    holes: [[[-1, -1], [-1, 1], [1, 1], [1, -1]]],
    depth: 0.5,
    bevelEnabled: false
  });
  const swept = context.builders.sweep({
    profile: [[-0.25, -0.25], [0.25, -0.25], [0.25, 0.25], [-0.25, 0.25]],
    path: [[0, 0, 0], [0, 0.5, 1], [1, 0.5, 2]],
    steps: 12
  });
  const curve = new context.THREE.LineCurve3(
    new context.THREE.Vector3(0, 0, 0),
    new context.THREE.Vector3(0, 0, 2)
  );
  const curveSweep = context.builders.sweep({
    profile: [[-0.1, -0.1], [0.1, -0.1], [0.1, 0.1], [-0.1, 0.1]],
    path: curve,
    steps: 4
  });
  const extrudePosition = extruded.geometry.getAttribute('position');
  const scene = new context.THREE.Scene();
  scene.add(extruded, swept, curveSweep);
  const validation = validateScene(scene);
  const sweepBounds = new context.THREE.Box3().setFromObject(swept, true);

  assert.ok(
    Array.from(extrudePosition.array).some((value) => Math.abs(value - 1) < 1e-6),
    'Expected the extruded geometry to include hole-boundary vertices.'
  );
  assert.ok(sweepBounds.max.z - sweepBounds.min.z > 1.9);
  assert.equal(validation.valid, true);
  assert.equal(validation.counts.meshes, 3);
});

test('bounds, alignment, fitting, and baked mirroring preserve geometry', () => {
  const context = createBuildContext();
  const target = context.builders.box({
    size: [2, 2, 2],
    position: [0, 1, 0]
  });
  const subject = context.builders.box({
    size: [1, 1, 1],
    position: [3, 0, 0]
  });

  context.helpers.align(subject, target, {
    axes: ['y'],
    sourceAnchor: 'min',
    targetAnchor: 'max',
    offset: [0, 0.25, 0]
  });
  const alignedBounds = context.helpers.getBounds(subject);
  assert.ok(Math.abs(alignedBounds.min.y - 2.25) < 1e-6);
  assert.equal(subject.position.x, 3);

  const fitted = context.builders.box({ size: [2, 4, 1] });
  context.helpers.fitToSize(fitted, [1, 1, 1]);
  assertVectorClose(
    context.helpers.getBounds(fitted).size.toArray(),
    [0.5, 1, 0.25]
  );

  const source = context.builders.group({
    name: 'transform-source',
    position: [2, 1, -1],
    rotationDeg: [0, 30, 0],
    scale: [1.5, 0.75, 2],
    children: [
      context.builders.box({
        name: 'offset-box',
        size: [2, 1, 1],
        position: [1, 0.5, 0]
      })
    ]
  });
  const sourceBounds = context.helpers.getBounds(source);
  const baked = context.helpers.bakeTransforms(source);
  const bakedBounds = context.helpers.getBounds(baked);

  assert.notEqual(
    baked.children[0].geometry,
    source.children[0].geometry,
    'Baking must not mutate shared source geometry.'
  );
  assertVectorClose(bakedBounds.min.toArray(), sourceBounds.min.toArray());
  assertVectorClose(bakedBounds.max.toArray(), sourceBounds.max.toArray());
  baked.traverse((object) => {
    assertVectorClose(object.position.toArray(), [0, 0, 0]);
    assertVectorClose(object.scale.toArray(), [1, 1, 1]);
  });

  const mirrored = context.helpers.mirrorBaked(source, {
    axis: 'x',
    offset: 0
  });
  const mirroredExtrude = context.helpers.mirrorBaked(
    context.builders.extrude({
      points: [[-1, -1], [1, -1], [1, 1], [-1, 1]],
      depth: 0.5
    })
  );
  const mirroredBounds = context.helpers.getBounds(mirrored);
  const scene = new context.THREE.Scene();
  scene.add(mirrored, mirroredExtrude);
  const validation = validateScene(scene);

  assert.ok(Math.abs(mirroredBounds.min.x + sourceBounds.max.x) < 1e-6);
  assert.ok(Math.abs(mirroredBounds.max.x + sourceBounds.min.x) < 1e-6);
  assertNormalsMatchWinding(mirrored.children[0]);
  assertNormalsMatchWinding(mirroredExtrude);
  assert.equal(validation.valid, true);
  assert.equal(
    validation.warnings.some((warning) => warning.includes('negative scale')),
    false
  );
});

test('template builds and round-trips GLB, glTF, OBJ, and STL', async () => {
  const outputDirectory = await mkdtemp(
    join(tmpdir(), '3d-model-generator-by-threejs-')
  );
  const templatePath = fileURLToPath(
    new URL('../../assets/model-build.template.mjs', import.meta.url)
  );

  try {
    const manifest = await buildAndExport({
      build: templatePath,
      out: outputDirectory,
      formats: ['glb', 'gltf', 'obj', 'stl'],
      seed: 7,
      timeoutMs: 15000
    });

    assert.equal(manifest.files.length, 4);
    assert.ok(manifest.validation.counts.meshes >= 3);
    assert.ok(manifest.validation.counts.triangles > 0);

    for (const file of manifest.files) {
      const fileStat = await stat(file.path);
      assert.ok(fileStat.size > 80, `${file.format} output is unexpectedly small.`);
    }

    const glbBuffer = await readFile(join(outputDirectory, 'model.glb'));
    const glbArrayBuffer = glbBuffer.buffer.slice(
      glbBuffer.byteOffset,
      glbBuffer.byteOffset + glbBuffer.byteLength
    );
    const gltf = await new GLTFLoader().parseAsync(glbArrayBuffer, '');
    let glbMeshes = 0;
    gltf.scene.traverse((object) => {
      if (object.isMesh) glbMeshes += 1;
    });
    assert.ok(glbMeshes >= 3);

    const gltfJson = JSON.parse(
      await readFile(join(outputDirectory, 'model.gltf'), 'utf8')
    );
    assert.equal(gltfJson.asset.version, '2.0');
    assert.ok(gltfJson.meshes.length >= 3);

    const objText = await readFile(join(outputDirectory, 'model.obj'), 'utf8');
    const obj = new OBJLoader().parse(objText);
    let objMeshes = 0;
    obj.traverse((object) => {
      if (object.isMesh) objMeshes += 1;
    });
    assert.ok(objMeshes >= 1);

    const stlBuffer = await readFile(join(outputDirectory, 'model.stl'));
    const stlArrayBuffer = stlBuffer.buffer.slice(
      stlBuffer.byteOffset,
      stlBuffer.byteOffset + stlBuffer.byteLength
    );
    const stlGeometry = new STLLoader().parse(stlArrayBuffer);
    assert.ok(stlGeometry.getAttribute('position').count > 0);

    const validation = JSON.parse(
      await readFile(join(outputDirectory, 'validation.json'), 'utf8')
    );
    assert.equal(validation.valid, true);
  } finally {
    assertSafeTempPath(outputDirectory);
    await rm(outputDirectory, { recursive: true, force: true });
  }
});
