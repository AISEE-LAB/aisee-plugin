#!/usr/bin/env node
/**
 * Installs aisee-init project hooks for Codex.
 *
 * The installer copies hook scripts into the target project under .aisee/hooks/
 * so runtime config never depends on where this skill is installed.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const REQUIRED_HOOKS = ['session-inject.js', 'spec-drift.js', 'prompt-scan.js'];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return {};
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
  console.log(`  wrote ${filePath}`);
}

function uniqueArray(items) {
  const seen = new Set();
  const out = [];
  for (const item of items) {
    const key = JSON.stringify(item);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
  }
  return out;
}

function mergeHookConfig(existing, incoming) {
  const result = { ...existing };
  result.hooks = { ...(existing.hooks || {}) };

  for (const [eventName, groups] of Object.entries(incoming.hooks || {})) {
    result.hooks[eventName] = uniqueArray([...(result.hooks[eventName] || []), ...groups]);
  }

  return result;
}

function detectTargets() {
  const args = process.argv.slice(2);
  if (args.includes('--codex')) return { codex: true };

  const codex = fs.existsSync('AGENTS.md') || fs.existsSync('.codex');

  if (!codex) {
    throw new Error('无法自动检测 Codex 目标。请先创建 AGENTS.md / .codex，或传入 --codex。');
  }

  return { codex };
}

function findSourceHooksDir() {
  const candidates = [
    process.env.AISEE_INIT_HOOKS_DIR,
    path.join(__dirname, 'hooks'),
    path.join(process.cwd(), 'aisee-init', 'scripts', 'hooks'),
    path.join(os.homedir(), '.codex', 'skills', 'aisee-init', 'scripts', 'hooks')
  ].filter(Boolean);

  for (const dir of candidates) {
    if (REQUIRED_HOOKS.every(file => fs.existsSync(path.join(dir, file)))) {
      return dir;
    }
  }

  throw new Error(`找不到 hook 源脚本目录。请设置 AISEE_INIT_HOOKS_DIR，且目录内包含：${REQUIRED_HOOKS.join(', ')}`);
}

function projectRoot() {
  try {
    return execSync('git rev-parse --show-toplevel', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return process.cwd();
  }
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function nodeCommand(scriptPath, env = {}) {
  const prefix = Object.entries(env)
    .map(([key, value]) => `${key}=${shellQuote(value)}`)
    .join(' ');
  return `${prefix ? `${prefix} ` : ''}node ${shellQuote(scriptPath)}`;
}

function installHookScripts(root, sourceDir) {
  const targetDir = path.join(root, '.aisee', 'hooks');
  ensureDir(targetDir);

  for (const file of REQUIRED_HOOKS) {
    fs.copyFileSync(path.join(sourceDir, file), path.join(targetDir, file));
  }

  console.log(`  installed hooks to ${path.relative(root, targetDir)}`);
  return targetDir;
}

function upsertCodexFeatureFlag(configPath) {
  ensureDir(path.dirname(configPath));
  if (!fs.existsSync(configPath)) {
    fs.writeFileSync(configPath, '[features]\nhooks = true\n');
    console.log(`  wrote ${configPath}`);
    return;
  }

  const content = fs.readFileSync(configPath, 'utf8');
  if (/^\s*hooks\s*=\s*true\s*$/m.test(content)) {
    console.log(`  kept ${configPath} ([features].hooks already enabled)`);
    return;
  }

  if (/^\s*\[features]\s*$/m.test(content)) {
    const updated = content.replace(/^(\s*\[features]\s*$)/m, '$1\nhooks = true');
    fs.writeFileSync(configPath, updated.endsWith('\n') ? updated : `${updated}\n`);
  } else {
    fs.appendFileSync(configPath, `${content.endsWith('\n') ? '' : '\n'}\n[features]\nhooks = true\n`);
  }

  console.log(`  updated ${configPath} ([features].hooks = true)`);
}

function setupCodex(root, hookDir) {
  const hooksPath = path.join(root, '.codex', 'hooks.json');
  const configPath = path.join(root, '.codex', 'config.toml');
  const hook = name => path.join(hookDir, name);

  upsertCodexFeatureFlag(configPath);

  const incoming = {
    hooks: {
      SessionStart: [
        {
          matcher: 'startup|resume|clear',
          hooks: [
            {
              type: 'command',
              command: nodeCommand(hook('session-inject.js'), { CODEX_HOOK: '1' }),
              statusMessage: 'Loading OpenSpec context',
              timeout: 10
            }
          ]
        }
      ],
      UserPromptSubmit: [
        {
          hooks: [
            {
              type: 'command',
              command: nodeCommand(hook('spec-drift.js'), { CODEX_HOOK: '1' }),
              statusMessage: 'Checking spec scope',
              timeout: 10
            },
            {
              type: 'command',
              command: nodeCommand(hook('prompt-scan.js'), { CODEX_HOOK: '1' }),
              statusMessage: 'Scanning prompt',
              timeout: 5
            }
          ]
        }
      ],
      PreToolUse: [
        {
          matcher: 'Bash|apply_patch|Edit|Write',
          hooks: [
            {
              type: 'command',
              command: nodeCommand(hook('prompt-scan.js'), { CODEX_HOOK: '1' }),
              statusMessage: 'Scanning tool input',
              timeout: 5
            }
          ]
        }
      ]
    }
  };

  const merged = mergeHookConfig(readJson(hooksPath), incoming);
  writeJson(hooksPath, merged);
}

function main() {
  const root = projectRoot();
  process.chdir(root);

  const targets = detectTargets();
  const sourceDir = findSourceHooksDir();
  const hookDir = installHookScripts(root, sourceDir);

  console.log(`\n目标项目：${root}`);
  console.log('目标代理：Codex\n');

  if (targets.codex) setupCodex(root, hookDir);

  console.log('\n完成。Codex 项目级 hooks 首次运行前可能需要在 /hooks 中信任。\n');
}

try {
  main();
} catch (error) {
  console.error(`\n失败：${error.message}\n`);
  process.exit(1);
}
