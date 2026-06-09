# Team Knowledge Guardrails

> 实验性功能：当前适合本地试用和工作流 dogfood，不建议作为公开稳定 contract 依赖。默认 onboarding 路径已经切到 `aisee knowledge init-repo` 和 `aisee knowledge configure`；远程仓库同步和 promote-batch 已可用。PR 自动化和 MCP 服务仍未稳定。

Team knowledge 用于跨项目复用少量经审查的工程经验，帮助 AI 在实现、review、verify 等阶段避免重复犯同类错误。

它不是：

- OpenSpec specs、active changes 或 baseline 的替代品；
- 项目 memory 的跨项目复制；
- `docs/solutions/` 或 reflect 文档的整库迁移；
- 通用知识问答系统；
- 向量库事实源。

## 当前可用能力

当前版本支持：

- 通过 `aisee knowledge init-repo --dest <path> --initial-pack <id> --json` 初始化独立 team knowledge 仓库骨架；
- 通过 `aisee knowledge configure --path <path> --enable-pack <id> --json` 写入业务项目侧 `aisee/knowledge.yaml`；
- 使用 marketplace-installed plugin 的 `skills/aisee-knowledge-curate/assets/team-knowledge/` 作为 contract-valid 示例模板，或使用外部 Git 仓库；
- 通过 `aisee knowledge inspect --json` 检查配置；
- 通过 `aisee knowledge doctor --json` 检查配置 path 与实际 team knowledge 目录是否一致；
- 通过 `aisee knowledge check --json` 或 `--team-path <path>` 校验 card / pack；
- 通过 `aisee knowledge install/update --json` 同步已配置的 Git team knowledge checkout；
- 通过 `aisee knowledge query ... --json` 检索少量 guardrails；
- 通过 `aisee knowledge index --json` 构建项目侧 cache，或用 `--team-path` 构建 team repo lexical cache；
- 通过 `aisee context pack --knowledge` 将少量 matches 注入实现上下文；
- 通过 `aisee:reflect` 生成项目内 reusable knowledge candidates；
- 通过 `aisee:knowledge-curate` 批量审查候选并生成 card drafts；
- 通过 `aisee knowledge promote-batch --curation <path> --team-path <path> --pack <id> --json` 把已审查 drafts 写入 team knowledge worktree。

当前不做：

- 自动把项目经验写入 team knowledge；
- 自动创建分支、提交、合并或 PR；
- 默认读取完整 card 正文；
- 直接扫描 `knowledge/cards/**/*.md` 给 AI 做上下文。

## 推荐配置

业务项目只 pin 自己需要的 packs。推荐通过 `aisee knowledge configure` 生成，而不是手工编辑：

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

V1 以本地 `path` 为主；`repo` 和 `ref` 用于记录来源与人工同步依据。`configure` 默认保留未显式覆盖的已有字段，并且不会复制整个知识库到业务项目。

## 读取方式

推荐初始化顺序：

```bash
aisee knowledge init-repo --dest ../aisee-team-knowledge --initial-pack web-app --json
aisee knowledge check --team-path ../aisee-team-knowledge --json
aisee knowledge configure --path ../aisee-team-knowledge --enable-pack web-app --json
aisee knowledge doctor --json
```

如果团队已经有静态模板仓库，或需要参考 marketplace 插件里的示例内容，`skills/aisee-knowledge-curate/assets/team-knowledge/` 仍然是 contract-valid 示例，但默认 onboarding 不再要求手工复制目录。

先检查配置：

```bash
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
```

`aisee knowledge check --json` 和 `--team-path <path>` 现在会在 `team_knowledge.write_ready` 中显式返回该仓库是否满足 `promote-batch` 的写入前置条件；如果 `write_ready` 为 `false`，通常表示 marker 或基础目录结构还没准备好。

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

需要刷新本地 checkout 时：

```bash
aisee knowledge install --json
aisee knowledge update --json
```

需要重建 cache 时：

```bash
aisee knowledge index --json
aisee knowledge index --team-path .aisee/team-knowledge --json
```

## 沉淀方式

知识沉淀默认由用户主动触发：

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> 用户确认后运行 aisee knowledge promote-batch
  -> 人工 review diff 后再 commit / PR
```

写入 team knowledge repo、创建分支、提交、合并或 PR 必须再次获得用户明确授权。`aisee knowledge promote-batch` 在写入前会校验 `.aisee-team-knowledge` marker 以及 `knowledge/packs`、`knowledge/cards` 结构，避免误把业务项目根目录当作 team repo。

## 稳定前缺口

公开稳定前还需要补齐：

- 更多真实 team knowledge card packs；
- stale card refresh 工作流；它是后续独立 change，不由 `aisee:verify`、reviewer lens 或 `aisee:knowledge-curate` 隐式执行；
- 可选 semantic rerank 或 MCP 包装，但不改变 Git + card/pack 事实源。

底层架构说明见 [Aisee Team Knowledge Architecture](architecture/aisee-team-knowledge.md)。
