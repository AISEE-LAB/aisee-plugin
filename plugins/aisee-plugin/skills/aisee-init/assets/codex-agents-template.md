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
- 当前 schema 的 capabilities、artifact 列表、依赖顺序、requiredness / N/A 规则和模板说明。

不要把 `aisee-app-spec-driven` 当成隐藏基类。每个 change 都必须按当前 schema 的声明读取和生成 artifact：

- 只有 schema 声明 `source_map_traceability` 时才要求 `source-map.md`。
- 只有 artifact `requiredness=conditional` 且当前 change 标记 Required=yes 时才展开按需 artifact。
- `Required=no` 且写明 N/A 原因时，不要为了填模板而展开完整 artifact。
- 其它 schema 只读取它自己声明的 artifacts / apply tracks / archive tracks，不套用 app artifact 清单。

## 上下文加载顺序

开始实现、修复或审查 OpenSpec change 时按顺序读取：

1. `openspec/project.md`：项目上下文、技术栈、开发命令。
2. `openspec/changes/<feature>/.openspec.yaml` 和 `openspec/config.yaml`：确认当前 schema。
3. 当前 schema 要求的 artifacts，按 schema 的 `requires` 依赖顺序读取。
4. `aisee/memory/rules.md` 与 `aisee/memory/index.md`：先读规则和索引，再只加载相关记忆条目。
5. `aisee/docs/reflect/`：会话复盘和 memory 候选区；只有用户明确要求提升时，才按 `aisee/memory/rules.md` 写入 `aisee/memory/`。

若找不到对应 change，先说明 `[SPEC-GAP]`，不要直接实现新范围。

开始需求规划或 change 边界规划时，按需读取：

- `aisee/docs/requirements/`：SRS 与 FR 来源。
- `aisee/docs/ui-content/`：页面内容、元素、状态和交互来源。
- `aisee/docs/architecture/`：技术事实、架构决策、项目约束、共享前置和风险来源。
- `aisee/docs/change-plan/`：已生成的 change 边界规划结果。

这些规划文档用于生成或补齐 OpenSpec artifacts，不能替代 `openspec/changes/<feature>/`。

## 工作流状态机

```text
aisee:init
  └─ aisee-schema-pack          # 安装当前项目需要的 schema pack

aisee:srs
  ├─ aisee:ui-content           # 可选：页面、交互、多端内容规格
  ├─ aisee:architecture         # 可选：技术架构事实、决策、项目约束、共享前置
  └─ aisee:change-plan          # 规划 OpenSpec change 边界
       └─ /opsx:new <change> --schema <selected-schema>
            └─ aisee:change-author
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```

约束：

- 规划材料不足：先补 `aisee/docs/requirements/`、`aisee/docs/ui-content/` 或 `aisee/docs/architecture/`，不要直接进入实现。
- task 有误：暂停，更新 `tasks.md`，再继续。
- spec 有误：暂停，走 spec 修改流程，再继续。
- artifact 与实现事实冲突：暂停，更新对应 artifact；若当前 schema 生成 `source-map.md`，同步检查 traceability 与 artifact applicability。
- 不跳过状态机步骤。
- 不带已知错误继续实现。
- 每个 change 必须以 archive 闭环。

## 冲突标记

| 标记 | 含义 | 处理 |
|---|---|---|
| `[SPEC-CHANGE-REQUIRED]` | 建议与现有 spec 冲突 | 暂停，实现前走 spec 修改流程 |
| `[SPEC-GAP]` | spec 缺少必要决策 | 补齐 spec 后继续 |
| `[STACK-CONTEXT-MISSING]` | 缺少项目级技术栈来源 | 先更新 `openspec/project.md` 或补 architecture |
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

- 记忆规则：`aisee/memory/rules.md`
- 项目索引：`aisee/memory/index.md`

先读规则和索引，再只加载本任务相关条目。`aisee/memory/` 是长期项目记忆的权威位置；`aisee/docs/reflect/` 是会话复盘和待确认候选区，不能替代 `aisee/memory/`。

## 知识库

- `aisee/docs/requirements/`：`aisee:srs` 输出。
- `aisee/docs/ui-content/`：`aisee:ui-content` 输出，说明页面内容、元素、状态和交互，不含视觉设计规范。
- `aisee/docs/architecture/`：`aisee:architecture` 输出，说明技术事实、架构决策、项目约束、共享前置和风险；不能替代 `openspec/project.md` 的项目级技术栈事实。
- `aisee/docs/change-plan/`：`aisee:change-plan` 输出。
- `aisee/docs/reflect/`：会话反思、技能草案、memory 候选。

## Hook 配置

- Codex hooks：`.codex/hooks.json`
- Codex 配置：`.codex/config.toml`
- hook 脚本：`aisee/hooks/`

项目级 Codex hooks 首次运行前可能需要在 `/hooks` 中信任。

## 输出要求

- 所有回复使用中文。
- 总结包含：改动文件、验证命令、未完成事项或风险。
- 涉及 spec 的输出必须引用具体路径。
```
