import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { deflateSync } from 'node:zlib';
import { dirname, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { installNodeFileReader } from './runtime/node-file-reader.mjs';

const VIEW_DIRECTIONS = {
  iso: [1.2, 0.85, 1.35],
  front: [0, 0, 1],
  back: [0, 0, -1],
  left: [-1, 0, 0],
  right: [1, 0, 0],
  top: [0, 1, 0]
};

const FONT = {
  A: ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
  B: ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
  C: ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
  E: ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
  F: ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
  G: ['01111', '10000', '10000', '10111', '10001', '10001', '01111'],
  H: ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
  I: ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
  K: ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
  L: ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
  N: ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
  O: ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
  P: ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
  R: ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
  S: ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
  T: ['11111', '00100', '00100', '00100', '00100', '00100', '00100']
};

function parseArgs(argv) {
  const options = {
    views: ['iso'],
    width: 1200,
    height: 720,
    background: '#091018'
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--model') options.model = argv[++index];
    else if (token === '--out') options.out = argv[++index];
    else if (token === '--views') {
      options.views = argv[++index]
        .split(',')
        .map((value) => value.trim().toLowerCase())
        .filter(Boolean);
    } else if (token === '--width') {
      options.width = Number.parseInt(argv[++index], 10);
    } else if (token === '--height') {
      options.height = Number.parseInt(argv[++index], 10);
    } else if (token === '--background') {
      options.background = argv[++index];
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  return options;
}

function arrayBufferFrom(buffer) {
  return buffer.buffer.slice(
    buffer.byteOffset,
    buffer.byteOffset + buffer.byteLength
  );
}

async function loadModel(path) {
  const extension = extname(path).toLowerCase();
  const contents = await readFile(path);

  if (extension === '.glb') {
    installNodeFileReader();
    const gltf = await new GLTFLoader().parseAsync(
      arrayBufferFrom(contents),
      ''
    );
    return gltf.scene;
  }

  if (extension === '.gltf') {
    installNodeFileReader();
    const gltf = await new GLTFLoader().parseAsync(
      contents.toString('utf8'),
      ''
    );
    return gltf.scene;
  }

  if (extension === '.obj') {
    return new OBJLoader().parse(contents.toString('utf8'));
  }

  if (extension === '.stl') {
    const geometry = new STLLoader().parse(arrayBufferFrom(contents));
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

  throw new Error(`Unsupported preview format: ${extension}`);
}

function isVisibleInHierarchy(object) {
  let current = object;
  while (current) {
    if (!current.visible) return false;
    current = current.parent;
  }
  return true;
}

function materialForOffset(mesh, offset) {
  const materials = Array.isArray(mesh.material)
    ? mesh.material
    : [mesh.material];

  if (materials.length === 1 || mesh.geometry.groups.length === 0) {
    return materials[0];
  }

  const group = mesh.geometry.groups.find(
    (item) => offset >= item.start && offset < item.start + item.count
  );
  return materials[group?.materialIndex ?? 0] ?? materials[0];
}

function materialColor(material, colorAttribute, vertexIndices) {
  const color = material?.color?.isColor
    ? material.color.clone()
    : new THREE.Color(0xb8c0cc);

  if (material?.vertexColors && colorAttribute) {
    const vertexColor = new THREE.Color();
    const sample = new THREE.Color();

    for (const index of vertexIndices) {
      sample.setRGB(
        colorAttribute.getX(index),
        colorAttribute.getY(index),
        colorAttribute.getZ(index)
      );
      vertexColor.add(sample);
    }

    vertexColor.multiplyScalar(1 / vertexIndices.length);
    color.multiply(vertexColor);
  }

  if (material?.emissive?.isColor) {
    color.add(
      material.emissive
        .clone()
        .multiplyScalar(material.emissiveIntensity ?? 1)
    );
  }

  color.r = Math.max(0, Math.min(1, color.r));
  color.g = Math.max(0, Math.min(1, color.g));
  color.b = Math.max(0, Math.min(1, color.b));
  color.convertLinearToSRGB();

  return {
    r: Math.round(color.r * 255),
    g: Math.round(color.g * 255),
    b: Math.round(color.b * 255),
    a: Math.round(
      Math.max(0.15, Math.min(1, material?.opacity ?? 1)) * 255
    )
  };
}

function collectTriangles(root) {
  const triangles = [];
  const a = new THREE.Vector3();
  const b = new THREE.Vector3();
  const c = new THREE.Vector3();
  const edgeA = new THREE.Vector3();
  const edgeB = new THREE.Vector3();

  root.updateMatrixWorld(true);
  root.traverse((object) => {
    if (
      !object.isMesh ||
      !object.geometry?.isBufferGeometry ||
      !isVisibleInHierarchy(object)
    ) {
      return;
    }

    const position = object.geometry.getAttribute('position');
    if (!position) return;

    const index = object.geometry.index;
    const colorAttribute = object.geometry.getAttribute('color');
    const elementCount = index?.count ?? position.count;

    for (let offset = 0; offset < elementCount; offset += 3) {
      const first = index ? index.getX(offset) : offset;
      const second = index ? index.getX(offset + 1) : offset + 1;
      const third = index ? index.getX(offset + 2) : offset + 2;
      a.fromBufferAttribute(position, first).applyMatrix4(object.matrixWorld);
      b.fromBufferAttribute(position, second).applyMatrix4(object.matrixWorld);
      c.fromBufferAttribute(position, third).applyMatrix4(object.matrixWorld);
      const normal = edgeA
        .subVectors(b, a)
        .cross(edgeB.subVectors(c, a))
        .normalize()
        .clone();

      if (normal.lengthSq() === 0) continue;

      const material = materialForOffset(object, offset);
      triangles.push({
        a: a.clone(),
        b: b.clone(),
        c: c.clone(),
        normal,
        color: materialColor(
          material,
          colorAttribute,
          [first, second, third]
        ),
        side: material?.side ?? THREE.FrontSide
      });
    }
  });

  return triangles;
}

function parseColor(value) {
  const match = /^#?([0-9a-f]{6})$/i.exec(value);
  if (!match) throw new Error(`Expected a six-digit hex color, received: ${value}`);
  const number = Number.parseInt(match[1], 16);
  return {
    r: (number >> 16) & 255,
    g: (number >> 8) & 255,
    b: number & 255,
    a: 255
  };
}

function setPixel(pixels, width, height, x, y, color) {
  if (x < 0 || y < 0 || x >= width || y >= height) return;
  const offset = (y * width + x) * 4;
  pixels[offset] = color.r;
  pixels[offset + 1] = color.g;
  pixels[offset + 2] = color.b;
  pixels[offset + 3] = color.a;
}

function fillRect(pixels, width, height, x, y, rectWidth, rectHeight, color) {
  const minX = Math.max(0, Math.floor(x));
  const maxX = Math.min(width, Math.ceil(x + rectWidth));
  const minY = Math.max(0, Math.floor(y));
  const maxY = Math.min(height, Math.ceil(y + rectHeight));

  for (let py = minY; py < maxY; py += 1) {
    for (let px = minX; px < maxX; px += 1) {
      setPixel(pixels, width, height, px, py, color);
    }
  }
}

function drawLabel(pixels, width, height, x, y, text) {
  const scale = 2;
  let cursor = x;
  const color = { r: 128, g: 231, b: 215, a: 255 };

  for (const character of text.toUpperCase()) {
    const glyph = FONT[character];
    if (!glyph) {
      cursor += 3 * scale;
      continue;
    }

    for (let row = 0; row < glyph.length; row += 1) {
      for (let column = 0; column < glyph[row].length; column += 1) {
        if (glyph[row][column] !== '1') continue;
        fillRect(
          pixels,
          width,
          height,
          cursor + column * scale,
          y + row * scale,
          scale,
          scale,
          color
        );
      }
    }

    cursor += 6 * scale;
  }
}

function projectSetup(bounds, panel, view) {
  const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  const outward = new THREE.Vector3(...VIEW_DIRECTIONS[view]).normalize();
  const forward = outward.clone().negate();
  const requestedUp =
    view === 'top'
      ? new THREE.Vector3(0, 0, -1)
      : new THREE.Vector3(0, 1, 0);
  const right = forward.clone().cross(requestedUp).normalize();
  const up = right.clone().cross(forward).normalize();
  const cameraPosition = center
    .clone()
    .addScaledVector(outward, Math.max(size.length() * 3, 3));
  const corners = [];

  for (const x of [bounds.min.x, bounds.max.x]) {
    for (const y of [bounds.min.y, bounds.max.y]) {
      for (const z of [bounds.min.z, bounds.max.z]) {
        corners.push(new THREE.Vector3(x, y, z));
      }
    }
  }

  const projected = corners.map((corner) => {
    const relative = corner.clone().sub(center);
    return {
      x: relative.dot(right),
      y: relative.dot(up)
    };
  });
  const minX = Math.min(...projected.map((point) => point.x));
  const maxX = Math.max(...projected.map((point) => point.x));
  const minY = Math.min(...projected.map((point) => point.y));
  const maxY = Math.max(...projected.map((point) => point.y));
  const spanX = Math.max(maxX - minX, 1e-6);
  const spanY = Math.max(maxY - minY, 1e-6);
  const scale = Math.min(
    panel.width * 0.78 / spanX,
    panel.height * 0.74 / spanY
  );
  const projectedCenterX = (minX + maxX) * 0.5;
  const projectedCenterY = (minY + maxY) * 0.5;

  return {
    outward,
    forward,
    right,
    up,
    center,
    cameraPosition,
    project(point) {
      const relative = point.clone().sub(center);
      return {
        x:
          panel.x +
          panel.width * 0.5 +
          (relative.dot(right) - projectedCenterX) * scale,
        y:
          panel.y +
          panel.height * 0.52 -
          (relative.dot(up) - projectedCenterY) * scale,
        depth: point.clone().sub(cameraPosition).dot(forward)
      };
    }
  };
}

function rasterizeTriangle(
  pixels,
  zBuffer,
  width,
  height,
  panel,
  vertices,
  color
) {
  const [a, b, c] = vertices;
  const area =
    (b.x - a.x) * (c.y - a.y) -
    (b.y - a.y) * (c.x - a.x);

  if (Math.abs(area) < 1e-8) return;

  const minX = Math.max(
    panel.x,
    Math.floor(Math.min(a.x, b.x, c.x))
  );
  const maxX = Math.min(
    panel.x + panel.width - 1,
    Math.ceil(Math.max(a.x, b.x, c.x))
  );
  const minY = Math.max(
    panel.y,
    Math.floor(Math.min(a.y, b.y, c.y))
  );
  const maxY = Math.min(
    panel.y + panel.height - 1,
    Math.ceil(Math.max(a.y, b.y, c.y))
  );

  for (let y = minY; y <= maxY; y += 1) {
    for (let x = minX; x <= maxX; x += 1) {
      const px = x + 0.5;
      const py = y + 0.5;
      const w0 =
        ((b.x - px) * (c.y - py) -
          (b.y - py) * (c.x - px)) /
        area;
      const w1 =
        ((c.x - px) * (a.y - py) -
          (c.y - py) * (a.x - px)) /
        area;
      const w2 = 1 - w0 - w1;

      if (w0 < -1e-6 || w1 < -1e-6 || w2 < -1e-6) continue;

      const depth = w0 * a.depth + w1 * b.depth + w2 * c.depth;
      const pixelIndex = y * width + x;
      if (depth >= zBuffer[pixelIndex]) continue;

      zBuffer[pixelIndex] = depth;
      const offset = pixelIndex * 4;
      const alpha = color.a / 255;
      pixels[offset] = Math.round(
        color.r * alpha + pixels[offset] * (1 - alpha)
      );
      pixels[offset + 1] = Math.round(
        color.g * alpha + pixels[offset + 1] * (1 - alpha)
      );
      pixels[offset + 2] = Math.round(
        color.b * alpha + pixels[offset + 2] * (1 - alpha)
      );
      pixels[offset + 3] = 255;
    }
  }
}

function renderView(pixels, zBuffer, width, height, panel, view, bounds, triangles) {
  const setup = projectSetup(bounds, panel, view);
  const lightDirection = new THREE.Vector3(0.45, 0.85, 0.55).normalize();

  for (const triangle of triangles) {
    const centroid = triangle.a
      .clone()
      .add(triangle.b)
      .add(triangle.c)
      .multiplyScalar(1 / 3);
    const toCamera = setup.cameraPosition.clone().sub(centroid);
    const facing = triangle.normal.dot(toCamera);

    if (triangle.side === THREE.FrontSide && facing <= 0) continue;
    if (triangle.side === THREE.BackSide && facing >= 0) continue;

    const normal =
      triangle.side === THREE.DoubleSide && facing < 0
        ? triangle.normal.clone().negate()
        : triangle.normal;
    const diffuse = Math.max(0, normal.dot(lightDirection));
    const rim = Math.pow(
      1 - Math.abs(normal.dot(setup.outward)),
      2
    );
    const shade = Math.min(1.25, 0.36 + diffuse * 0.72 + rim * 0.12);
    const shadedColor = {
      r: Math.min(255, Math.round(triangle.color.r * shade)),
      g: Math.min(255, Math.round(triangle.color.g * shade)),
      b: Math.min(255, Math.round(triangle.color.b * shade)),
      a: triangle.color.a
    };

    rasterizeTriangle(
      pixels,
      zBuffer,
      width,
      height,
      panel,
      [
        setup.project(triangle.a),
        setup.project(triangle.b),
        setup.project(triangle.c)
      ],
      shadedColor
    );
  }

  const border = { r: 35, g: 58, b: 68, a: 255 };
  fillRect(pixels, width, height, panel.x, panel.y, panel.width, 1, border);
  fillRect(
    pixels,
    width,
    height,
    panel.x,
    panel.y + panel.height - 1,
    panel.width,
    1,
    border
  );
  fillRect(pixels, width, height, panel.x, panel.y, 1, panel.height, border);
  fillRect(
    pixels,
    width,
    height,
    panel.x + panel.width - 1,
    panel.y,
    1,
    panel.height,
    border
  );
  drawLabel(pixels, width, height, panel.x + 18, panel.y + 18, view);
}

function crc32(buffer) {
  let crc = 0xffffffff;

  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }

  return (crc ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data = Buffer.alloc(0)) {
  const typeBuffer = Buffer.from(type, 'ascii');
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(Buffer.concat([typeBuffer, data])));
  return Buffer.concat([length, typeBuffer, data, checksum]);
}

function encodePng(width, height, pixels) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width, 0);
  header.writeUInt32BE(height, 4);
  header[8] = 8;
  header[9] = 6;
  const scanlines = Buffer.alloc((width * 4 + 1) * height);

  for (let y = 0; y < height; y += 1) {
    const targetOffset = y * (width * 4 + 1);
    scanlines[targetOffset] = 0;
    pixels.copy(
      scanlines,
      targetOffset + 1,
      y * width * 4,
      (y + 1) * width * 4
    );
  }

  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    pngChunk('IHDR', header),
    pngChunk('IDAT', deflateSync(scanlines, { level: 9 })),
    pngChunk('IEND')
  ]);
}

