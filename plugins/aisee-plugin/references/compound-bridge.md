# Compound Engineering Bridge

Aisee 与 Compound Engineering 的衔接规则：

- `ce-doc-review`：审核 SRS、design、contracts、tasks、source-map。
- `ce-plan`：仅在 `tasks.md` 或 `source-map.md` 不足时按需细化，结论必须回写 OpenSpec change。
- `ce-work`：按单个 OpenSpec change 工程包执行实现。
- `ce-debug`：处理失败、异常和阻塞。
- `ce-code-review` / `ce-test-*`：实现后审核和专项验证。
- `ce-commit` / `ce-commit-push-pr`：交付和 PR handoff。

OpenSpec change 是长期事实源。Compound 输出需要长期保留时，应回写 owner 文档或记录到 review/verification 产物。

## 复用优先

创建任务或执行任务前，先检查当前项目已有工作流和 skill：

- 无明确 change 时，先走 `aisee:flow` 判断下一步，而不是直接创建任务或执行。
- 有单个 authored change 时，先读取 `aisee context pack --change <change> --for ce-work --json`。
- `context pack` 中 `requires_ce_plan=true` 时，才按需使用 `ce-plan` 细化执行顺序；结论必须回写当前 schema apply tracks，只有 source-map schema 才回写 `source-map.md`。
- `requires_ce_plan=false` 且实现路径清楚时，优先 `aisee:implementation-bridge -> ce-work`。
- Verify/archive 阶段只消费 CE review/test/debug evidence，不新增替代 CE 的执行、代码审查或测试 agent。

如需 Aisee 专职 reviewer，只使用 `aisee-change-architect`、`aisee-spec-reviewer`、`aisee-implementation-reviewer` 这类只读一致性审查角色。接口、UI、硬件、固件、安全和验证差异作为 schema-aware check lenses，不单独创建全能审查 agent。
