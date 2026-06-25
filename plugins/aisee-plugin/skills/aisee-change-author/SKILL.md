---
name: aisee:change-author
description: 按当前 schema 的模板，为单个已确认 OpenSpec change 详细生成或补全文档。用于任何 schema 下的 schema-aware authoring：逐文档写清目标、范围、行为、约束、风险、验证和实施顺序，减少开发、评审和验证阶段的误解与漏项。不拆 change 边界、不重新选择 schema、不写代码；只处理 schema 声明的文档并保持跨文档一致。
---

# aisee:change-author

`aisee:change-author` 是单个 OpenSpec change 的详细文档 author。它读取当前 change 绑定的 schema、模板和已有文档，把该 schema 声明的各个文档写得更清晰、更完整、更不容易让后续开发出错。

它不是流程裁决器，也不是代码执行器。它的价值在于：**按当前 schema 逐文档补齐高质量内容，并保持文档之间一致。**

## 职责边界

负责：

- 只处理一个已确认边界和 schema 的 OpenSpec change。
- 读取当前 schema 的 `schema.yaml`、`instruction`、`template`、当前 change 目录和直接相关上游输入。
- 按 schema `artifacts[].requires` 的顺序生成或补齐文档。
- 先保留当前 schema 模板的章节和结构，再在模板基础上补强必要内容。
- 让每个文档都达到可执行、可审查、少歧义的粒度，而不是只填模板骨架。
- 在文档之间保持范围、术语、行为、约束、风险、验证方式和任务顺序一致。
- 对缺失前提、信息冲突、模板不足或边界不清的地方显式标 gap / blocker，而不是靠实现阶段临时猜。
- 已有文档存在时增量补齐，不覆盖用户已写内容。

不负责：

- 拆 change 边界、重新选择 schema、升级 schema 或一次处理多个 changes。
- 为 schema 未声明的文档创建文件。
- 写代码、生成实现代码、替代 review / test / archive。
- 把 planning docs、聊天记录或外部资料原样复制成 change 文档。
- 发明不在当前 change 和当前 schema 中的长期事实源。

## 输入门禁

开始 author 前必须确认：

- 当前只处理一个 OpenSpec change。
- change 已由 `aisee:change-plan` 或用户明确确认边界、schema 和依赖。
- 能读取 `openspec/changes/<change>/`，或用户明确要求只输出草稿 / patch。
- 能读取当前 schema 的 `schema.yaml` 和相关模板。
- 当前 change metadata 已声明 schema，且项目内已安装该 schema。
- 已收集与当前 change 直接相关的上游输入，例如 Change Plan、Issue、用户输入、SRS、baseline migration 结论或其它直接材料。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。

如果 schema metadata 缺失、schema 未安装、模板缺失或当前 change 边界仍不清楚，输出 `[CHANGE-AUTHOR-BLOCKED]` 并列出缺口，不继续写文档。

## CHECKPOINT

写入或修改任何 artifact 前，必须先给出以下摘要并等待用户确认：

- 当前 change
- 当前 schema
- schema 声明的文档顺序
- 计划生成 / 更新哪些文件
- 既有文档的合并策略
- 已发现的 blocker / gap / 风险

未确认时，只能输出 author 草稿、patch 预览或缺口报告，不直接写入 change 目录。

## 读取顺序

1. 读取当前 schema 的 `schema.yaml`，确认 artifact DAG、模板位置和缺失项。
2. 逐个读取本次会写到的 artifact 的 `instruction` 和 `template`。
3. 读取当前 change 已有文档，理解用户已写内容和未完成部分。
4. 读取与当前 change 直接相关的上游输入。
5. 按 schema 声明顺序对每个文档执行 `template pass -> strengthening pass -> local check`。
6. 完成后做一次一致性复检，确认文档之间没有明显冲突或漏项。

详细写法、逐文档边界、一致性检查、N/A 处理和编号规则见：

```text
references/authoring-rules.md
```

## Author 子阶段

```text
schema preflight
  -> change / schema / template / existing-doc check

document inventory
  -> 确认本次要写哪些 schema 文档

detail pass
  -> 逐文档先落模板骨架，再补齐目标、范围、行为、约束、风险、验证、实施顺序

local check
  -> 检查当前文档是否既遵循模板，又补足了后续实现最容易出错的信息

consistency pass
  -> 对齐术语、边界、前置假设、N/A、验证口径

final check
  -> schema / template / cross-doc consistency recheck
```

## 核心规则

- 任何 schema 一视同仁；不要只偏向 `spec-driven`、app schema 或轻量 schema。
- 以当前 schema 的 `artifacts[].requires` 为唯一生成顺序来源。
- 生成每个文档前，先读它自己的 `instruction` 和 `template`。
- 先遵循模板已有结构、章节名和顺序；除非模板或用户明确允许，不要擅自重排文档结构。
- 不要因为某个文档常见就创建 schema 未声明的文件。
- 不要只填模板标题；要在模板骨架基础上把每个文档展开到足以指导后续开发、评审和验证的粒度。
- 文档要各司其职：需求写需求、设计写约束、任务写实施与验证，不要互相替代。
- `tasks.md` 或其它 apply-track 文档必须在前置事实文档之后收口，不要抢先承载需求和设计。
- 上游输入不足时，标 gap / blocker；不要伪造确定性结论。
- 如果 schema 仍声明 `source-map.md`，把它当成普通 schema 文档按模板补齐，不把它当成当前工作流中心，也不要让其他文档依赖它的存在。
- 发现 schema DAG 循环、模板缺失、requires 指向不存在 artifact 时，停止并输出 `[SCHEMA-INVALID]`。

## 逐文档执行法

对每个要写的文档，固定执行这三步：

1. `template pass`
   - 按当前 schema 模板建立章节和基础字段。
   - 不擅自删改模板的结构意图。
2. `strengthening pass`
   - 补写该文档最容易遗漏但会影响实现、评审或验证的关键信息。
   - 至少补强：边界、例外、风险、验证或实施衔接中的相关项。
3. `local check`
   - 检查当前文档是否既遵循模板，又没有停留在空骨架层面。
   - 检查本文件中的术语、范围、N/A 和占位写法是否自洽。

## 写入与输出

如果用户要求直接写文件：

- 只写当前 change 目录内 schema 声明的文档。
- 已存在文档时先读取并增量补齐。
- 不删除用户已有内容，除非它与 schema 或当前 change 边界明确冲突且用户确认。

输出摘要必须包含：

- 生成 / 更新了哪些文档。
- 当前是依据哪些 schema 模板进行补写。
- 每个文档本次补强了什么。
- 哪些文档是 N/A 及原因。
- 还存在哪些 blocker / gap / 临时占位。
- 建议下一步：`openspec validate`，然后进入 implementation / review / test。
