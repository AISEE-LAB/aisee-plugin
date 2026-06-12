#!/usr/bin/env node
/**
 * Installs optional OpenSpec schemas from aisee-schema-pack/assets/schema-pack into
 * the current project's openspec/schemas/ directory.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, spawnSync } = require('child_process');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function projectRoot() {
  try {
    return execSync('git rev-parse --show-toplevel', {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore']
    }).trim();
  } catch {
    return process.cwd();
  }
}

function findSchemaPackDir() {
  const candidates = [
    process.env.AISEE_SCHEMA_PACK_DIR,
    path.join(__dirname, '..', 'assets', 'schema-pack'),
    path.join(process.cwd(), 'skills', 'aisee-schema-pack', 'assets', 'schema-pack'),
    path.join(process.cwd(), 'aisee-schema-pack', 'assets', 'schema-pack'),
    path.join(process.cwd(), 'aisee-opsx-schema', 'assets', 'schema-pack'),
    path.join(os.homedir(), '.agents', 'skills', 'aisee-schema-pack', 'assets', 'schema-pack'),
    path.join(os.homedir(), '.agents', 'skills', 'aisee-opsx-schema', 'assets', 'schema-pack'),
    path.join(os.homedir(), '.codex', 'skills', 'aisee-schema-pack', 'assets', 'schema-pack'),
    path.join(os.homedir(), '.codex', 'skills', 'aisee-opsx-schema', 'assets', 'schema-pack')
  ].filter(Boolean);

  for (const dir of candidates) {
    if (fs.existsSync(dir) && listSchemas(dir).length > 0) return dir;
  }

  throw new Error('找不到 schema-pack。请设置 AISEE_SCHEMA_PACK_DIR 指向 schema 包目录，或从包含 skills/aisee-schema-pack/ 的仓库根目录运行。');
}

function listSchemas(packDir) {
  try {
    return fs.readdirSync(packDir)
      .filter(name => {
        const schemaPath = path.join(packDir, name, 'schema.yaml');
        return fs.existsSync(schemaPath);
      })
      .sort();
  } catch {
    return [];
  }
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const selected = [];
  let force = false;
  let forceBaseline = false;
  let initBaseline = false;
  let list = false;
  let validate = true;

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--all') {
      selected.length = 0;
      selected.push('*');
    } else if (arg === '--schema') {
      if (!args[i + 1]) throw new Error('--schema 需要 schema 名称');
      selected.push(args[i + 1]);
      i += 1;
    } else if (arg === '--force') {
      force = true;
    } else if (arg === '--init-baseline') {
      initBaseline = true;
    } else if (arg === '--force-baseline') {
      forceBaseline = true;
      initBaseline = true;
    } else if (arg === '--list') {
      list = true;
    } else if (arg === '--no-validate') {
      validate = false;
    } else {
      throw new Error(`未知参数：${arg}`);
    }
  }

  return { selected, force, forceBaseline, initBaseline, list, validate };
}

function assertOpenSpecProject(root) {
  const required = [
    path.join(root, 'openspec', 'config.yaml'),
    path.join(root, 'openspec', 'changes')
  ];
  const missing = required.filter(item => !fs.existsSync(item));
  if (missing.length) {
    throw new Error(`当前项目尚未 openspec init，缺少：${missing.map(p => path.relative(root, p)).join(', ')}`);
  }
}

function copySchema(sourceDir, targetDir, force) {
  if (fs.existsSync(targetDir)) {
    if (!force) return 'skipped';
    removeDirRecursive(targetDir);
  }
  ensureDir(path.dirname(targetDir));
  copyDirRecursive(sourceDir, targetDir, {
    shouldSkipDir: (sourcePath, relativePath) => relativePath === 'examples'
  });
  return 'installed';
}

function removeDirRecursive(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      removeDirRecursive(fullPath);
    } else {
      fs.unlinkSync(fullPath);
    }
  }
  fs.rmdirSync(dir);
}

function copyDirRecursive(sourceDir, targetDir, options = {}) {
  const { shouldSkipDir = () => false } = options;
  ensureDir(targetDir);
  for (const entry of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    const sourcePath = path.join(sourceDir, entry.name);
    const targetPath = path.join(targetDir, entry.name);
    const relativePath = path.relative(sourceDir, sourcePath);
    if (entry.isDirectory()) {
      if (shouldSkipDir(sourcePath, relativePath)) continue;
      copyDirRecursive(sourcePath, targetPath, options);
    } else if (entry.isFile()) {
      fs.copyFileSync(sourcePath, targetPath);
    }
  }
}

function walkFiles(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkFiles(fullPath));
    } else if (entry.isFile()) {
      files.push(fullPath);
    }
  }
  return files;
}

function initBaselineTemplates(root, packDir, schemas, forceBaseline) {
  const results = [];
  for (const schema of schemas) {
    const baselineDir = path.join(packDir, schema, 'baseline-templates');
    if (!fs.existsSync(baselineDir)) continue;

    const files = walkFiles(baselineDir);
    for (const sourceFile of files) {
      const relative = path.relative(baselineDir, sourceFile);
      const targetFile = path.join(root, 'openspec', relative);
      let state = 'created';

      if (fs.existsSync(targetFile)) {
        if (!forceBaseline) {
          results.push({ state: 'skipped', schema, file: path.relative(root, targetFile) });
          continue;
        }
        state = 'overwritten';
      }

      ensureDir(path.dirname(targetFile));
      fs.copyFileSync(sourceFile, targetFile);
      results.push({ state, schema, file: path.relative(root, targetFile) });
    }
  }
  return results;
}

function validateSchemas(root, schemas) {
  const openspec = resolveOpenSpecCommand();
  const spawnOptions = process.platform === 'win32' ? { shell: true } : {};

  if (spawnSync(openspec, ['--version'], { stdio: 'ignore', ...spawnOptions }).status !== 0) {
    console.warn('  跳过校验：未找到 openspec CLI');
    return;
  }

  for (const schema of schemas) {
    const result = spawnSync(openspec, ['schema', 'validate', schema], {
      cwd: root,
      encoding: 'utf8',
      ...spawnOptions
    });
    if (result.status !== 0) {
      process.stderr.write(result.stdout || '');
      process.stderr.write(result.stderr || '');
      throw new Error(`schema 校验失败：${schema}`);
    }
    console.log(`  validated ${schema}`);
  }
}

function resolveOpenSpecCommand() {
  if (process.env.OPENSPEC_BIN) return process.env.OPENSPEC_BIN;

  if (process.platform !== 'win32') return 'openspec';

  const npmShim = process.env.APPDATA
    ? path.join(process.env.APPDATA, 'npm', 'openspec.cmd')
    : null;

  if (npmShim && fs.existsSync(npmShim)) return npmShim;
  return 'openspec.cmd';
}

function main() {
  const root = projectRoot();
  process.chdir(root);
  const packDir = findSchemaPackDir();
  const available = listSchemas(packDir);
  const { selected, force, forceBaseline, initBaseline, list, validate } = parseArgs(process.argv);

  if (list) {
    console.log(available.join('\n'));
    return;
  }

  assertOpenSpecProject(root);

  const wanted = selected.length === 0 || selected.includes('*') ? available : selected;
  const unknown = wanted.filter(name => !available.includes(name));
  if (unknown.length) throw new Error(`schema-pack 中不存在：${unknown.join(', ')}`);

  const installed = [];
  console.log(`安装 OpenSpec schemas 到 ${path.join(root, 'openspec', 'schemas')}`);
  for (const name of wanted) {
    const state = copySchema(
      path.join(packDir, name),
      path.join(root, 'openspec', 'schemas', name),
      force
    );
    console.log(`  ${state} ${name}`);
    if (state === 'installed') installed.push(name);
  }

  if (initBaseline) {
    const baselines = initBaselineTemplates(root, packDir, wanted, forceBaseline);
    if (baselines.length) {
      console.log('初始化 OpenSpec baseline templates');
      for (const item of baselines) {
        console.log(`  ${item.state} ${item.schema} -> ${item.file}`);
      }
    } else {
      console.log('未找到可初始化的 baseline templates');
    }
  }

  if (validate && installed.length) validateSchemas(root, installed);
}

try {
  main();
} catch (error) {
  console.error(`失败：${error.message}`);
  process.exit(1);
}
