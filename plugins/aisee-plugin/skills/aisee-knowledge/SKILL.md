---
name: aisee:knowledge
description: 引导团队知识 CLI 的日常使用。用于用户询问团队知识是否可用、如何初始化或接入 team knowledge、如何同步知识仓库、如何查询 guardrails、如何把已审查 drafts 写入 team knowledge，或提到 aisee knowledge、knowledge.yaml、team knowledge、团队知识命令时触发。它负责选择和执行 `aisee knowledge` 命令；候选知识审查和 card draft 生成仍转交 `aisee:knowledge-curate`。
---

# aisee:knowledge

引导团队知识 CLI 的低门槛使用：初始化、配置、检查、同步、检索和已审查 drafts 的写入。

## 职责

- 检查业务项目是否已配置 `aisee/knowledge.yaml`。
- 使用 `aisee knowledge inspect/doctor/check` 判断 team knowledge 状态。
- 使用 `init-repo` 和 `configure` 建立最小可用团队知识链路。
- 使用 `install/update` 同步已 pin 的 Git team knowledge checkout。
- 使用 `query` 给实现、审查和验证提供少量 guardrails。
- 在用户明确授权后，使用 `promote-batch` 把已审查 curation report 写入本地 team knowledge worktree。

## 不负责

- 不审查、去敏、泛化项目候选知识；这属于 `aisee:knowledge-curate`。
- 不从聊天记录或全仓库 Markdown 临时生成 active team card。
- 不让 team knowledge 替代 OpenSpec specs、tasks、contracts、source-map 或 baseline。
- 不把 `aisee/cache/knowledge-index.json` 当事实源。
- 不自动创建分支、commit、push、merge 或 PR。

## Workflow

按用户目标选择模式；需要命令细节时读取 `references/workflow.md`。

| 用户目标 | 处理方式 |
|---|---|
| “检查团队知识是否可用” | 运行 `aisee knowledge inspect --json`、`doctor --json`，必要时 `check --json`。 |
| “初始化团队知识库” | 先说明写入路径，用户确认后运行 `init-repo`，再 `configure`。 |
| “配置当前项目使用团队知识” | 运行 `configure --path <path> --enable-pack <pack>`，再 `doctor`。 |
| “同步团队知识” | 检查 `knowledge.yaml` 后运行 `install` 或 `update`。 |
| “查询可复用经验” | 运行 `query`；有明确 change 时优先 `query --from-change <change> --for ce-work`。 |
| “实现时带团队知识” | 使用 `aisee knowledge query --from-change <change> --for ce-work --json`。 |
| “把候选沉淀到团队知识” | 若还没有审查报告，转交 `aisee:knowledge-curate`；已有 report 且用户授权后使用 `promote-batch`。 |

## Guardrails

- 写入 `aisee/knowledge.yaml`、team knowledge repo 或 cache 前，说明将写入的路径和命令。
- `promote-batch` 前必须确认目标路径是 team knowledge worktree，并优先运行 `aisee knowledge check --team-path <path> --json`。
- `promote-batch` 默认写入 candidate；只有用户明确要求激活时才传 `--activate`。
- `install/update` 只处理已配置的 Git checkout；dirty checkout 被阻断时不要自动清理。
- 最终回复说明运行过的命令、状态、写入路径、命中 card 数量和剩余风险。
