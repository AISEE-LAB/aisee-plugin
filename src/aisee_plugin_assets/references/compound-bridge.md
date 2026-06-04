# Compound Engineering Bridge

Aisee 与 Compound Engineering 的衔接规则：

- `ce-doc-review`：审核 SRS、design、contracts、tasks、source-map。
- `ce-plan`：仅在 `tasks.md` 或 `source-map.md` 不足时按需细化，结论必须回写 OpenSpec change。
- `ce-work`：按单个 OpenSpec change 工程包执行实现。
- `ce-debug`：处理失败、异常和阻塞。
- `ce-code-review` / `ce-test-*`：实现后审核和专项验证。
- `ce-commit` / `ce-commit-push-pr`：交付和 PR handoff。

OpenSpec change 是长期事实源。Compound 输出需要长期保留时，应回写 owner 文档或记录到 review/verification 产物。
