# Aisee Team Knowledge Architecture

本文说明 Aisee team knowledge 的仓库边界、读取模型和沉淀流程。

## 目标

Team knowledge 解决跨项目复用工程经验的问题。它向 AI 提供少量经审查的 guardrails，避免重复踩坑。

它不负责：

- 替代 OpenSpec specs 或 active changes；
- 保存完整项目 memory；
- 复制 `docs/solutions/` 正文；
- 做通用知识问答；
- 作为向量库或缓存事实源。

## 仓库结构

推荐独立仓库：

```text
aisee-team-knowledge/
  AGENTS.md
  README.md
  knowledge/
    cards/
      frontend/
      backend/
      cli/
      openspec/
      security/
      testing/
    packs/
      web-app.yaml
      backend-service.yaml
      openspec.yaml
      aisee-plugin.yaml
    deprecated/
  schemas/
    knowledge-card.schema.json
    knowledge-pack.schema.json
  docs/
    authoring-guide.md
    review-policy.md
  indexes/
    lexical-index.json
    vector-index/
```

事实源只有 `knowledge/cards/**` 和 `knowledge/packs/**`。`indexes/**` 是可删除、可重建缓存。

## 业务项目配置

业务项目使用 `aisee/knowledge.yaml` pin 所需 packs：

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

V1 可以只支持本地 `path`，不自动 clone 远程仓库。

## 读取模型

CLI 负责 knowledge retrieval 的全部边界控制：

1. 读项目配置。
2. 读 pack manifest。
3. 读 pack 声明的 card frontmatter。
4. 做 status、pack、schema、phase、surface、stack 硬过滤。
5. 对通过过滤的候选做 lexical scoring。
6. 按需做 semantic rerank。
7. 执行 project-local / team knowledge 去重。
8. 输出 top N guardrails。

Skill 和 AI 提示不得直接扫描 `knowledge/cards/**/*.md`。所有调用都应通过：

```bash
aisee knowledge query ...
```

## 语义匹配边界

Semantic matching 只能作用于硬过滤后的候选集。它不能绕过 pack、status、phase、surface、stack 和可用 risk signals 做全库召回。

默认输出最多 3 条 matches。安全、权限、公开接口、架构类知识宁可少召回，不做宽召回。

## 沉淀流程

知识沉淀分三层：

1. `aisee:reflect`：用户主动触发，生成项目内 reusable knowledge candidate。
2. `aisee:knowledge-curate`：用户主动或阶段性触发，批量去敏、泛化、去重、补边界并产出 card drafts。
3. Team knowledge repo 写入：必须用户明确授权，且应以 batch PR 为默认策略。

`aisee:archive-guard`、`aisee:verify` 或 `aisee:reflect` 可以提示候选信号，但不得自动写入项目候选或 team knowledge。

## 与 Compound 的边界

`ce-compound` 继续记录具体工程问题和解决方案。Team knowledge card 可以引用 solution 作为 evidence，但不复制 solution 正文。

`ce-compound-refresh` 继续维护 `docs/solutions/`。Team knowledge refresh 是后续独立流程，不混入 Compound refresh。

## 去重规则

检索输出优先级：

1. OpenSpec/current change facts 最高。
2. Project-local evidence 是本地上下文。
3. Team active card 是经审查 guardrail。

如果 project-local candidate 与 team active card 重叠，默认只输出 team card，并在 `dedupe` 中说明。如果 project-local evidence 更新或更具体，输出 stale candidate 提示，避免重复注入两份知识。
