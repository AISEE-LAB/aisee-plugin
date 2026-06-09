# Knowledge Card Contract

本文定义 Aisee team knowledge 的最小可解析协议。目标是让 CLI 能按需读取、稳定过滤和小上下文输出，不把知识库做成第二套规范事实源。

## 定位

Team knowledge card 是经审查的工程 guardrail，不是 OpenSpec spec、change artifact、task list 或 source-map。

- OpenSpec/current change 是规范事实源。
- Project-local reflect/solution 是本地证据。
- Team active card 是可复用提醒。
- Index/vector/cache 都不是事实源。

## Repo Parse Contract

CLI 的默认读取入口固定为：

```text
<project>/aisee/knowledge.yaml
<team-knowledge>/knowledge/packs/*.yaml
<team-knowledge>/knowledge/cards/**/*.md
<team-knowledge>/knowledge/cards/**/*.yaml
```

独立 team knowledge 仓库的默认初始化入口是 `aisee knowledge init-repo --dest <path> --initial-pack <id> --json`。marketplace-installed plugin 的 `skills/aisee-knowledge-curate/assets/team-knowledge/` 仍是 contract-valid 示例模板，也可以使用团队维护的外部模板仓库。`aisee knowledge scaffold` 已从公开 CLI 命令面移除。配置完成后，用 `aisee knowledge configure --path <path> --enable-pack <id> --json` 写入项目 pin，再运行 `aisee knowledge doctor --json` 检查配置 path 与实际目录是否一致。需要预检该仓库能否被 `promote-batch` 写入时，可读取 `aisee knowledge check --team-path <path> --json` 返回中的 `team_knowledge.write_ready`。

读取顺序：

1. 读取项目 `aisee/knowledge.yaml`，获得 repo/path/ref/packs/retrieval。
2. 读取声明的 pack manifest。
3. 按 pack 中声明的 card ids 或 card globs 读取 card frontmatter/metadata。
4. 完成 status、pack、schema、phase、surface、stack 等硬过滤。
5. 仅对通过硬过滤的候选做 lexical scoring 和可选 semantic rerank。
6. 默认只输出命中 card 的摘要字段；只有 explain/debug 或用户显式请求时读取完整正文。

业务项目同步已 pin 仓库时使用 `aisee knowledge install --json` 或 `aisee knowledge update --json`。写入候选 card 时使用 `aisee knowledge promote-batch`，该命令只写本地 worktree，不执行 commit、push 或 PR，并且写入前要求 `.aisee-team-knowledge` marker。

CLI 不得默认递归扫描：

```text
docs/**
reviews/**
drafts/**
deprecated/**
任意 Markdown
```

这些目录可以存在，但只有被 pack 显式声明且通过 status 过滤时才参与读取。

## Project Config

业务项目只 pin team knowledge，不复制完整知识库：

```yaml
repo: git@github.com:org/aisee-team-knowledge.git
path: .aisee/team-knowledge
ref: v0.1.0
packs:
  - web-app
  - openspec
retrieval:
  max_cards: 3
  include_project_candidates: true
  vector: optional
```

`repo` 是远程来源，`path` 是本地 checkout 或 vendored fixture。`install` 和 `update` 可同步已 pin 的远程仓库，但仍属于实验性能力；业务项目不得把生成的 `context-index.json` 当作事实源。

## Pack Schema

Pack 是 CLI 读取 team knowledge 的入口。CLI 不从全仓库猜测有效 card。

```yaml
id: web-app
version: 0.1.0
status: active
description: Web app guardrails
applies_to:
  project_types: [web-app]
defaults:
  max_cards: 3
cards:
  - cli-json-output-stability
  - http-contract-backward-compatibility
card_globs:
  - knowledge/cards/frontend/*.md
disabled_cards: []
```

## Card Required Fields

Card 必填机器字段只服务于 CLI 硬过滤、轻量匹配和默认输出：

```yaml
id: cli-json-output-stability
title: CLI JSON 输出必须保持字段稳定
status: active
applies_to:
  stacks: [python]
  frameworks: []
  phases: [implementation, verify]
  schemas: []
  surfaces: [cli, json-output]
trigger:
  - 新增或修改 public CLI command
  - 修改 JSON 输出字段、错误 envelope 或退出码
recommended_action:
  - 保持新增字段向后兼容
  - 补充 CLI contract test
boundaries:
  - 不适用于仅面向人类的非 JSON 日志输出
```

Required 字段必须存在于 frontmatter 或 YAML card 顶层。Markdown 正文不得承担第一轮过滤所需的信息。

## Recommended Fields

推荐字段用于排序、审查和 explain，但不得成为第一轮检索硬依赖：

```yaml
risk_types: [public-contract]
tags: [cli, json-output]
evidence:
  - type: solution
    repo: aisee-plugin
    path: docs/solutions/cli/json-output-stability.md
```

`risk_types` 存在时可以参与过滤或降权；缺失时 card 仍然有效。

## Optional Fields

可选字段只在 curate、debug、explain 或人工 review 时按需读取：

```yaml
examples: []
deprecated_by:
review:
  reviewed_at:
  reviewer:
source_links: []
```

## Status Semantics

- `candidate`: 项目内或 team repo 中的候选知识，默认不参与业务项目检索。
- `active`: 已审查、可默认参与检索。
- `deprecated`: 已废弃，默认不参与检索；可以通过 `deprecated_by` 指向替代 card。

## Retrieval Output

默认 query 输出必须小而可解释：

```json
{
  "id": "cli-json-output-stability",
  "title": "CLI JSON 输出必须保持字段稳定",
  "match_reason": "current change touches public CLI JSON output",
  "recommended_action": ["补充 CLI contract test"],
  "boundaries": ["不适用于非 JSON 日志输出"],
  "source": {
    "pack": "web-app",
    "path": "knowledge/cards/cli/json-output-stability.md"
  },
  "dedupe": {
    "status": "unique"
  }
}
```

不得默认输出完整 card 正文。

## Deduplication

优先级：

1. OpenSpec/current change facts。
2. Project-local reflect/solution evidence。
3. Team active cards。

如果 project-local candidate 与 team active card 重叠，默认只注入 team card，并在 `dedupe` 中说明。如果 project-local evidence 更新或更具体，输出 stale candidate 提示，而不是重复注入两份知识。

## Sensitive Information Check

进入 team knowledge 前必须检查：

- secrets、tokens、cookies、private certificates；
- 客户名、个人信息、内部域名、生产 URL；
- 私有仓库路径和不能公开的业务细节；
- 复制自 `docs/solutions/` 的大段项目实现正文。

Card 应保留可验证 evidence link，但不复制 solution 正文。

## Index Boundary

允许的可重建缓存：

```text
indexes/lexical-index.json
indexes/vector-index/
aisee/cache/knowledge-index.json
```

缓存必须标记 `cache_is_fact_source: false`。删除缓存后，CLI 必须能退回 pack/card 按需读取。
