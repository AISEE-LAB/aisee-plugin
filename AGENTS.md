# AGENTS.md

- 默认使用中文回复和编写文档，除非用户明确要求其他语言。
- 保持 Aisee、OpenSpec、Compound Engineering 的职责边界清晰。
- OpenSpec change 和 baseline 是规范事实源；不要创建平行规范事实源。
- Aisee CLI 的 JSON 输出应调用时解析 Markdown、OpenSpec artifacts、`aisee/registry/sources.json`、`aisee/registry/id-registry.json` 和 `source-map.md`。
- `aisee/cache/context-index.json` 只能作为可删除、可重建的缓存，不能作为事实源。
- `tasks.md` 是唯一长期任务清单；`ce-plan` 只能作为按需细化器，结论必须回写 `tasks.md` 或 `source-map.md`。
- 修改 skill 时保持 `SKILL.md` 精简，将长规则放入 `references/` 或 `docs/architecture/`。
- 不要把教程站内容放入本仓库。
