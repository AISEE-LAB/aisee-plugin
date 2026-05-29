#!/usr/bin/env node
/**
 * Adds a lightweight spec-scope self-check when a prompt appears to extend scope.
 * It does not call an external model; the active assistant receives compact context.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const THRESHOLD = 3;

const SIGNALS = [
  { pattern: /另外|顺便|还需要|我还想|能不能加|新增|补充一个|加一个|追加/, weight: 3 },
  { pattern: /new feature|add a|also need|can we add|in addition|additionally/i, weight: 3 },
  { pattern: /能否|可以加|要不要|是否支持|新功能|新模块|新页面|新接口/, weight: 2 },
  { pattern: /could we|what about|how about|support for|new (module|page|api)/i, weight: 2 },
  { pattern: /改一下|调整|换成|修改|扩展|升级/, weight: 1 },
  { pattern: /change|modify|update|extend|upgrade/i, weight: 1 }
];

const IGNORE_PATTERNS = [
  /^(yes|no|ok|好|不|是|否|继续|确认|生成|执行|done|完成)[\s.!。]*$/i,
  /^(thanks|谢谢|thank you|好的)/i,
  /fix (the )?(bug|error|issue|typo)/i,
  /运行|测试|部署|install|npm|pnpm|yarn|git/i
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

  return out.join(' ').slice(0, 500);
}

function taskExcerpt(filePath, maxTasks = 15) {
  if (!fs.existsSync(filePath)) return [];
  return fs.readFileSync(filePath, 'utf8')
    .split('\n')
    .filter(line => /^\s*-\s*\[[ xX]\]/.test(line))
    .map(line => line.trim().replace(/^-\s*\[[ xX]\]\s*/, ''))
    .slice(0, maxTasks);
}

function specSummaries(cwd) {
  return activeChanges(cwd).map(changeDir => {
    const change = path.basename(changeDir);
    const proposal = sectionExcerpt(
      path.join(changeDir, 'proposal.md'),
      /^#+\s*(what|scope|做什么|功能范围|范围)/i
    );
    const design = sectionExcerpt(
      path.join(changeDir, 'design.md'),
      /^#+\s*(architecture|design|方案|架构)/i,
      6
    );
    const tasks = taskExcerpt(path.join(changeDir, 'tasks.md'));
    return { change, proposal, design, tasks };
  }).filter(summary => summary.proposal || summary.design || summary.tasks.length);
}

function buildInjection(prompt, summaries) {
  const specText = summaries.map(summary => {
    const parts = [`Change：${summary.change}`];
    if (summary.proposal) parts.push(`Proposal 范围：${summary.proposal}`);
    if (summary.design) parts.push(`Design 摘要：${summary.design}`);
    if (summary.tasks.length) parts.push(`Tasks：\n${summary.tasks.map(task => `- ${task}`).join('\n')}`);
    return parts.join('\n');
  }).join('\n\n');

  return [
    '[OpenSpec 范围自检]',
    '用户请求可能引入当前 OpenSpec 范围之外的内容。回答前先判断请求是否仍属于现有 change。',
    '',
    '当前 spec 摘要：',
    specText,
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

  const summaries = specSummaries(cwd);
  if (!summaries.length) process.exit(0);

  outputAdditionalContext(eventName, buildInjection(prompt, summaries));
});
