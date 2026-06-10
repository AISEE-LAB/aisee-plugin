# Aisee Layout Migration

本文是 `aisee:init` 目录布局和旧路径迁移规则的维护源。

## Canonical Layout

新项目只创建和写入 `aisee/` 布局：

```text
aisee/
  registry/
  cache/
  docs/
  memory/
  hooks/
  config/
```

## Legacy Fallback

旧项目兼容路径只允许读取 fallback：

- `.memory/rules.md`
- `.memory/index.md`
- `docs/requirements/`
- `docs/ui-content/`
- `docs/architecture/`
- `docs/change-plan/`
- `docs/reflect/`

## Default Policy

- `aisee:init` 审计时只报告迁移建议，不自动移动、删除或合并旧文件。
- `aisee doctor` 只检查并报告 legacy-only / dual-path 风险。
- `aisee bootstrap --plan` 只输出迁移计划。
- `bootstrap --apply` 当前不执行迁移。
- 如果新旧路径都存在，以 `aisee/` 为准，旧路径只能提示“可能过期”。

## Assisted Migration

用户明确要求执行迁移时，按交互式人工协助处理：

1. 列出源路径、目标路径、冲突情况和将要进行的文件操作。
2. 等待用户确认。
3. 只迁移 Aisee 产物；不移动 OpenSpec baseline/change，不修改业务代码。
4. 迁移后运行 `aisee doctor --json`。
5. 按影响范围运行最小测试或检查。

## File Rules

- legacy-only 可移动到对应 canonical 路径。
- 目录迁移只搬文件，保持相对结构，不搬空目录。
- dual-path 必须先比较内容；不自动合并、不覆盖 canonical，不删除旧路径，除非用户确认处理方式。
- hooks 不搬旧文件，改为重新运行 hook 安装。
- memory 可从 `.memory/*` 迁移到 `aisee/memory/*`；若新 memory 已存在，先比较再确认。
