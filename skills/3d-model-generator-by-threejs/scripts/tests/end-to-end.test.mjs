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