function validateOptions(options) {
  if (!options.model || !options.out) {
    throw new Error(
      'Usage: node render-preview.mjs --model <model.glb> --out <preview.png> [--views iso,front,top]'
    );
  }

  if (
    !Number.isInteger(options.width) ||
    !Number.isInteger(options.height) ||
    options.width < 64 ||
    options.height < 64 ||
    options.width > 4096 ||
    options.height > 4096
  ) {
    throw new Error('Preview width and height must be integers from 64 to 4096.');
  }

  if (
    !Array.isArray(options.views) ||
    options.views.length === 0 ||
    options.views.some((view) => !VIEW_DIRECTIONS[view])
  ) {
    throw new Error(
      `Preview views must use: ${Object.keys(VIEW_DIRECTIONS).join(', ')}.`
    );
  }

  if (extname(options.out).toLowerCase() !== '.png') {
    throw new Error('Preview output must use a .png extension.');
  }
}

export async function renderPreview(options) {
  const normalized = {
    views: ['iso'],
    width: 1200,
    height: 720,
    background: '#091018',
    ...options,
    model: options.model ? resolve(options.model) : undefined,
    out: options.out ? resolve(options.out) : undefined
  };
  validateOptions(normalized);

  const root = await loadModel(normalized.model);
  root.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(root, true);
  if (bounds.isEmpty()) {
    throw new Error('Cannot render a model with empty bounds.');
  }

  const triangles = collectTriangles(root);
  if (triangles.length === 0) {
    throw new Error('Cannot render a model with no visible mesh triangles.');
  }

  const background = parseColor(normalized.background);
  const pixels = Buffer.alloc(normalized.width * normalized.height * 4);
  for (let offset = 0; offset < pixels.length; offset += 4) {
    pixels[offset] = background.r;
    pixels[offset + 1] = background.g;
    pixels[offset + 2] = background.b;
    pixels[offset + 3] = background.a;
  }
  const zBuffer = new Float64Array(normalized.width * normalized.height);
  zBuffer.fill(Number.POSITIVE_INFINITY);

  const columns = Math.min(3, normalized.views.length);
  const rows = Math.ceil(normalized.views.length / columns);
  const panelWidth = Math.floor(normalized.width / columns);
  const panelHeight = Math.floor(normalized.height / rows);

  normalized.views.forEach((view, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    const panel = {
      x: column * panelWidth,
      y: row * panelHeight,
      width:
        column === columns - 1
          ? normalized.width - column * panelWidth
          : panelWidth,
      height:
        row === rows - 1
          ? normalized.height - row * panelHeight
          : panelHeight
    };
    renderView(
      pixels,
      zBuffer,
      normalized.width,
      normalized.height,
      panel,
      view,
      bounds,
      triangles
    );
  });

  const png = encodePng(normalized.width, normalized.height, pixels);
  await mkdir(dirname(normalized.out), { recursive: true });
  await writeFile(normalized.out, png);

  return {
    model: normalized.model,
    out: normalized.out,
    views: normalized.views,
    width: normalized.width,
    height: normalized.height,
    triangles: triangles.length,
    bytes: png.length
  };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = await renderPreview(parseArgs(process.argv.slice(2)));
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error.stack ?? error.message}\n`);
    process.exitCode = 1;
  }
}
