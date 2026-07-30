export async function buildModel(ctx) {
  const { builders, helpers } = ctx;

  const root = builders.group({ name: 'generated-model' });

  const body = builders.roundedBox({
    name: 'body',
    size: [2, 1.2, 1.4],
    radius: 0.12,
    segments: 3,
    position: [0, 0.8, 0],
    material: {
      color: '#3f77c5',
      roughness: 0.62,
      metalness: 0.08
    }
  });

  const cap = builders.cylinder({
    name: 'cap',
    radius: 0.46,
    height: 0.7,
    radialSegments: 32,
    position: [0, 1.75, 0],
    material: {
      color: '#d8e0e8',
      roughness: 0.32,
      metalness: 0.65
    }
  });

  const marker = builders.box({
    name: 'front-marker',
    size: [0.48, 0.32, 0.12],
    position: [0, 0.82, 0.74],
    material: {
      color: '#f0a33a',
      roughness: 0.48,
      metalness: 0.02
    }
  });

  root.add(body, cap, marker);
  helpers.placeOnGround(root);

  return {
    root,
    animations: [],
    metadata: {
      name: 'generated-model',
      units: 'meters',
      upAxis: 'Y'
    }
  };
}
