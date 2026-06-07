# Team Knowledge Guardrails

> 实验性功能：当前适合本地试用和工作流 dogfood，不建议作为公开稳定 contract 依赖。远程仓库安装、自动同步、promote-batch、PR 自动化和 MCP 服务仍未稳定。

Team knowledge 用于跨项目复用少量经审查的工程经验，帮助 AI 在实现、review、verify 等阶段避免重复犯同类错误。

它不是：

- OpenSpec specs、active changes 或 baseline 的替代品；
- 项目 memory 的跨项目复制；
- `docs/solutions/` 或 reflect 文档的整库迁移；
- 通用知识问答系统；
- 向量库事实源。

## 当前可用能力

当前版本支持：

- 在业务项目中通过 `aisee/knowledge.yaml` pin 本地 team knowledge 路径、ref 和 packs；
- 通过 `aisee knowledge inspect --json` 检查配置；
- 通过 `aisee knowledge query ... --json` 检索少量 guardrails；
- 通过 `aisee context pack --knowledge` 将少量 matches 注入实现上下文；
- 通过 `aisee:reflect` 生成项目内 reusable knowledge candidates；
- 通过 `aisee:knowledge-curate` 批量审查候选并生成 card drafts。

当前不做：

- 自动 clone 或更新远程 team knowledge 仓库；
- 自动把项目经验写入 team knowledge；
- 自动创建分支、提交、合并或 PR；
- 默认读取完整 card 正文；
- 直接扫描 `knowledge/cards/**/*.md` 给 AI 做上下文。

## 推荐配置

业务项目只 pin 自己需要的 packs：

```yaml
repo: git@example.com:org/aisee-team-knowledge.git
path: .aisee/team-knowledge
ref: v0.1.0
packs:
  - web-app
retrieval:
  max_cards: 3
  include_project_candidates: true
```

V1 以本地 `path` 为主；`repo` 和 `ref` 用于记录来源与人工同步依据。

## 读取方式

先检查配置：

```bash
aisee knowledge inspect --json
```

按阶段和场景查询：

```bash
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
```

基于当前 change 查询：

```bash
aisee knowledge query --from-change <change> --for ce-work --json
```

在 context pack 中显式启用：

```bash
aisee context pack --change <change> --for ce-work --knowledge --json
```

## 沉淀方式

知识沉淀默认由用户主动触发：

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> 用户确认后再写入独立 team knowledge 仓库
```

写入 team knowledge repo、创建分支、提交、合并或 PR 必须再次获得用户明确授权。

## 稳定前缺口

公开稳定前还需要补齐：

- 独立 `aisee-team-knowledge` 仓库 scaffold；
- card / pack schema 示例和测试 fixtures；
- `aisee knowledge install/update` 或等价同步流程；
- `aisee knowledge promote-batch` 或等价人工提交辅助；
- stale / deprecated card 生命周期；
- 可选 semantic rerank 或 MCP 包装，但不改变 Git + card/pack 事实源。

底层架构说明见 [Aisee Team Knowledge Architecture](architecture/aisee-team-knowledge.md)。
