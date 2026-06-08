# Memory Rules

> 项目本地记忆规则。
> 本文件应写入项目根目录下的 `aisee/memory/rules.md`，与 `aisee/memory/index.md` 配套使用。

## 目录结构

使用项目记忆的项目必须遵循以下结构：

```text
{project-root}/
└── aisee/
    └── memory/
        ├── index.md       ← 入口文件；始终先读它
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

Slug 规则：小写、只用连字符、无空格、无特殊字符。
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

1. 始终先读 `aisee/memory/index.md`，不要直接扫描整个 `aisee/memory/` 树。
2. 只加载当前任务相关的具体记忆文件。
3. 写入前确认 `aisee/memory/` 位于项目根目录；不存在则在项目根目录创建。
4. 先写 memory 文件，再更新 `aisee/memory/index.md`。
5. 不要把项目记忆写到项目根目录之外的位置。
6. 无法判断项目根目录时，停止并询问用户，不要退回到全局路径。

违反第 5 或第 6 条属于严重执行错误。

## 记忆文件格式

每个记忆文件使用以下结构：

```markdown
# {标题}

**日期：** YYYY-MM-DD
**类型：** arch | pref | ctx | stack

## 摘要

一到两句话说明这条记忆记录了什么。

## 详情

正文内容。

## 引用

- 相关文件或链接（如有）
```
