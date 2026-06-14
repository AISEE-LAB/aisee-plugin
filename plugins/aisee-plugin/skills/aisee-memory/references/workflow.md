# Project Memory CLI Workflow

## 1. Inspect

检查当前项目是否已有项目记忆：

```bash
aisee memory inspect --json
```

读取重点：

- `memory.state`：`canonical`、`legacy-only`、`dual` 或 `missing`。
- `memory.policy.fact_source`：必须为 `false`。
- `memory.next_commands`：可用命令入口。
- `entries`：metadata 摘要，不含完整正文。

`aisee doctor --json` 不负责列出 memory 命令；memory 能力发现属于 `aisee memory inspect`。

## 2. Search

按任务检索少量相关记忆：

```bash
aisee memory search --query "<当前任务>" --json
aisee memory search --query "commit style" --type pref --json
```

默认行为：

- 只返回 active entries。
- 只返回 metadata，不返回完整正文。
- 默认最多 5 条，硬上限 20 条。
- `aisee/cache/memory-index.json` 只是 cache，不是事实源。

需要正文时显式请求 bounded excerpt：

```bash
aisee memory search --query "<当前任务>" --include-body --json
```

## 3. List

需要按类型或状态查看时使用：

```bash
aisee memory list --type pref --json
aisee memory list --status stale --json
```

不要把 `list --include-body` 当默认流程；只有确实需要正文时才使用。

## 4. Add

只有用户明确要求“记住 / 写入项目记忆 / 以后本项目都...”时才写入：

```bash
aisee memory add \
  --type pref \
  --title "提交信息语言" \
  --summary "本项目提交信息默认使用中文。" \
  --body "本项目 commit message 默认使用中文，并遵循 AGENTS.md 的提交规则。" \
  --source-ref AGENTS.md \
  --priority high \
  --json
```

写入规则：

- 新写入只使用 canonical `aisee/memory/`。
- `meta.writes` 必须为 `true`。
- CLI 会同步更新 `aisee/memory/index.md` 和 `aisee/cache/memory-index.json`。
- 不写 secrets、token、cookie、生产凭据或个人隐私。

## 5. Update Index

当用户怀疑索引漂移、手工修改过 memory 文件，或新增条目后需要重建 cache：

```bash
aisee memory update-index --json
```

`index.md` 是入口摘要；`aisee/cache/memory-index.json` 可删除、可重建，不是事实源。

## 6. Implementation Guidance

实现阶段如需带项目记忆，直接按当前任务检索：

```bash
aisee memory search --query "<当前任务>" --json
```

项目记忆仍然只是 guidance，不混入 OpenSpec facts。
