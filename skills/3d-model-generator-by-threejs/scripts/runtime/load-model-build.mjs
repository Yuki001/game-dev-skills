import { readFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const FORBIDDEN_PATTERNS = [
  [/^\s*import\s/m, 'static imports'],
  [/\bimport\s*\(/, 'dynamic imports'],
  [/\b(?:eval|Function)\s*\(/, 'dynamic code evaluation'],
  [/\b(?:process|require|child_process)\b/, 'Node process capabilities'],
  [/\b(?:fetch|XMLHttpRequest|WebSocket)\b/, 'network capabilities'],
  [/\bnode:/, 'Node built-in modules'],
  [/\b(?:setInterval|setTimeout)\s*\(/, 'background timers'],
  [/\bMath\.random\s*\(/, 'non-deterministic random values']
];

export function inspectBuildSource(source) {
  const violations = [];

  for (const [pattern, label] of FORBIDDEN_PATTERNS) {
    if (pattern.test(source)) violations.push(label);
  }

  return violations;
}

export async function loadModelBuild(buildPath) {
  const absolutePath = resolve(buildPath);
  const source = await readFile(absolutePath, 'utf8');
  const violations = inspectBuildSource(source);

  if (violations.length > 0) {
    throw new Error(
      `Generated build module uses forbidden capabilities: ${violations.join(', ')}.`
    );
  }

  const fileStat = await stat(absolutePath);
  const moduleUrl = pathToFileURL(absolutePath);
  moduleUrl.searchParams.set('mtime', String(fileStat.mtimeMs));
  const module = await import(moduleUrl.href);

  if (typeof module.buildModel !== 'function') {
    throw new Error('Generated module must export a buildModel(ctx) function.');
  }

  return {
    absolutePath,
    buildModel: module.buildModel
  };
}
