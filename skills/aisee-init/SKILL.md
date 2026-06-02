---
name: aisee:init
description: 初始化、审计并优化 OpenSpec 项目的 Codex 配置体系。用于创建或修复 AGENTS.md、openspec/project.md、aisee/memory/ 和 Codex hooks；检查 hook 机制兼容性、OpenSpec 状态机、规划目录与项目技术架构边界。触发词包括 aisee:init、aisee-init、初始化项目配置、优化 AGENTS.md、配置 Codex hooks、OpenSpec 配置审计。
---

# aisee:init

对外 skill 名称是 `aisee:init`；目录名保持 `aisee-init/`，脚本路径仍使用 `aisee-init/scripts/...`。

## 目标

把一个项目整理成 OpenSpec 驱动的 Codex 配置：

- `AGENTS.md`：Codex 项目规则、OpenSpec 工作流、工具调用约束、沙箱和验证要求。
- `openspec/project.md`：项目事实、技术栈、架构、开发命令；不放 AI 行为规则。
- `aisee/docs/requirements/`、`aisee/docs/ui-content/`、`aisee/docs/architecture/`、`aisee/docs/change-plan/`：Aisee 规划链路产物目录。
- `aisee/memory/rules.md` 与 `aisee/memory/index.md`：项目本地记忆规则和记忆入口。
- `aisee/docs/reflect/`：会话复盘和 memory 候选区；不替代 `aisee/memory/`。
- `.codex/hooks.json` 与 `.codex/config.toml`：项目级 Codex hook 配置。
- `aisee/hooks/`：本技能安装到目标项目的 hook 脚本目录，Codex 从这里执行脚本。

## 先决条件

执行任何初始化、审计或优化前，先确认项目已由 OpenSpec 初始化：

```bash
node -e "const fs=require('fs'); for (const [p,t] of [['openspec/config.yaml','file'],['openspec/changes','dir'],['openspec/changes/archive','dir']]) { try { const s=fs.statSync(p); console.log(p + ':' + ((t==='dir'?s.isDirectory():s.isFile())?'ok':'bad')); } catch { console.log(p + ':missing'); } }"
node -e "const {execSync}=require('child_process'); try { execSync('openspec --version',{stdio:'ignore'}); console.log('openspec:ok'); } catch { console.log('openspec:missing'); }"
```

如果缺少 `openspec/config.yaml` 或 `openspec/changes/`，停止并让用户先运行：

```bash
openspec init
```

不要手动替代 `openspec init` 创建目录。

## 模式选择

- **INIT**：从模板生成配置文件和 hooks。
- **AUDIT**：读取现有配置，报告缺失、重复、职责漂移和冲突。
- **OPTIMIZE**：在用户确认后最小化修改现有配置。

若用户只说“检查并改进这个技能”，审计技能自身：检查 frontmatter、模板引用、hook 协议、过时命名、可验证性和 Codex 兼容性。

## INIT 流程

1. 收集缺失信息：项目类型、技术栈、团队规模、使用的代理、当前痛点。
2. 用 `assets/codex-agents-template.md` 生成 `AGENTS.md`。
3. 用 `assets/openspec-project-template.md` 生成 `openspec/project.md`。
4. 若 `aisee/memory/rules.md` 不存在，用 `assets/memory-rules-template.md` 写入项目本地记忆规则。
5. 若 `aisee/memory/index.md` 不存在，用 `assets/memory-index-template.md` 初始化 `aisee/memory/arch`、`aisee/memory/pref`、`aisee/memory/ctx`、`aisee/memory/stack`。
6. 运行 `scripts/setup-hooks.js --codex` 安装 hooks。

## 目录布局与迁移

新项目只创建和写入 `aisee/` 布局；旧 `.aisee/`、`.memory/` 和历史 `docs/*` 产物目录只允许作为 fallback 读取。

迁移默认只提示，不自动执行。只有用户明确要求迁移时，才按 [layout-migration.md](references/layout-migration.md) 执行交互式人工协助迁移。

关键约束：

- 执行前列出源路径、目标路径、冲突情况和文件操作，等待用户确认。
- 只迁移 Aisee 产物；不移动 OpenSpec baseline/change，不修改业务代码。
- 新旧同时存在时，不自动合并、不覆盖 canonical、不删除旧路径。
- cache 不迁移；hooks 通过重新安装修复；registry 和 memory 合并必须单独确认策略。

模板填充规则：

- 输出内容使用中文。
- 不留下 `{placeholder}`。
- `AGENTS.md` 必须承载完整 OpenSpec 工作流、冲突标记和 Codex 执行约束。
- 项目级技术栈只放 `openspec/project.md`；未确认项写“未确认”，不要在 `AGENTS.md` 里补技术选型。
- Hook 命令只引用项目内 `aisee/hooks/`，不要引用技能安装路径。
- 记忆规则使用项目本地 `aisee/memory/rules.md`，不再引用或写入任何全局 memory rules 文件。
- `aisee/memory/` 是长期项目记忆的权威位置；`aisee/docs/reflect/` 只作为复盘、草案和待确认候选区。
- OpenSpec custom schemas 由 `aisee-schema-pack` 负责；本技能不安装或维护 schema pack。

