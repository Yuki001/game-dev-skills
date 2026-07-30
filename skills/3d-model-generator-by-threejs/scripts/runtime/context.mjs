import * as THREE from 'three';
import { createBuilders } from './builders.mjs';
import { helpers } from './helpers.mjs';
import { createSeededRng } from './random.mjs';

export function createBuildContext(options = {}) {
  const seed = options.seed ?? 1;

  return Object.freeze({
    apiVersion: 1,
    THREE,
    builders: createBuilders(),
    helpers,
    rng: createSeededRng(seed),
    logger: options.logger ?? console
  });
}
