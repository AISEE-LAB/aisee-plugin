# Memory Rules

> 项目本地记忆规则。
> 本文件应写入项目根目录下的 `aisee/memory/rules.md`，与 `aisee/memory/index.md` 配套使用。

## 目录结构

使用项目记忆的项目必须遵循以下结构：

```text
{project-root}/
└── aisee/
    └── memory/
        ├── index.md       ← 入口摘要；由 CLI 重建
        ├── rules.md       ← 写入与读取规则
        ├── arch/          ← 架构决策，长期保留
        │   └── YYYY-MM-DD-{slug}.md
        ├── pref/          ← 用户偏好，如风格、工具、习惯
        │   └── {topic}.md
        ├── ctx/           ← 上下文快照，约 30 天过期
        │   └── YYYY-MM-DD-{slug}.md
        └── stack/         ← 技术栈笔记，如版本、配置、已知问题
            └── {technology}.md
```

## 命名规则

| 目录 | 文件名格式 | 保留策略 | 更新策略 |
|---|---|---|---|
| `arch/` | `YYYY-MM-DD-{slug}.md` | 长期 | 每个决策追加新文件 |
| `pref/` | `{topic}.md` | 长期 | 偏好变化时覆盖 |
| `ctx/` | `YYYY-MM-DD-{slug}.md` | 约 30 天 | 每次快照追加新文件 |
| `stack/` | `{technology}.md` | 长期 | 技术栈信息变化时覆盖 |

Slug 由 `aisee memory add` 自动生成：小写、只用连字符、无空格、无特殊字符；中文标题会生成安全 hash slug。
示例：`use-postgres`、`auth-refactor`、`drop-redux`。

## index.md 格式

`index.md` 是扁平链接列表，只放一行摘要，不放正文。

```markdown
# Memory Index

## 架构决策（arch/）

- [YYYY-MM-DD] <一句话摘要> → arch/YYYY-MM-DD-{slug}.md

## 用户偏好（pref/）

- <一句话摘要> → pref/{topic}.md

## 上下文快照（ctx/）

- [YYYY-MM-DD] <一句话摘要> → ctx/YYYY-MM-DD-{slug}.md

## 技术栈笔记（stack/）

- <一句话摘要> → stack/{technology}.md
```

## 执行规则

1. 使用 `aisee memory inspect --json` 发现项目记忆状态和命令入口。
2. 使用 `aisee memory search --query "<task>" --json` 只加载当前任务相关记忆。
3. 只有需要正文时才显式使用 `--include-body`。
4. 写入必须来自用户明确意图，并通过 `aisee memory add ... --json` 写入 canonical `aisee/memory/`。
5. 重建入口和 cache 使用 `aisee memory update-index --json`。
6. 不要把项目记忆写到项目根目录之外的位置。
7. 无法判断项目根目录时，停止并询问用户，不要退回到全局路径。

违反第 6 或第 7 条属于严重执行错误。

## 记忆文件格式

CLI 新写入的每个记忆文件使用 YAML frontmatter + Markdown 正文。旧粗体 metadata 只作为 legacy fallback 读取，不再作为新写入格式。

```markdown
---
id: <safe-slug>
title: <标题>
type: arch | pref | ctx | stack
status: active
priority: high | normal | low
summary: <一句话摘要>
source_refs: []
updated_at: <ISO datetime>
---

# <标题>

正文内容。
```
