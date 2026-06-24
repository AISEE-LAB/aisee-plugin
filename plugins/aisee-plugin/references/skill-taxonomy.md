# Aisee Skill Taxonomy

本文定义单一 `aisee-plugin` 内公开 skill 的当前分层合同。Codex manifest 继续暴露 `./skills/`；分层约束通过文档与测试守住，而不是通过拆插件改变安装模型。

## Project Setup / Adoption

以下 skill 用于 OpenSpec 接入、初始化、配置审计和治理；它们不是默认新需求 / 新 change 的必经节点：

- `aisee:init`

## OpenSpec Core

以下 skill 构成 Aisee 当前主推的 OpenSpec companion 能力：

- `aisee:spec-migrate`
- `aisee:srs`
- `aisee:change-plan`
- `aisee:change-author`

## Memory And Knowledge

以下 skill 服务项目记忆、团队 guardrails 和候选沉淀，不替代 OpenSpec 事实源：

- `aisee:reflect`
- `aisee:memory`
- `aisee:knowledge`
- `aisee:knowledge-curate`

## Legacy / Transitional

以下 skill 当前仍公开存在，但不再属于主推产品面，后续会收敛、迁移或删除：

- `aisee:design-spec`
- `aisee:design-assets`
- `aisee:svg-assets`
- `aisee:image-object`

## Hardware / Experimental

以下 skill 面向硬件、嵌入式或实验域；它们继续作为同插件内公开能力存在，但不影响当前 OpenSpec companion 主路径：

- `hw:srs`
- `hw:architecture`
- `hw:init`
- `hw:change-plan`

## Governance Rules

- 所有公开 `plugins/aisee-plugin/skills/*/SKILL.md` 都必须出现在本分类中。
- `Project Setup / Adoption`、`OpenSpec Core`、`Memory And Knowledge`、`Legacy / Transitional` 与 `Hardware / Experimental` 的 skill 集合属于 public plugin content contract；变更时必须同步 README、workflow、compatibility policy、release notes 和测试。
- `Legacy / Transitional` 中的 skill 不得继续在 README、workflow、defaultPrompt 或初始化模板中伪装成当前主推路径。
- 所有公开 skill 都必须提供 `evals/evals.json`；taxonomy 只能标记覆盖深度优先级，不能豁免 eval 准入。
