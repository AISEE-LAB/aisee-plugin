# Knowledge Curate Workflow

## Step 1 — Candidate Inventory

读取：

- `aisee/docs/reflect/knowledge-candidates/**/*.md`
- `aisee/docs/reflect/**/*.md` 中明确标记的 reusable knowledge candidates
- 候选引用的 `docs/solutions/**/*.md` 摘要或 frontmatter

不要从全仓库任意 Markdown 推断候选。

## Step 2 — Eligibility Filter

保留满足以下条件的候选：

- 可跨项目复用；
- 触发条件可观察；
- `applies_to` 可以写清楚；
- 推荐动作可执行；
- boundaries 能防止误用；
- 不依赖当前项目私密业务背景。

拒绝或退回修改：

- 一次性上下文；
- 只适用于当前客户、私有部署或当前仓库的路径细节；
- 无法去敏；
- 本质上是具体 solution 正文；
- 没有证据来源且风险较高。

## Step 3 — Generalization

泛化时保留工程模式，移除项目私有细节。

示例：

```text
不要写：在 aisee-plugin 的 src/aisee_cli/context_pack.py 修改 knowledge 字段时...
应该写：修改公开 CLI JSON/context pack 输出字段时...
```

## Step 4 — Deduplication

去重顺序：

1. 项目内候选之间去重。
2. 与 project-local solutions evidence 去重。
3. 如果 `aisee/knowledge.yaml` 已配置 team repo/path，调用或建议调用 `aisee knowledge query` 检查 active cards。

重复处理：

- 已有 active team card 覆盖同一经验：不生成新 card，标记 `deduped_by`。
- 项目证据更新或更具体：保留 stale candidate note，建议 refresh 旧 card。
- 同一主题多个候选：合并为一个 draft，保留 evidence 列表。

## Step 5 — Draft Card

Card draft 必须包含：

```yaml
id:
title:
status: candidate
applies_to:
  stacks: []
  frameworks: []
  phases: []
  schemas: []
  surfaces: []
trigger: []
recommended_action: []
boundaries: []
```

Review info 可以包含：

```yaml
risk_types: []
tags: []
evidence: []
sensitive_information_check: []
dedupe: {}
```

## Step 6 — Output

输出 batch review report。只有用户明确要求写入文件时，写入：

```text
aisee/docs/reflect/knowledge-curation/YYYY-MM-DD_<slug>.md
```

不要自动写入 team knowledge repo。
