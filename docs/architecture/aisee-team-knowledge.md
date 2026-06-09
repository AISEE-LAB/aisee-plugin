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

推荐独立仓库。默认 onboarding 入口是 `aisee knowledge init-repo`，由 CLI 直接生成最小 contract-valid 仓库骨架；marketplace plugin 的 `skills/aisee-knowledge-curate/assets/team-knowledge/` 保留为 contract-valid 示例模板。PyPI CLI 不再从 wheel 复制本地 scaffold。

```text
aisee-team-knowledge/
  .aisee-team-knowledge
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

team knowledge 仓库内可解析、可审查的持久来源只有 `knowledge/cards/**` 和 `knowledge/packs/**`。`indexes/**` 是可删除、可重建缓存。它不改变 OpenSpec change、baseline specs、tasks、contracts 和 source-map 的规范事实源地位。

`.aisee-team-knowledge` 是 team repo 的写入保护 marker。任何会写入 team repo worktree 的 CLI 命令都应先校验 marker 和基础目录结构，避免误把业务项目根目录当作知识库。

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

推荐通过 `aisee knowledge configure --path <path> --enable-pack <id> --json` 写入或更新该文件，而不是手工编辑。`configure` 只修改项目侧 pin，不 clone、update 或写入 team repo。

当前 CLI 也提供 `aisee knowledge install --json` 和 `aisee knowledge update --json`，按 `repo/ref/path` 同步本地 Git checkout。同步命令默认拒绝 dirty checkout，避免覆盖人工编辑的 card 或 pack。

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

`aisee knowledge promote-batch --curation <path> --team-path <path> --pack <id> --json` 只负责把已审查 draft 写入本地 team knowledge worktree，并可幂等更新 pack。它不自动创建分支、commit、push、merge 或 PR。写入前会校验 `.aisee-team-knowledge` marker、`knowledge/packs` 和 `knowledge/cards` 是否存在。

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

## 索引与校验

`aisee knowledge check --team-path <path> --json` 校验 card / pack 的最小机器协议，包括必填字段、status、glob 安全、重复 ID 和 deprecated replacement。它还会返回 `team_knowledge.write_ready`，用于表达该仓库是否满足 `promote-batch` 的写入前置条件。

`aisee knowledge index --json` 写项目侧 cache：

```text
aisee/cache/knowledge-index.json
```

`aisee knowledge index --team-path <path> --json` 写 team repo cache：

```text
indexes/lexical-index.json
```

两类 index 都必须标记 `cache_is_fact_source: false`，删除后 CLI 必须能回退到 pack/card 文件读取。
