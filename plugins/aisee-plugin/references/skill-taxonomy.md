# Aisee Skill Taxonomy

本文定义单一 `aisee-plugin` 内公开 skill 的分层治理合同。Codex manifest 继续暴露 `./skills/`；分层约束通过文档与测试守住，而不是通过拆插件改变安装模型。

## Core Workflow

默认 happy path 只包含 11 个核心主流程 skill：

- `aisee:flow`
- `aisee:init`
- `aisee:srs`
- `aisee:ui-content`
- `aisee:architecture`
- `aisee:change-plan`
- `aisee:change-author`
- `aisee-schema-pack`
- `aisee:implementation-bridge`
- `aisee:verify`
- `aisee:archive-guard`

## Optional Extensions

以下 skill 继续公开暴露，但只在特定场景按需触发，不进入默认 happy path：

- `aisee:design-spec`
- `aisee:design-assets`
- `aisee:svg-assets`
- `aisee:image-object`
- `aisee:spec-migrate`

## Knowledge Loop

以下 skill 服务项目内复盘、审查和团队知识沉淀，不是每次迭代必经节点：

- `aisee:reflect`
- `aisee:knowledge-curate`

## Hardware / Experimental

以下 skill 面向硬件、嵌入式或实验域；它们继续作为同插件内公开能力存在，但不影响 app 默认路径：

- `hw:srs`
- `hw:architecture`
- `hw:init`
- `hw:change-plan`

## Governance Rules

- 所有公开 `plugins/aisee-plugin/skills/*/SKILL.md` 都必须出现在本分类中。
- `Core Workflow` 的 skill 集合和数量属于 public workflow contract；变更时必须同步 README、workflow、compatibility policy、release notes 和测试。
- `Optional Extensions`、`Knowledge Loop`、`Hardware / Experimental` 继续公开暴露，但不得在默认新功能 happy path 中伪装成必经节点。
- 所有公开 skill 都必须提供 `evals/evals.json`；taxonomy 只能标记覆盖深度优先级，不能豁免 eval 准入。
