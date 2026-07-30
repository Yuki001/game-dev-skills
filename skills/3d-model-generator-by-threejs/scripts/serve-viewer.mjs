import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const CONTENT_TYPES = {
  '.css': 'text/css; charset=utf-8',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.obj': 'text/plain; charset=utf-8',
  '.stl': 'model/stl'
};

function parseArgs(argv) {
  const options = {
    port: 4173,
    host: '127.0.0.1'
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--artifact-dir') options.artifactDir = argv[++index];
    else if (token === '--model') options.model = argv[++index];
    else if (token === '--source') options.source = argv[++index];
    else if (token === '--port') options.port = Number.parseInt(argv[++index], 10);
    else if (token === '--host') options.host = argv[++index];
    else throw new Error(`Unknown argument: ${token}`);
  }

  return options;
}

function resolveWithin(root, relativePath) {
  const absoluteRoot = resolve(root);
  const target = resolve(absoluteRoot, relativePath);

  if (target !== absoluteRoot && !target.startsWith(`${absoluteRoot}${sep}`)) {
    return null;
  }

  return target;
}

async function sendFile(response, path) {
  try {
    const fileStat = await stat(path);
    if (!fileStat.isFile()) throw new Error('Not a file.');

    response.writeHead(200, {
      'Content-Type': CONTENT_TYPES[extname(path).toLowerCase()] ?? 'application/octet-stream',
      'Content-Length': fileStat.size,
      'Cache-Control': 'no-store'
    });
    createReadStream(path).pipe(response);
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Not found');
  }
}

export async function startViewerServer(options) {
  if (!options.artifactDir) {
    throw new Error(
      'Usage: node serve-viewer.mjs --artifact-dir <dir> [--model model.glb | --source model-build.mjs]'
    );
  }

  const scriptsDirectory = fileURLToPath(new URL('.', import.meta.url));
  const viewerDirectory = resolve(scriptsDirectory, '../assets/viewer');
  const runtimeDirectory = resolve(scriptsDirectory, 'runtime');
  const threeDirectory = resolve(scriptsDirectory, 'node_modules/three');
  const artifactDirectory = resolve(options.artifactDir);

  const server = createServer(async (request, response) => {
    const requestUrl = new URL(request.url, `http://${request.headers.host}`);
    const pathname = decodeURIComponent(requestUrl.pathname);
    let filePath;

    if (pathname === '/') {
      filePath = resolve(viewerDirectory, 'index.html');
    } else if (pathname.startsWith('/viewer/')) {
      filePath = resolveWithin(viewerDirectory, pathname.slice('/viewer/'.length));
    } else if (pathname.startsWith('/runtime/')) {
      filePath = resolveWithin(runtimeDirectory, pathname.slice('/runtime/'.length));
    } else if (pathname.startsWith('/three/')) {
      filePath = resolveWithin(threeDirectory, pathname.slice('/three/'.length));
    } else if (pathname.startsWith('/artifact/')) {
      filePath = resolveWithin(artifactDirectory, pathname.slice('/artifact/'.length));
    }

    if (!filePath) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('Not found');
      return;
    }

    await sendFile(response, filePath);
  });

  await new Promise((resolvePromise, reject) => {
    server.once('error', reject);
    server.listen(options.port ?? 4173, options.host ?? '127.0.0.1', resolvePromise);
  });

  const query = new URLSearchParams();
  if (options.model) query.set('model', `/artifact/${options.model}`);
  if (options.source) query.set('source', `/artifact/${options.source}`);
  const suffix = query.size > 0 ? `?${query}` : '';
  const url = `http://${options.host ?? '127.0.0.1'}:${options.port ?? 4173}/${suffix}`;

  return { server, url };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const options = parseArgs(process.argv.slice(2));
    const { url } = await startViewerServer(options);
    process.stdout.write(`Viewer: ${url}\n`);
  } catch (error) {
    process.stderr.write(`${error.stack ?? error.message}\n`);
    process.exitCode = 1;
  }
}
