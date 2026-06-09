---
name: aisee:reflect
description: 复盘当前会话并把可复用经验沉淀为项目内可审查资产。用于会话结束复盘、总结“这次学到了什么”、提炼团队约定、发现可转成新 skill 的重复流程、审查现有 skill 的缺口、记录 workflow fix，或用户明确说 reflect、aisee:reflect、aisee-reflect、复盘、沉淀、保存经验、转成技能、优化技能、总结本次协作时触发。长会话中如果出现多轮纠错、重复工具链、稳定偏好或可复用流程，也应主动建议使用本技能。
---

# aisee:reflect

复盘当前会话，识别可复用经验，并把结论写成项目内可版本化、可审查的候选资产。

生成 reflect 文档时，frontmatter 字段合同统一遵循 `plugins/aisee-plugin/references/planning-doc-frontmatter.md`；这些文档只服务索引和候选沉淀，不提升为 OpenSpec 事实源。

`aisee:reflect` 默认只负责 **反思、归纳、候选沉淀**。`aisee/docs/reflect/` 是候选区，不是规范事实源；`aisee/memory/` 才是经用户确认后的长期项目记忆区。不要直接修改全局记忆、隐藏配置、OpenSpec baseline、active change artifacts 或其他技能目录，除非用户明确要求继续执行对应改动。

## 与 Compound 知识沉淀的边界

`aisee:reflect` 不替代 `ce-compound`、`ce-compound-refresh` 或 `docs/solutions/`：

- `ce-compound` 记录一个刚解决的具体工程问题、根因、解决方案和预防措施。
- `ce-compound-refresh` 维护 `docs/solutions/`，处理过期、重复、合并或删除。
- `aisee:reflect` 负责会话复盘、分类、memory 候选、workflow/skill 改进候选，以及跨项目复用候选判断。

如果复盘中发现“具体已解决工程问题”适合写 solution，不要在 reflect 中重复生成 solution 正文；输出 follow-up：`Suggested follow-up: run ce-compound for the concrete solution.`。Reflect 可以引用 `docs/solutions/...` 作为证据来源，但不能复制或改写同一内容。

## 输出位置

| 产物 | 路径 |
|---|---|
| 会话复盘与 memory 候选 | `aisee/docs/reflect/YYYY-MM-DD_<slug>.md` |
| 新技能草案 | `aisee/docs/reflect/skills/YYYY-MM-DD_<skill-name>.md` |
| 现有技能优化建议 | `aisee/docs/reflect/skill-patches/YYYY-MM-DD_<skill-name>.md` |
| 工作流修复建议 | `aisee/docs/reflect/workflow-fixes/YYYY-MM-DD_<slug>.md` |
| 可复用知识候选 | `aisee/docs/reflect/knowledge-candidates/YYYY-MM-DD_<slug>.md` |
| 已确认长期记忆 | `aisee/memory/arch/`、`aisee/memory/pref/`、`aisee/memory/ctx/`、`aisee/memory/stack/` |

文件名使用当天日期和短 kebab-case slug。默认使用用户语言；没有明确语言时使用中文。

## 工作模式

根据用户意图选择模式：

| 用户意图 | 行为 |
|---|---|
| 只说“reflect / 复盘 / 总结这次” | 先输出复盘报告，不写文件，等待用户确认 |
| 明确说“保存 / 写入 / 生成文档 / 全部落盘” | 输出报告后直接写入对应文件 |
| 明确说“写入 memory / 提升到记忆 / 更新 aisee/memory” | 按 `aisee/memory/rules.md` 分类写入项目记忆，并更新 `aisee/memory/index.md` |
| 明确要求“转成 skill / 优化某技能” | 生成技能草案或技能补丁，不把草案直接提升为活动技能 |
| 明确要求“跨项目复用 / 以后其他项目也用 / 避免重复犯错” | 生成 reusable knowledge candidate，不写全局知识库 |
| 会话很短或缺少可沉淀信息 | 说明发现有限，只列出有信号的事项 |

如果用户要求修改真实技能目录，应结合 `skill-creator` 工作流；本技能生成的草案默认只是审查材料。

## 边界

必须遵守：

- `aisee/docs/reflect/` 只存复盘记录、候选规则、技能草案、补丁建议和 workflow fix。
- `aisee/memory/` 只有在用户明确要求“写入 memory / 提升到记忆 / 更新 aisee/memory”时才写。
- 写入 `aisee/memory/` 前必须读取 `aisee/memory/rules.md` 和 `aisee/memory/index.md`；不存在时建议运行 `aisee:init`，不要临时发明结构。
- 不写全局 memory、用户主目录 memory 或代理私有 memory，除非用户明确要求并确认影响。
- 不把 reflect 文档当作 OpenSpec change、baseline spec、SRS、UI Content、Architecture、tasks 或 source-map 的替代品。
- 不把 reflect 文档当作 `docs/solutions/` 的替代品；具体问题解决方案应交给 `ce-compound`。
- 不把一次性偶然事件写成长期规则；优先沉淀未来再次发生时会节省时间或降低风险的内容。
- 不写入 secrets、token、cookie、私密身份信息或生产凭据。

## Phase 0 — 读取项目上下文

先通读当前会话，并优先检查项目内已有规则，避免重复沉淀。扫描文件时必须遵守 `.gitignore`；优先使用 `rg --files`，不要用全仓库裸 `find` 把依赖、构建产物、缓存或生成文件当作项目事实。

```bash
rg --files \
  -g 'AGENTS.md' \
  -g 'README.md' \
  -g 'aisee/memory/*.md' \
  -g 'aisee/memory/**/*.md' \
  | sort

rg --files aisee/docs/reflect 2>/dev/null | sort | tail -20
```

如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物和缓存目录，并只查本技能需要的文件类型。

如果 `AGENTS.md` 不存在，`CLAUDE.md` 只能作为 legacy fallback；不要主动把 `CLAUDE.md` 当作新项目主规则入口。

## Workflow

先按 Phase 0 读取上下文，再按需读取 references。保持渐进加载：简单口头复盘只读主流程；需要落盘或跨项目复用时才读模板或知识候选规则。

Reference loading：

- 需要分类判断或生成复盘报告时读取 `references/workflow.md`。
- 需要写文件、提升 memory、生成技能草案、技能补丁或 workflow fix 时读取 `references/output-templates.md`。
- 用户要求跨项目复用、避免重复犯错，或出现 `docs/solutions/` / `ce-compound` 边界判断时读取 `references/knowledge-candidates.md`。
- 只做一句话口头总结时不必读取完整 workflow。
- 如果用户要求修改真实 skill，先读取目标 skill，再按 `skill-creator` 执行；不要只依赖 reflect 补丁建议。

## Guardrails

- 复盘结论必须能对应到本次会话中的行为、纠错、明确偏好或已确认项目事实。
- 输出要少而精；没有发现的类别不要输出。
- 每条候选规则都写成可执行规则，不写泛泛观察。
- 技能草案必须包含触发描述、工作流、输出格式和边界；不要直接写入活动 skill 目录。
- 技能补丁必须给出可复制的 `After` 文本，不只写泛泛建议。
- 工作流修复必须说明适用范围：全局或本项目。
- 写入任何 `aisee/docs/reflect/` 产物后，只建议是否在项目规则中增加 reflect 索引；不要擅自修改 `AGENTS.md`。
- 最终回复列出写入或修改的文件、每类产物数量、是否更新索引，以及未执行验证或剩余风险。
