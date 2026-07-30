# Builder and helper API

## Contents

- [Builder conventions](#builder-conventions)
- [Primitive builders](#primitive-builders)
- [Profile and path builders](#profile-and-path-builders)
- [Height-field surfaces](#height-field-surfaces)
- [Custom construction](#custom-construction)
- [Helpers](#helpers)
- [Seeded random values](#seeded-random-values)

## Builder conventions

Every mesh builder accepts common node options:

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

builders.torusKnot({
  radius: 1,
  tube: 0.2,
  tubularSegments: 96,
  radialSegments: 12,
  p: 2,
  q: 3
});

builders.plane({
  size: [width, height],
  segments: [1, 1]
});

builders.disc({
  radius: 1,
  segments: 32
});

builders.ring({
  innerRadius: 0.6,
  outerRadius: 1,
  thetaSegments: 32,
  phiSegments: 1
});

builders.polyhedron({
  vertices: [1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1],
  indices: [2, 1, 0, 0, 3, 2, 1, 3, 0, 2, 3, 1],
  radius: 1,
  detail: 0
});
```

`plane`, `disc`, and `ring` lie in the local XY plane.

`polyhedron` projects the supplied vertices onto `radius`; increase `detail` to subdivide its faces.

## Profile and path builders

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
  holes: [[[-0.3, -0.3], [-0.3, 0.3], [0.3, 0.3], [0.3, -0.3]]],
  depth: 0.4,
  bevelEnabled: true,
  bevelSize: 0.05,
  bevelThickness: 0.05,
  bevelSegments: 2
});
```

Sweep a 2D profile along a 3D curve or point path:

```js
builders.sweep({
  profile: [[-0.1, -0.2], [0.1, -0.2], [0.1, 0.2], [-0.1, 0.2]],
  holes: [],
  path: [[0, 0, 0], [0, 1, 1], [1, 2, 2]],
  steps: 48,
  closed: false,
  curveType: 'centripetal',
  tension: 0.5
});
```

Path sweeps disable beveling. Pass an existing `THREE.Curve` as `path` when a Catmull-Rom point path is not suitable.

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

`builders.tube()` also accepts an existing `THREE.Curve` as `path`.

## Height-field surfaces

Create an indexed, smooth Y-up surface from a rectangular height grid:

```js
builders.heightField({
  heights: [
    [0, 0.2, 0],
    [0.1, 0.8, 0.15],
    [0, 0.25, 0]
  ],
  size: [4, 3],
  heightScale: 1.5,
  heightOffset: 0,
  material: { color: '#668a4c', roughness: 0.9 }
});
```

Rows run along Z, columns run along X, and `size` is `[width, depth]`. The builder centers X and Z at the local origin, creates UVs over `[0, 1]`, and computes shared-vertex normals. The result is an open surface; add walls and a base separately when a watertight mesh is required.

For flat raster-style data, provide `[columns, rows]`:

```js
builders.heightField({
  heights: new Float32Array([0, 0.2, 0, 0.5, 0.1, 0]),
  gridSize: [3, 2],
  size: [2, 1]
});
```

`builders.terrain(options)` is an alias for the same builder.

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

Read world-space bounds:

```js
const bounds = helpers.getBounds(root);
const size = bounds?.size;
const center = bounds?.center;
```

Move an object so the bottom of its world-space bounds rests on Y=0:

```js
helpers.placeOnGround(root);
```

Center an object at the world origin:

```js
helpers.centerAtOrigin(root, { axes: ['x', 'z'] });
```

Align source and target bounds:

```js
helpers.align(panel, body, {
  axes: ['x'],
  sourceAnchor: 'min',
  targetAnchor: 'max',
  offset: [0.05, 0, 0]
});
```

Anchors are `min`, `center`, or `max`. Pass one string for every selected axis or an object such as `{ x: 'center', y: 'min' }`. The target may be an `Object3D` or a world-space `[x, y, z]` point.

Uniformly fit an object inside target dimensions:

```js
helpers.fitToSize(root, [2, 1, 2], {
  axes: ['x', 'y', 'z'],
  mode: 'contain'
});
```

Use `mode: 'cover'` to fill instead. Set `uniform: false` only for axis-aligned objects that may be distorted.

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

`helpers.mirror()` retains a negative scale. Prefer a baked mirror for OBJ/STL or final static geometry:

```js
const right = helpers.mirrorBaked(left, {
  axis: 'x',
  offset: 0,
  name: 'right-side'
});
```

Bake all hierarchy transforms into cloned mesh geometry and reset node transforms:

```js
const baked = helpers.bakeTransforms(root);
```

The source remains unchanged by default. Pass `{ clone: false }` only when intentional in-place replacement is safe. Baking is intended for static meshes, not skinned or transform-animated hierarchies.

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
