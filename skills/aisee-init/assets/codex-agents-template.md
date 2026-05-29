# AGENTS.md 模板

用于 INIT。替换 `{placeholder}` 后写入项目根目录 `AGENTS.md`。
本模板承载 Codex 项目规则、OpenSpec 工作流、冲突标记和执行约束。

```markdown
# AGENTS.md

> 最后更新：{date}
> 项目上下文：见 `openspec/project.md`

## 指令加载

Codex 会在开始工作前读取 `AGENTS.md`。若存在多层 `AGENTS.md`，更靠近当前目录的文件优先生效；用户当前消息和系统消息优先级更高。

## 单一事实来源

本项目以 `openspec/` 为唯一真实规范。
`openspec/changes/<feature>/` 下的 artifacts 具有规范效力。
对话历史、PR 评论、IM 讨论和个人笔记只能作为参考，不能覆盖 spec。

Artifact 由当前 change 使用的 schema 决定。开始处理 change 前必须先读取：

- `openspec/changes/<feature>/.openspec.yaml`：确认 schema 名称；缺失时按项目默认 schema 或 OpenSpec 默认规则处理。
- `openspec/config.yaml`：确认项目默认 schema 和 OpenSpec 配置。
- 当前 schema 的 artifact 列表、依赖顺序和模板说明。

默认推荐 schema 是 `aisee-app-spec-driven`。当 change 使用 `aisee-app-spec-driven` 时，常见 artifacts 为：

- `proposal.md`
- `source-map.md`
- `specs/`
- `design.md`
- `ui-contract.md`
- `data-model.md`
- `service-contract.md`
- `tasks.md`

如果 change 使用其他 schema，必须按该 schema 的 artifact 定义读取和生成文件，不要套用 `aisee-app-spec-driven` 的 artifact 清单。

## 上下文加载顺序

开始实现、修复或审查 OpenSpec change 时按顺序读取：

1. `openspec/project.md`：项目上下文、技术栈、开发命令。
2. `openspec/changes/<feature>/.openspec.yaml` 和 `openspec/config.yaml`：确认当前 schema。
3. 当前 schema 要求的 artifacts，按 schema 的 `requires` 依赖顺序读取。
4. `.memory/rules.md` 与 `.memory/index.md`：先读规则和索引，再只加载相关记忆条目。
5. `docs/reflect/`：会话复盘和 memory 候选区；只有用户明确要求提升时，才按 `.memory/rules.md` 写入 `.memory/`。

若找不到对应 change，先说明 `[SPEC-GAP]`，不要直接实现新范围。

开始需求规划或 change 边界规划时，按需读取：

- `docs/requirements/`：SRS 与 FR 来源。
- `docs/ui-content/`：页面内容、元素、状态和交互来源。
- `docs/tech-context/`：技术事实、项目约束、共享前置和风险来源。
- `docs/change-plan/`：已生成的 change 边界规划结果。

这些规划文档用于生成或补齐 OpenSpec artifacts，不能替代 `openspec/changes/<feature>/`。

## 工作流状态机

```text
aisee:init
  └─ aisee-schema-pack          # 安装 aisee-app-spec-driven

aisee:srs
  ├─ aisee:ui-content           # 可选：页面、交互、多端内容规格
  ├─ aisee:tech-context         # 可选：技术事实、项目约束、共享前置
  └─ aisee:change-plan          # 规划 OpenSpec change 边界
       └─ /opsx:new <change> --schema aisee-app-spec-driven
            └─ /opsx:continue   # 按 schema 依赖顺序生成 artifacts
            └─ /opsx:apply
            └─ /opsx:verify
            └─ /opsx:archive
```

约束：

- 规划材料不足：先补 `docs/requirements/`、`docs/ui-content/` 或 `docs/tech-context/`，不要直接进入实现。
- task 有误：暂停，更新 `tasks.md`，再继续。
- spec 有误：暂停，走 spec 修改流程，再继续。
- artifact 与实现事实冲突：暂停，更新对应 artifact；若使用 `aisee-app-spec-driven`，同步检查 `source-map.md`。
- 不跳过状态机步骤。
- 不带已知错误继续实现。
- 每个 change 必须以 archive 闭环。

## 冲突标记

| 标记 | 含义 | 处理 |
|---|---|---|
| `[SPEC-CHANGE-REQUIRED]` | 建议与现有 spec 冲突 | 暂停，实现前走 spec 修改流程 |
| `[SPEC-GAP]` | spec 缺少必要决策 | 补齐 spec 后继续 |
| `[STACK-CONTEXT-MISSING]` | 缺少项目级技术栈来源 | 先更新 `openspec/project.md` 或补 tech-context |
| `[STACK-DECISION-REQUIRED]` | 需要正式技术决策 | 暂停具体设计 |
| `[STACK-CONFLICT]` | 需求或输入与项目技术事实冲突 | 等待确认 |
| `[RISK]` | 识别到实现风险 | 在 `tasks.md` 增加缓解措施 |

## Codex 执行约束

- 默认先读后写，修改前读取目标文件。
- 使用最小必要工具集；可并行读取时合并并行读取。
- 不回滚用户已有改动，除非用户明确要求。
- 不在项目外修改系统状态，除非用户明确要求。
- 不安装全局依赖，除非用户明确要求。
- 修改后运行与变更相关的最小验证命令。
- 若涉及 OpenAI / Codex / 第三方库配置，先查当前官方文档或项目内文档。

## 沙箱和网络

- 遵守当前 Codex sandbox、approval policy 和网络策略。
- 网络仅用于任务必要的依赖安装、官方文档核对或 spec 明确允许的 API。
- 高风险命令必须先解释影响，再请求确认。

## 项目记忆

- 记忆规则：`.memory/rules.md`
- 项目索引：`.memory/index.md`

先读规则和索引，再只加载本任务相关条目。`.memory/` 是长期项目记忆的权威位置；`docs/reflect/` 是会话复盘和待确认候选区，不能替代 `.memory/`。

## 知识库

- `docs/requirements/`：`aisee:srs` 输出。
- `docs/ui-content/`：`aisee:ui-content` 输出，说明页面内容、元素、状态和交互，不含视觉设计规范。
- `docs/tech-context/`：`aisee:tech-context` 输出，说明技术事实、项目约束、共享前置和风险；不能替代 `openspec/project.md`。
- `docs/change-plan/`：`aisee:change-plan` 输出。
- `docs/reflect/`：会话反思、技能草案、memory 候选。

## Hook 配置

- Codex hooks：`.codex/hooks.json`
- Codex 配置：`.codex/config.toml`
- hook 脚本：`.aisee/hooks/`

项目级 Codex hooks 首次运行前可能需要在 `/hooks` 中信任。

## 输出要求

- 所有回复使用中文。
- 总结包含：改动文件、验证命令、未完成事项或风险。
- 涉及 spec 的输出必须引用具体路径。
```
