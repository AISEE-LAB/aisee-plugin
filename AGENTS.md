# Agent Instructions for Aisee Plugin

## 项目目的

Aisee Plugin 是一个面向 Codex 的 OpenSpec 工作流层，用于支持 spec-driven AI software engineering。

## 工程原则

- 默认使用中文回复和编写文档，除非用户明确要求其他语言。
- 保持 Aisee、OpenSpec、Compound Engineering 的职责边界清晰。
- 保持 CLI 公共命令行为稳定；除非用户明确要求，否则不要引入破坏性变更。
- 优先做小而可审查的改动；行为变化要同步更新测试和用户可见文档。
- 不要移除 OpenSpec、Codex、schema pack、context pack、verification 或 archive 相关能力，除非有明确替代方案。
- 修改 skill 时保持 `SKILL.md` 精简，将长规则放入 `references/` 或 `docs/architecture/`。
- 不要把教程站内容放入本仓库。

## 事实源边界

- OpenSpec change 和 baseline 是规范事实源；不要创建平行规范事实源。
- Aisee CLI 的 JSON 输出应调用时解析 Markdown、OpenSpec artifacts、`source-map.md`、`tasks.md`、evidence 和少量 planning doc metadata。
- 不要把编号、索引或缓存升级成独立规范事实源；context pack 的内部扫描视图只服务本次输出。
- `tasks.md` 是唯一长期任务清单；`ce-plan` 只能作为按需细化器，结论必须回写 `tasks.md` 或 `source-map.md`。

## Review 指引

- 将 CLI 行为损坏、schema 处理失效、不安全文件写入和误导性文档视为高优先级问题。
- 检查生成路径是否安全，避免覆盖当前项目之外的文件或无关目录。
- 检查 JSON / YAML 输出是否仍保持机器可读、字段稳定且示例可复现。
- 检查 README、示例和命令说明是否与当前实现一致。
- 检查示例是否能从干净仓库 checkout 后复现，尤其是 OpenSpec、Codex 和 archive 相关流程。
