#!/usr/bin/env node
/**
 * Injects compact OpenSpec context at session start.
 * Never reads full project files; it emits pointers and small summaries only.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const MAX_ACTIVE_CHANGES = 8;
const MAX_KNOWLEDGE_ENTRIES = 10;

const KNOWLEDGE_SOURCES = [
  {
    canonical: 'aisee/docs/requirements',
    legacy: 'docs/requirements',
    label: 'SRS 与 FR 来源，仅用于追溯，不能替代 openspec/'
  },
  {
    canonical: 'aisee/docs/ui-content',
    legacy: 'docs/ui-content',
    label: '页面内容、元素、状态和交互来源'
  },
  {
    canonical: 'aisee/docs/architecture',
    legacy: 'docs/architecture',
    label: '技术架构事实、决策、项目约束、共享前置和风险来源'
  },
  {
    canonical: 'aisee/docs/change-plan',
    legacy: 'docs/change-plan',
    label: 'change 边界规划结果，后续仍需创建 OpenSpec artifacts'
  },
  {
    canonical: 'aisee/docs/reflect',
    legacy: 'docs/reflect',
    label: '会话反思与 memory 候选'
  }
];

const OPTIONAL_KNOWLEDGE_SOURCES = [
  ['docs/learnings', '团队复盘与模式库'],
  ['docs/solutions', '历史解决方案']
];

function readLines(filePath, maxLines = 60) {
  try {
    return fs.readFileSync(filePath, 'utf8').split('\n').slice(0, maxLines).join('\n');
  } catch {
    return null;
  }
}

function listDirs(dirPath) {
  try {
    return fs.readdirSync(dirPath)
      .filter(name => name !== 'archive')
      .filter(name => fs.statSync(path.join(dirPath, name)).isDirectory())
      .sort();
  } catch {
    return [];
  }
}

function countMarkdownFiles(dirPath) {
  try {
    return fs.readdirSync(dirPath)
      .filter(name => name.endsWith('.md') && !name.startsWith('.'))
      .length;
  } catch {
    return 0;
  }
}

function schemaName(changeDir, cwd) {
  const changeConfig = path.join(changeDir, '.openspec.yaml');
  const projectConfig = path.join(cwd, 'openspec', 'config.yaml');
  for (const filePath of [changeConfig, projectConfig]) {
    if (!fs.existsSync(filePath)) continue;
    const match = fs.readFileSync(filePath, 'utf8').match(/^\s*schema\s*:\s*([A-Za-z0-9_.:-]+)/m);
    if (match) return match[1];
  }
  return 'unknown';
}

function extractProjectMeta(content) {
  if (!content) return null;
  const keep = [];
  const patterns = [
    /^#\s+/,
    /^\s*[-*]\s*\*\*(名称|类型|目标|语言|框架|数据库|Name|Type|Goal|Language|Framework|Database)/i,
    /^\s*[-*]\s*(名称|类型|目标|语言|框架|数据库|Name|Type|Goal|Language|Framework|Database)\s*[:：]/i
  ];

  for (const line of content.split('\n')) {
    if (patterns.some(pattern => pattern.test(line))) keep.push(line.trim());
    if (keep.length >= 8) break;
  }

  return keep.length ? keep.join('\n') : null;
}

function summarizeChanges(cwd) {
  const changeNames = listDirs(path.join(cwd, 'openspec', 'changes'));
  if (!changeNames.length) return null;

  const shown = changeNames.slice(0, MAX_ACTIVE_CHANGES)
    .map(name => {
      const schema = schemaName(path.join(cwd, 'openspec', 'changes', name), cwd);
      return `- openspec/changes/${name}/（schema: ${schema}）`;
    });
  const hiddenCount = changeNames.length - shown.length;
  if (hiddenCount > 0) shown.push(`- ...另有 ${hiddenCount} 个 active changes，先明确目标 change 再读取。`);

  return [
    `活跃 OpenSpec changes（${changeNames.length}）：`,
    ...shown,
    '实现前先读取 .openspec.yaml / openspec/config.yaml 判断 schema，再按该 schema 的 artifact 依赖读取对应文件。'
  ].join('\n');
}

function summarizeMemory(cwd) {
  const canonicalRules = path.join(cwd, 'aisee', 'memory', 'rules.md');
  const canonicalIndex = path.join(cwd, 'aisee', 'memory', 'index.md');
  const legacyRules = path.join(cwd, '.memory', 'rules.md');
  const legacyIndex = path.join(cwd, '.memory', 'index.md');
  const hasCanonical = fs.existsSync(canonicalRules) || fs.existsSync(canonicalIndex);
  const hasLegacy = fs.existsSync(legacyRules) || fs.existsSync(legacyIndex);

  if (!hasCanonical && !hasLegacy) return null;

  const rulesPath = fs.existsSync(canonicalRules) ? canonicalRules : legacyRules;
  const indexPath = fs.existsSync(canonicalIndex) ? canonicalIndex : legacyIndex;
  const files = [
    fs.existsSync(rulesPath) && path.relative(cwd, rulesPath),
    fs.existsSync(indexPath) && path.relative(cwd, indexPath)
  ].filter(Boolean).join('、');
  const legacyNote = hasLegacy && hasCanonical
    ? '检测到 legacy `.memory/`，仅作迁移提示；优先使用 `aisee/memory/`。'
    : hasLegacy
      ? '当前仅发现 legacy `.memory/`，可 fallback 读取；新写入应使用 `aisee/memory/`。'
      : '';

  return `项目记忆入口：${files}。先读规则和索引，再只加载本任务相关条目。${legacyNote}`;
}

function summarizeKnowledge(cwd) {
  const entries = [];
  const legacyNotes = [];

  for (const source of KNOWLEDGE_SOURCES) {
    const canonicalCount = countMarkdownFiles(path.join(cwd, source.canonical));
    const legacyCount = countMarkdownFiles(path.join(cwd, source.legacy));
    if (canonicalCount > 0) {
      entries.push(`- ${source.canonical}/：${source.label}（${canonicalCount} 个条目）`);
      if (legacyCount > 0) legacyNotes.push(`${source.legacy}/ 与 ${source.canonical}/ 同时存在，优先使用 canonical。`);
    } else if (legacyCount > 0) {
      entries.push(`- ${source.legacy}/：legacy ${source.label}（${legacyCount} 个条目，仅 fallback）`);
    }
  }

  for (const [dir, label] of OPTIONAL_KNOWLEDGE_SOURCES) {
    const count = countMarkdownFiles(path.join(cwd, dir));
    if (count > 0) entries.push(`- ${dir}/：${label}（${count} 个条目）`);
  }

  if (!entries.length) return null;

  const shown = entries.slice(0, MAX_KNOWLEDGE_ENTRIES);
  const hiddenCount = entries.length - shown.length;
  if (hiddenCount > 0) shown.push(`- ...另有 ${hiddenCount} 个知识库入口，按任务需要再扫描。`);
  if (legacyNotes.length) shown.push(`迁移提示：${legacyNotes.slice(0, 3).join('；')}`);

  return `按需知识库：\n${shown.join('\n')}`;
}

function buildContext(cwd) {
  const blocks = [];
  const projectPath = path.join(cwd, 'openspec', 'project.md');
  const projectMeta = extractProjectMeta(readLines(projectPath));

  if (projectMeta) {
    blocks.push(`OpenSpec 项目上下文摘要：\n${projectMeta}\n\n实现前仍需按需读取 openspec/project.md。`);
  } else if (fs.existsSync(projectPath)) {
    blocks.push('OpenSpec 项目上下文：存在 openspec/project.md；编辑源码前先读取相关章节。');
  }

  const changeSummary = summarizeChanges(cwd);
  if (changeSummary) blocks.push(changeSummary);

  const memorySummary = summarizeMemory(cwd);
  if (memorySummary) blocks.push(memorySummary);

  const knowledgeSummary = summarizeKnowledge(cwd);
  if (knowledgeSummary) blocks.push(knowledgeSummary);

  return blocks.join('\n\n');
}

function outputContext(eventName, context) {
  if (!context) process.exit(0);

  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: eventName,
      additionalContext: context
    }
  }));
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { raw += chunk; });
process.stdin.on('end', () => {
  let input = {};
  try {
    input = raw.trim() ? JSON.parse(raw) : {};
  } catch {
    input = {};
  }

  const cwd = input.cwd || process.cwd();
  const eventName = input.hook_event_name || 'SessionStart';
  outputContext(eventName, buildContext(cwd));
});
