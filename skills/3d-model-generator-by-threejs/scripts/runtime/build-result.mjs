import * as THREE from 'three';

const ALLOWED_UNITS = new Set(['meters', 'centimeters', 'millimeters']);
const ALLOWED_UP_AXES = new Set(['Y', 'Z']);

export function normalizeBuildResult(value, options = {}) {
  const result = value?.isObject3D ? { root: value } : value;

  if (!result || !result.root?.isObject3D) {
    throw new Error(
      'buildModel(ctx) must return a THREE.Object3D or { root: THREE.Object3D }.'
    );
  }

  if (
    result.animations !== undefined &&
    (!Array.isArray(result.animations) ||
      result.animations.some((clip) => !clip?.isAnimationClip))
  ) {
    throw new Error('Build result animations must be an array of AnimationClip values.');
  }

  const metadata = {
    name: result.metadata?.name ?? options.defaultName ?? 'model',
    units: result.metadata?.units ?? 'meters',
    upAxis: result.metadata?.upAxis ?? 'Y',
    seed: result.metadata?.seed ?? options.seed ?? 1,
    ...result.metadata
  };

  if (!ALLOWED_UNITS.has(metadata.units)) {
    throw new Error(`Unsupported metadata.units value: ${metadata.units}`);
  }

  if (!ALLOWED_UP_AXES.has(metadata.upAxis)) {
    throw new Error(`Unsupported metadata.upAxis value: ${metadata.upAxis}`);
  }

  const scene = result.root.isScene ? result.root : new THREE.Scene();

  if (!result.root.isScene) {
    scene.name = `${metadata.name}-scene`;
    scene.add(result.root);
  }

  scene.updateMatrixWorld(true);

  return {
    scene,
    root: result.root,
    animations: result.animations ?? [],
    metadata
  };
}
