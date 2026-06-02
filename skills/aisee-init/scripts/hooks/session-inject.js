#!/usr/bin/env node
/**
 * Injects compact OpenSpec context at session start.
 * Never reads full project files; it emits pointers and small summaries only.
 */
'use strict';

const fs = require('fs');
const path = require('path');

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

function existingPath(cwd, preferred, legacy) {
  const preferredPath = path.join(cwd, preferred);
  if (fs.existsSync(preferredPath)) return preferredPath;
  const legacyPath = path.join(cwd, legacy);
  if (fs.existsSync(legacyPath)) return legacyPath;
  return preferredPath;
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

function buildContext(cwd) {
  const blocks = [];
  const projectPath = path.join(cwd, 'openspec', 'project.md');
  const projectMeta = extractProjectMeta(readLines(projectPath));

  if (projectMeta) {
    blocks.push(`OpenSpec 项目上下文摘要：\n${projectMeta}\n\n实现前仍需按需读取 openspec/project.md。`);
  } else if (fs.existsSync(projectPath)) {
    blocks.push('OpenSpec 项目上下文：存在 openspec/project.md；编辑源码前先读取相关章节。');
  }

  const changes = listDirs(path.join(cwd, 'openspec', 'changes'));
  if (changes.length) {
    blocks.push([
      `活跃 OpenSpec changes（${changes.length}）：`,
      ...changes.map(name => `- openspec/changes/${name}/`),
      '实现前先读取 .openspec.yaml / openspec/config.yaml 判断 schema，再按该 schema 的 artifact 依赖读取对应文件。'
    ].join('\n'));
  }

  const memoryRulesPath = existingPath(cwd, path.join('aisee', 'memory', 'rules.md'), path.join('.memory', 'rules.md'));
  const memoryIndexPath = existingPath(cwd, path.join('aisee', 'memory', 'index.md'), path.join('.memory', 'index.md'));
  if (fs.existsSync(memoryRulesPath) || fs.existsSync(memoryIndexPath)) {
    const memoryFiles = [
      fs.existsSync(memoryRulesPath) && path.relative(cwd, memoryRulesPath),
      fs.existsSync(memoryIndexPath) && path.relative(cwd, memoryIndexPath)
    ].filter(Boolean).join('、');
    blocks.push(`项目记忆入口：${memoryFiles}。先读规则和索引，再只加载本任务相关条目。`);
  }

  const knowledge = [
    ['aisee/docs/requirements', 'SRS 与 FR 来源，仅用于追溯，不能替代 openspec/'],
    ['aisee/docs/ui-content', '页面内容、元素、状态和交互来源'],
    ['aisee/docs/architecture', '技术架构事实、决策、项目约束、共享前置和风险来源'],
    ['aisee/docs/change-plan', 'change 边界规划结果，后续仍需创建 OpenSpec artifacts'],
    ['aisee/docs/reflect', '会话反思与 memory 候选'],
    ['docs/requirements', 'legacy SRS 与 FR 来源，仅用于追溯，不能替代 openspec/'],
    ['docs/ui-content', 'legacy 页面内容、元素、状态和交互来源'],
    ['docs/architecture', 'legacy 技术架构事实、决策、项目约束、共享前置和风险来源'],
    ['docs/change-plan', 'legacy change 边界规划结果，后续仍需创建 OpenSpec artifacts'],
    ['docs/learnings', '团队复盘与模式库'],
    ['docs/solutions', '历史解决方案'],
    ['docs/reflect', 'legacy 会话反思与 memory 候选']
  ]
    .map(([dir, label]) => [dir, label, countMarkdownFiles(path.join(cwd, dir))])
    .filter(([, , count]) => count > 0)
    .map(([dir, label, count]) => `- ${dir}/：${label}（${count} 个条目）`);

  if (knowledge.length) {
    blocks.push(`按需知识库：\n${knowledge.join('\n')}`);
  }

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