## Hook 安装

运行方式：

```bash
node aisee-init/scripts/setup-hooks.js --codex
node aisee-init/scripts/setup-hooks.js
```

默认自动检测：存在 `AGENTS.md` 或 `.codex/` 则安装 Codex hooks。无法检测时传入 `--codex`。

安装结果：

| 目标 | 写入文件 |
|---|---|
| 共享脚本 | `aisee/hooks/session-inject.js`、`aisee/hooks/spec-drift.js`、`aisee/hooks/prompt-scan.js` |
| Codex | `.codex/hooks.json`、`.codex/config.toml` |

Hook 职责：

- `SessionStart` → `session-inject.js`：注入 OpenSpec、活跃 change 和 memory 入口摘要。
- `UserPromptSubmit` → `spec-drift.js`：发现疑似越过当前 spec 的需求，注入自检上下文。
- `UserPromptSubmit` / `PreToolUse` → `prompt-scan.js`：发现明显密钥并阻断。

兼容性要求：

- Codex 使用 `[features].hooks = true`；`codex_hooks` 只作为旧别名，不再生成。
- Codex 项目级 hooks 写入 `<repo>/.codex/hooks.json`，并需要用户在 `/hooks` 中信任。
- Hook 脚本必须从 stdin 读取 JSON，并按 `hook_event_name` 返回对应 JSON。
- `UserPromptSubmit` 阻断使用顶层 `decision: "block"`。
- `PreToolUse` 阻断使用 `hookSpecificOutput.permissionDecision: "deny"`，并保留旧式 `decision: "block"` 兼容。
- 注入上下文使用 `hookSpecificOutput.additionalContext`，不要依赖普通 stdout。

## AUDIT 清单

### `AGENTS.md`

- 是否说明 Codex 会读取 `AGENTS.md`，且直接用户指令优先。
- 是否指向 `openspec/project.md`。
- 是否声明 OpenSpec 是唯一规范来源。
- 是否要求实现、修复或审查 OpenSpec change 前先读取 `.openspec.yaml` / `openspec/config.yaml` 判断 schema，再按 schema 的 artifact 依赖顺序读取文件。
- 是否定义 `[SPEC-CHANGE-REQUIRED]`、`[SPEC-GAP]`、`[RISK]`。
- 是否包含完整状态机：`aisee:srs → aisee:ui-content / aisee:architecture → aisee:change-plan → /opsx:new --schema <schema> → aisee:change-author → openspec validate → aisee:implementation-bridge → CE work/review/test → aisee:verify → aisee:archive-guard → openspec archive`。
- 是否包含 Codex 专属工具、沙箱、验证和输出约束。
- 是否包含技术栈，若有标记 `[VIOLATION]`。

### `openspec/project.md`

- 是否包含项目概览、技术栈状态、模块、开发命令、测试命令。
- 技术栈未确认时是否明确写“未确认”，而不是留空或由 AI 猜测。
- 环境设置命令是否可直接执行。
- 是否含 AI 行为规则，若有标记 `[VIOLATION]`。

### aisee 规划产物

- 是否说明 `aisee/docs/requirements/`、`aisee/docs/ui-content/`、`aisee/docs/architecture/`、`aisee/docs/change-plan/` 的职责。
- 若已有规划产物，hook 或配置是否能提示这些目录，但不把它们提升为 OpenSpec artifacts 的替代品。
- 是否明确 `aisee/docs/architecture/` 提供技术架构事实、决策和约束，不能替代 `openspec/project.md` 的项目级技术栈来源。
- 若存在旧路径 `.aisee/`、`.memory/` 或 `docs/requirements/` 等历史目录，标记 `[MIGRATION]`，说明只兼容读取，不自动迁移。
- 若新旧路径同时存在，标记 `[CONFLICT]`，说明 `aisee/` 为准，旧路径可能过期。
- 若用户要求执行迁移，先读取 [layout-migration.md](references/layout-migration.md)。

### Hooks

- `aisee/hooks/*.js` 是否存在且 Node 语法通过。
- Codex 配置是否包含 `SessionStart`、`UserPromptSubmit`、`PreToolUse`。
- `.codex/config.toml` 是否使用 `[features].hooks = true`。
- hook 命令是否从 git root 或绝对项目路径定位脚本，而不是技能安装路径。
- 若项目仍引用全局 memory rules 路径，标记 `[VIOLATION]`，改为项目本地 `aisee/memory/rules.md`。
- 若用户要安装、创建或审计 OpenSpec custom schemas，转交 `aisee-schema-pack`。

## OPTIMIZE 规则

- 先输出问题和最小修改计划，再改文件。
- 只修与配置职责、过时命名、hook 兼容、模板一致性相关的问题。
- 不重写无关内容，不美化相邻段落。
- 对现有用户配置使用合并；不要覆盖未知 hooks。
- 删除由本技能产生的重复 hook 条目。

## 输出格式

审计报告用中文：

```markdown
# OpenSpec 配置审计报告

## 结论

## 问题

### [MISSING]
### [VIOLATION]
### [DUPLICATION]
### [CONFLICT]

## 修复建议

## 已验证
```

实施完成后列出：修改文件、验证命令、剩余风险。
