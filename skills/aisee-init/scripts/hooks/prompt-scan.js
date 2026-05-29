#!/usr/bin/env node
/**
 * Blocks obvious secret leakage in user prompts and supported tool inputs.
 * Compatible with Codex hook JSON.
 */
'use strict';

const PATTERNS = [
  { re: /sk-[A-Za-z0-9_-]{20,}/, label: 'OpenAI API key' },
  { re: /ghp_[A-Za-z0-9]{36}/, label: 'GitHub personal access token' },
  { re: /github_pat_[A-Za-z0-9_]{20,}/, label: 'GitHub fine-grained token' },
  { re: /AKIA[0-9A-Z]{16}/, label: 'AWS access key' },
  { re: /xox[baprs]-[A-Za-z0-9-]{10,}/, label: 'Slack token' },
  { re: /-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/, label: 'private key' }
];

function readStdin(callback) {
  let raw = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => { raw += chunk; });
  process.stdin.on('end', () => callback(raw));
}

function parseInput(raw) {
  if (!raw.trim()) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function collectText(value, depth = 0) {
  if (value == null || depth > 5) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map(item => collectText(item, depth + 1)).join('\n');
  if (typeof value === 'object') {
    return Object.values(value).map(item => collectText(item, depth + 1)).join('\n');
  }
  return '';
}

function textForScan(input) {
  return [
    input.prompt,
    input.tool_input,
    input.command,
    input.message
  ].map(collectText).join('\n');
}

function blockPayload(eventName, reason) {
  if (eventName === 'PreToolUse' || eventName === 'PermissionRequest') {
    return {
      decision: 'block',
      reason,
      hookSpecificOutput: {
        hookEventName: eventName,
        permissionDecision: 'deny',
        permissionDecisionReason: reason
      }
    };
  }

  return {
    decision: 'block',
    reason
  };
}

readStdin(raw => {
  const input = parseInput(raw);
  const eventName = input.hook_event_name || 'UserPromptSubmit';
  const text = textForScan(input);
  const hit = PATTERNS.find(pattern => pattern.re.test(text));

  if (!hit) process.exit(0);

  const reason = `检测到疑似密钥：${hit.label}。请移除敏感内容后重新提交。`;
  process.stdout.write(JSON.stringify(blockPayload(eventName, reason)));
});
