function hashSeed(value) {
  const text = String(value);
  let hash = 2166136261;

  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return hash >>> 0;
}

export function createSeededRng(seed = 1) {
  const initialSeed = hashSeed(seed);
  let state = initialSeed || 0x6d2b79f5;

  function next() {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  }

  return Object.freeze({
    seed: initialSeed,
    next,
    float(min = 0, max = 1) {
      return min + next() * (max - min);
    },
    int(min, max) {
      const lower = Math.ceil(Math.min(min, max));
      const upper = Math.floor(Math.max(min, max));
      return Math.floor(next() * (upper - lower + 1)) + lower;
    },
    pick(values) {
      if (!Array.isArray(values) || values.length === 0) {
        throw new Error('rng.pick() requires a non-empty array.');
      }
      return values[Math.floor(next() * values.length)];
    },
    fork(label) {
      return createSeededRng(`${initialSeed}:${label}`);
    }
  });
}
