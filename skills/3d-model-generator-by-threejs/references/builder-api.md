# Builder and helper API

## Contents

- [Builder conventions](#builder-conventions)
- [Primitive builders](#primitive-builders)
- [Custom construction](#custom-construction)
- [Helpers](#helpers)
- [Seeded random values](#seeded-random-values)

## Builder conventions

Every primitive builder accepts common node options:

```js
{
  name: 'part-name',
  material: { color: '#4488ff', roughness: 0.7, metalness: 0.1 },
  position: [0, 1, 0],
  rotation: [0, helpers.deg(30), 0],
  rotationDeg: [0, 30, 0],
  scale: [1, 1, 1],
  castShadow: true,
  receiveShadow: true,
  userData: { role: 'body' }
}
```

Use either `rotation` or `rotationDeg`, not both.

Create groups:

```js
const root = builders.group({
  name: 'asset-root',
  children: [partA, partB]
});
```

Create materials:

```js
const metal = builders.material({
  type: 'standard',
  color: '#59636f',
  metalness: 0.75,
  roughness: 0.28
});
```

Supported material types are `standard`, `physical`, `basic`, `lambert`, and `phong`. A color string or number is shorthand for a standard material.

## Primitive builders

```js
builders.box({
  size: [width, height, depth],
  segments: [1, 1, 1]
});

builders.roundedBox({
  size: [width, height, depth],
  radius: 0.08,
  segments: 3
});

builders.sphere({
  radius: 1,
  widthSegments: 32,
  heightSegments: 16
});

builders.cylinder({
  radius: 1,
  radiusTop: 1,
  radiusBottom: 1,
  height: 2,
  radialSegments: 32,
  heightSegments: 1,
  openEnded: false
});

builders.cone({
  radius: 1,
  height: 2,
  radialSegments: 32
});

builders.capsule({
  radius: 0.5,
  length: 1,
  capSegments: 8,
  radialSegments: 16
});

builders.torus({
  radius: 1,
  tube: 0.25,
  radialSegments: 12,
  tubularSegments: 48,
  arc: Math.PI * 2
});

builders.plane({
  size: [width, height],
  segments: [1, 1]
});
```

Create a surface of revolution from `[radius, y]` points:

```js
builders.lathe({
  points: [[0.2, 0], [0.7, 0.2], [0.5, 1.4], [0.1, 1.6]],
  segments: 32
});
```

Extrude a 2D polygon in the XY plane:

```js
builders.extrude({
  points: [[-1, -1], [1, -1], [1, 1], [-1, 1]],
  depth: 0.4,
  bevelEnabled: true,
  bevelSize: 0.05,
  bevelThickness: 0.05,
  bevelSegments: 2
});
```

Create a tube through 3D points:

```js
builders.tube({
  points: [[0, 0, 0], [0, 1, 0], [1, 2, 0]],
  tubularSegments: 48,
  radius: 0.1,
  radialSegments: 10,
  closed: false
});
```

## Custom construction

Wrap custom geometry:

```js
const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setIndex(indices);
geometry.computeVertexNormals();

const mesh = builders.mesh({
  geometry,
  material: { color: '#d26a3a' },
  name: 'custom-part'
});
```

## Helpers

Convert degrees:

```js
helpers.deg(45);
```

Move an object so the bottom of its world-space bounds rests on Y=0:

```js
helpers.placeOnGround(root);
```

Center an object at the world origin:

```js
helpers.centerAtOrigin(root, { axes: ['x', 'z'] });
```

Create linear copies:

```js
const row = helpers.repeatLinear(bolt, {
  count: 6,
  step: [0.25, 0, 0],
  name: 'bolt-row'
});
```

Create radial copies around an axis:

```js
const ring = helpers.repeatRadial(spoke, {
  count: 12,
  radius: 1.5,
  axis: 'y',
  startAngle: 0,
  angleStep: Math.PI * 2 / 12,
  rotateWithArray: true,
  name: 'spoke-ring'
});
```

Mirror a clone:

```js
const right = helpers.mirror(left, {
  axis: 'x',
  offset: 0
});
```

Orient an object's local Y axis between two points:

```js
helpers.orientBetween(beam, [0, 0, 0], [1, 2, 0], {
  stretchAxis: 'y'
});
```

Set shadow flags recursively:

```js
helpers.setShadowRecursive(root, true, true);
```

## Seeded random values

```js
const uniform = rng.next();             // [0, 1)
const height = rng.float(0.8, 1.2);
const count = rng.int(3, 8);            // inclusive
const color = rng.pick(['red', 'blue']);
const branch = rng.fork('left-side');   // stable derived stream
```
