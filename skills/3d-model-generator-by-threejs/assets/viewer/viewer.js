import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { createBuildContext } from '/runtime/context.mjs';

const canvas = document.querySelector('#viewport');
const assetName = document.querySelector('#asset-name');
const sourceLabel = document.querySelector('#source-label');
const statusElement = document.querySelector('#status');
const meshCount = document.querySelector('#mesh-count');
const triangleCount = document.querySelector('#triangle-count');
const sizeValue = document.querySelector('#size-value');
const wireframeToggle = document.querySelector('#wireframe-toggle');
const gridToggle = document.querySelector('#grid-toggle');

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true
});
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x091018);

const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 10000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

const hemisphere = new THREE.HemisphereLight(0xe8f4ff, 0x1d2c35, 2.4);
scene.add(hemisphere);

const keyLight = new THREE.DirectionalLight(0xffffff, 3.1);
keyLight.position.set(5, 8, 6);
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(0x62d6c7, 2.2);
rimLight.position.set(-6, 4, -5);
scene.add(rimLight);

const grid = new THREE.GridHelper(20, 20, 0x38505c, 0x1d2c35);
grid.material.transparent = true;
grid.material.opacity = 0.62;
scene.add(grid);

let modelRoot = null;
let modelBounds = new THREE.Box3();
let wireframe = false;

function setStatus(message, error = false) {
  statusElement.textContent = message;
  statusElement.classList.toggle('error', error);
}

async function loadExportedModel(url) {
  const extension = url.split('?')[0].split('.').pop().toLowerCase();

  if (extension === 'glb' || extension === 'gltf') {
    const gltf = await new GLTFLoader().loadAsync(url);
    return gltf.scene;
  }

  if (extension === 'obj') {
    return await new OBJLoader().loadAsync(url);
  }

  if (extension === 'stl') {
    const geometry = await new STLLoader().loadAsync(url);
    geometry.computeVertexNormals();
    return new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        color: 0xb7c5d1,
        roughness: 0.62,
        metalness: 0.05
      })
    );
  }

  throw new Error(`Unsupported review format: ${extension}`);
}

async function loadSourceModel(url) {
  const module = await import(`${url}?review=${Date.now()}`);

  if (typeof module.buildModel !== 'function') {
    throw new Error('Source module does not export buildModel(ctx).');
  }

  const result = await module.buildModel(createBuildContext({ seed: 1 }));
  const root = result?.isObject3D ? result : result?.root;

  if (!root?.isObject3D) {
    throw new Error('buildModel(ctx) returned no Object3D root.');
  }

  return root;
}

function analyzeModel(root) {
  let meshes = 0;
  let triangles = 0;

  root.updateMatrixWorld(true);
  root.traverse((object) => {
    if (!object.isMesh || !object.geometry) return;
    meshes += 1;
    const position = object.geometry.getAttribute('position');
    const elementCount = object.geometry.index?.count ?? position?.count ?? 0;
    triangles += Math.floor(elementCount / 3);
  });

  modelBounds = new THREE.Box3().setFromObject(root, true);
  const size = modelBounds.getSize(new THREE.Vector3());

  return {
    meshes,
    triangles,
    bounds: {
      min: modelBounds.min.toArray(),
      max: modelBounds.max.toArray(),
      size: size.toArray(),
      center: modelBounds.getCenter(new THREE.Vector3()).toArray()
    }
  };
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
}

function updateStats(stats) {
  meshCount.textContent = formatNumber(stats.meshes);
  triangleCount.textContent = formatNumber(stats.triangles);
  sizeValue.textContent = stats.bounds.size
    .map((value) => formatNumber(value))
    .join(' × ');
}

function fitView(view = 'iso') {
  if (!modelRoot || modelBounds.isEmpty()) return;

  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const radius = Math.max(size.length() * 0.72, 0.5);
  const directions = {
    iso: new THREE.Vector3(1.2, 0.85, 1.35),
    front: new THREE.Vector3(0, 0, 1),
    back: new THREE.Vector3(0, 0, -1),
    left: new THREE.Vector3(-1, 0, 0),
    right: new THREE.Vector3(1, 0, 0),
    top: new THREE.Vector3(0, 1, 0)
  };
  const direction = directions[view] ?? directions.iso;

  camera.up.set(0, 1, 0);
  if (view === 'top') camera.up.set(0, 0, -1);

  camera.position.copy(center).add(direction.normalize().multiplyScalar(radius * 2.3));
  camera.near = Math.max(radius / 1000, 0.001);
  camera.far = Math.max(radius * 30, 100);
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

function toggleWireframe() {
  wireframe = !wireframe;
  wireframeToggle.classList.toggle('active', wireframe);

  modelRoot?.traverse((object) => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material)
      ? object.material
      : [object.material];

    for (const material of materials) {
      if ('wireframe' in material) {
        material.wireframe = wireframe;
        material.needsUpdate = true;
      }
    }
  });
}

function resizeRenderer() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  if (canvas.width !== width || canvas.height !== height) {
    renderer.setSize(width, height, false);
    camera.aspect = width / Math.max(height, 1);
    camera.updateProjectionMatrix();
  }
}

async function main() {
  const query = new URLSearchParams(window.location.search);
  const modelUrl = query.get('model');
  const sourceUrl = query.get('source');

  if (!modelUrl && !sourceUrl) {
    throw new Error('Pass ?model=/artifact/model.glb or ?source=/artifact/model-build.mjs.');
  }

  if (modelUrl) {
    modelRoot = await loadExportedModel(modelUrl);
    sourceLabel.textContent = `Round-trip artifact · ${modelUrl}`;
    assetName.textContent = modelUrl.split('/').pop();
  } else {
    modelRoot = await loadSourceModel(sourceUrl);
    sourceLabel.textContent = `Source build · ${sourceUrl}`;
    assetName.textContent = sourceUrl.split('/').pop();
  }

  scene.add(modelRoot);
  const stats = analyzeModel(modelRoot);
  updateStats(stats);
  fitView('iso');
  setStatus('Ready · drag to orbit · wheel to zoom');

  window.__MODEL_REVIEW__ = {
    source: modelUrl ?? sourceUrl,
    mode: modelUrl ? 'round-trip' : 'source',
    stats
  };
  window.__MODEL_REVIEW_READY__ = true;
}

document.querySelectorAll('[data-view]').forEach((button) => {
  button.addEventListener('click', () => {
    document
      .querySelectorAll('[data-view]')
      .forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    fitView(button.dataset.view);
  });
});

wireframeToggle.addEventListener('click', toggleWireframe);
gridToggle.addEventListener('click', () => {
  grid.visible = !grid.visible;
  gridToggle.classList.toggle('active', grid.visible);
});

function render() {
  resizeRenderer();
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(render);
}

main().catch((error) => {
  assetName.textContent = 'Review failed';
  sourceLabel.textContent = error.message;
  setStatus(error.stack ?? error.message, true);
  window.__MODEL_REVIEW_ERROR__ = error.message;
});

render();
