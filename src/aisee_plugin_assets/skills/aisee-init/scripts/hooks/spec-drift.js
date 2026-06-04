#!/usr/bin/env node
/**
 * Adds a lightweight spec-scope self-check when a prompt appears to extend scope.
 * It does not call an external model; the active assistant receives compact context.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const THRESHOLD = 3;
const MAX_CHANGE_SUMMARIES = 3;
const MAX_TASKS = 8;
const MAX_EXCERPT_CHARS = 420;

const SIGNALS = [
  { pattern: /另外|顺便|还需要|我还想|能不能加|新增|补充一个|加一个|追加/, weight: 3 },
  { pattern: /new feature|add a|also need|can we add|in addition|additionally/i, weight: 3 },
  { pattern: /能否|可以加|要不要|是否支持|新功能|新模块|新页面|新接口/, weight: 2 },
  { pattern: /could we|what about|how about|support for|new (module|page|api)/i, weight: 2 },
  { pattern: /改一下|调整|换成|修改|扩展|升级/, weight: 1 },
  { pattern: /change|modify|update|extend|upgrade/i, weight: 1 }
];

const IGNORE_PATTERNS = [
  /^(yes|no|ok|好|不|是|否|继续|确认|生成|执行|提交|done|完成|commit)[\s.!。]*$/i,
  /^(thanks|谢谢|thank you|好的)/i,
  /fix (the )?(bug|error|issue|typo)/i,
  /运行|测试|部署|install|npm|pnpm|yarn|git|提交|commit|push/i
];

const ARTIFACT_EXCERPTS = [
  {
    file: 'proposal.md',
    label: 'Proposal 范围',
    heading: /^#+\s*(what|scope|做什么|功能范围|范围)/i,
    lines: 8
  },
  {
    file: 'source-map.md',
    label: 'Source Map 摘要',
    heading: /^#+\s*(upstream|sources|id trace|affected paths|artifact applicability|来源|影响路径|适用性)/i,
    lines: 6
  },
  {
    file: 'change-context.md',
    label: 'Change Context 摘要',
    heading: /^#+\s*(context|scope|constraints|上下文|范围|约束)/i,
    lines: 5
  },
  {
    file: 'ui-contract.md',
    label: 'UI Contract 摘要',
    heading: /^#+\s*(ui|pages|states|actions|页面|状态|操作)/i,
    lines: 5
  },
  {
    file: 'service-contract.md',
    label: 'Service Contract 摘要',
    heading: /^#+\s*(api|service|contract|接口|服务|契约)/i,
    lines: 5
  },
  {
    file: 'data-model.md',
    label: 'Data Model 摘要',
    heading: /^#+\s*(data|model|entities|schema|数据|模型|实体)/i,
    lines: 5
  }
];

function scorePrompt(prompt) {
  return SIGNALS.reduce((sum, { pattern, weight }) => sum + (pattern.test(prompt) ? weight : 0), 0);
}

function shouldIgnore(prompt) {
  return IGNORE_PATTERNS.some(pattern => pattern.test(prompt.trim()));
}

function activeChanges(cwd) {
  const changesDir = path.join(cwd, 'openspec', 'changes');
  try {
    return fs.readdirSync(changesDir)
      .filter(name => name !== 'archive')
      .filter(name => fs.statSync(path.join(changesDir, name)).isDirectory())
      .sort()
      .map(name => path.join(changesDir, name));
  } catch {
    return [];
  }
}

function sectionExcerpt(filePath, headingPattern, maxLines = 8) {
  if (!fs.existsSync(filePath)) return '';
  const lines = fs.readFileSync(filePath, 'utf8').split('\n');
  const out = [];
  let inSection = false;

  for (const line of lines) {
    if (headingPattern.test(line)) {
      inSection = true;
      continue;
    }
    if (inSection && /^#+\s+/.test(line)) break;
    if (inSection && line.trim()) out.push(line.trim());
    if (out.length >= maxLines) break;
  }

  return out.join(' ').slice(0, MAX_EXCERPT_CHARS);
}

function taskExcerpt(filePath, maxTasks = 15) {
  if (!fs.existsSync(filePath)) return [];
  return fs.readFileSync(filePath, 'utf8')
    .split('\n')
    .filter(line => /^\s*-\s*\[[ xX]\]/.test(line))
    .map(line => line.trim().replace(/^-\s*\[[ xX]\]\s*/, ''))
    .slice(0, maxTasks);
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

