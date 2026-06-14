# Context Pack Targets

本文是 `aisee context pack --for <target>` 的 target-specific 规则维护源。核心 envelope 和通用字段见 [context-pack-contract.md](context-pack-contract.md)。

## Current Role

`context pack` 已收缩为 memory / knowledge companion。`--for <target>` 仍然保留，但它只影响可选注入层的检索边界，不再要求生成 target-specific 的 execution、verify 或 review 派生块。

当前支持的 target：

- `ce-work`
- `aisee-verify`
- `ce-doc-review`
- `ce-code-review`

这些 target 的共同规则：

- 当前 change 仍是唯一入口。
- OpenSpec artifacts、`source-map.md`、`tasks.md` 和 evidence 仍按通用 contract 进入 `facts.parsed` / `facts.derived`。
- `--for` 不再要求 `facts.derived.execution`、`facts.derived.checks`、`facts.derived.review` 或其它 target-specific envelope。
- `--project-memory` 与 `--knowledge` 产生的附加字段必须保持独立，不混入 OpenSpec facts。
- `gaps` 继续表达 metadata scan 与 traceability 缺口，但不由 `context pack` 自己推导下一步执行路由。

## Target Hints

### `--for ce-work`

- 用于“实现时带项目记忆 / 团队知识”场景。
- 只负责返回当前 change 的基础 metadata scan，以及显式请求的 `project_memory` / `knowledge` 注入。
- 不负责生成 `allowed_paths`、`requires_ce_plan`、`reusable_workflow_candidates` 或 completion gate。

### `--for aisee-verify`

- 用于“验证时带项目记忆 / 团队知识”场景。
- 不负责生成 verify 专用 `checks`、`drift_candidates` 或 archive readiness judgment。
- verify 自身应直接读取当前 change artifacts、schema 和 evidence。

### `--for ce-doc-review` / `--for ce-code-review`

- 仅作为可选检索范围提示保留。
- 不负责生成 review 范围、审查建议或派生审查上下文。