function selectedChanges(prompt, changes) {
  const lowerPrompt = prompt.toLowerCase();
  const matched = changes.filter(changeDir => lowerPrompt.includes(path.basename(changeDir).toLowerCase()));
  if (matched.length) return { changes: matched.slice(0, MAX_CHANGE_SUMMARIES), truncated: matched.length > MAX_CHANGE_SUMMARIES };
  return {
    changes: changes.slice(0, MAX_CHANGE_SUMMARIES),
    truncated: changes.length > MAX_CHANGE_SUMMARIES
  };
}

function artifactExcerpts(changeDir) {
  return ARTIFACT_EXCERPTS
    .map(({ file, label, heading, lines }) => {
      const text = sectionExcerpt(path.join(changeDir, file), heading, lines);
      return text ? { label, text } : null;
    })
    .filter(Boolean);
}

function specSummaries(cwd, prompt) {
  const allChanges = activeChanges(cwd);
  const selection = selectedChanges(prompt, allChanges);
  const summaries = selection.changes.map(changeDir => {
    const change = path.basename(changeDir);
    const schema = schemaName(changeDir, cwd);
    const artifacts = artifactExcerpts(changeDir);
    const tasks = taskExcerpt(path.join(changeDir, 'tasks.md'), MAX_TASKS);
    return { change, schema, artifacts, tasks };
  }).filter(summary => summary.artifacts.length || summary.tasks.length);

  return {
    activeChangeNames: allChanges.map(changeDir => path.basename(changeDir)),
    truncated: selection.truncated,
    summaries
  };
}

function buildInjection(prompt, data) {
  const specText = data.summaries.map(summary => {
    const parts = [`Change：${summary.change}`, `Schema：${summary.schema}`];
    for (const artifact of summary.artifacts) parts.push(`${artifact.label}：${artifact.text}`);
    if (summary.tasks.length) parts.push(`Tasks：\n${summary.tasks.map(task => `- ${task}`).join('\n')}`);
    return parts.join('\n');
  }).join('\n\n');

  const activeList = data.activeChangeNames.length
    ? `活跃 changes：${data.activeChangeNames.map(name => `openspec/changes/${name}/`).join('、')}`
    : '';
  const truncationNote = data.truncated
    ? '活跃 change 较多且用户未明确指定 change；只展示部分摘要。回答前先确认目标 change，避免把多个 change 混在一起。'
    : '';

  return [
    '[OpenSpec 范围自检]',
    '用户请求可能引入当前 OpenSpec 范围之外的内容。回答前先判断请求是否仍属于现有 change。',
    activeList,
    truncationNote,
    '',
    '当前 spec 摘要：',
    specText || '未找到可摘要的 proposal/source-map/contract/tasks。先读取目标 change 的 schema 和 artifacts，不要凭 hook 摘要做结论。',
    '',
    `用户请求：${prompt}`,
    '',
    '如果越界：用 [SPEC-CHANGE-REQUIRED] 或 [SPEC-GAP] 明确说明，并建议更新 openspec/changes/<feature>/ 后再继续。',
    '如果未越界：正常继续，不要提及本 hook。'
  ].join('\n');
}

function outputAdditionalContext(eventName, context) {
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
  if (process.env.SPEC_DRIFT_DISABLED === '1') process.exit(0);

  let input = {};
  try {
    input = raw.trim() ? JSON.parse(raw) : {};
  } catch {
    input = {};
  }

  const prompt = input.prompt || input.tool_input?.prompt || '';
  const cwd = input.cwd || process.cwd();
  const eventName = input.hook_event_name || 'UserPromptSubmit';

  if (!prompt || shouldIgnore(prompt) || scorePrompt(prompt) < THRESHOLD) process.exit(0);

  const data = specSummaries(cwd, prompt);
  if (!data.activeChangeNames.length) process.exit(0);

  outputAdditionalContext(eventName, buildInjection(prompt, data));
});
