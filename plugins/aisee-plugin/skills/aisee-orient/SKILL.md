---
name: aisee:orient
description: Aisee 默认入口定位 skill。用于进入任意项目后不确定该从哪个 Aisee skill、OpenSpec workflow 或 CLI 命令开始；根据项目状态、OpenSpec/Aisee 配置、baseline specs、active changes、规划文档和用户意图，输出下一步路由建议。触发词包括 aisee:orient、aisee orient、从哪开始、下一步用哪个 skill、判断项目状态、路由到 Aisee workflow。
---

# aisee:orient

`aisee:orient` 是 Aisee 工作流入口定位器。它回答“我现在该用哪个 Aisee skill / workflow 继续？”，不生产具体业务产物。

## 职责

- 读取项目接入状态：OpenSpec、Aisee 配置、baseline specs、active changes、planning docs、memory/knowledge 入口。
- 结合用户当前意图判断阶段：接入、迁移、需求澄清、架构/UI 补齐、change authoring、实现交接、验证、归档、记忆/知识维护。
- 推荐首选下一步 skill、CLI 命令或 workflow，并说明证据和原因。
- 标注阻塞项、风险、可选路径和需要用户确认的问题。
- 在证据不足时输出定位报告，不猜测业务事实。

## 不负责

- 不写 SRS、UI Content、Architecture、Design Spec 或迁移文档。
- 不写 `openspec/specs/` baseline，也不写 `openspec/changes/` artifacts。
- 不实现代码、不执行 review/test、不 archive。
- 不安装 schema pack、不维护 hooks、不替代 `aisee:init`。
- 不把 `aisee/docs/`、memory、knowledge 或 CLI JSON 输出当作 OpenSpec 事实源。

## 快速扫描

优先用轻量命令判断状态；不要全仓库裸扫描依赖、构建产物或缓存，也不要为了路由深读大量文档。`aisee:orient` 默认只看状态、目录、文件名和少量机器摘要。

```bash
node -e "const fs=require('fs'); for (const [p,t] of [['openspec/config.yaml','file'],['openspec/specs','dir'],['openspec/changes','dir'],['AGENTS.md','file'],['openspec/project.md','file'],['aisee/docs','dir'],['aisee/memory/index.md','file'],['.codex/hooks.json','file']]) { try { const s=fs.statSync(p); console.log(p + ':' + ((t==='dir'?s.isDirectory():s.isFile())?'ok':'bad')); } catch { console.log(p + ':missing'); } }"
node -e "const {execSync}=require('child_process'); for (const cmd of ['aisee doctor --json','aisee bootstrap --plan --json']) { try { console.log(cmd + ':ok'); execSync(cmd,{stdio:'ignore'}); } catch { console.log(cmd + ':unavailable-or-blocked'); } }"
rg --files openspec aisee/docs 2>/dev/null | head -80
```

如果 `aisee doctor --json` 可用，优先解析其 JSON；不可用时退回文件状态检查。若用户只问概念或路由，不需要运行破坏性或写入命令。

文档读取约束：

- 默认不打开 `docs/**`、`aisee/docs/**`、`openspec/specs/**` 或 `openspec/changes/**` 的正文。
- 只有文件名无法判断路由，或用户明确要求解释某个 change/spec/doc 时，才读取最小必要文件。
- 单次 orient 读取正文时优先选择入口文件：`AGENTS.md`、`openspec/project.md`、目标 active change 的 `tasks.md` / `source-map.md`，以及用户明确点名的文件。
- 判断需要迁移、写需求、做架构或验证后，停止深读并转交 `aisee:spec-migrate`、`aisee:srs`、`aisee:architecture`、`aisee:verify` 等目标 skill。

## 路由规则

| 状态 / 意图 | 推荐下一步 |
|---|---|
| 缺少 `openspec/config.yaml`，且用户要接入 Aisee/OpenSpec | `aisee openspec ensure --json`，成功后 `aisee:init` |
| OpenSpec 存在，但 `AGENTS.md`、`openspec/project.md`、Aisee 目录或 hooks 缺失/漂移 | `aisee:init` |
| 已有项目需要建立当前行为基线，且 `openspec/specs/` 缺失或很薄 | `aisee:spec-migrate` |
| 用户描述新产品/功能需求但范围未清 | `aisee:srs` |
| 已有需求，涉及页面、交互、状态、权限或平台差异 | `aisee:ui-content` |
| 需要确认技术栈、模块、接口边界、部署或复用能力 | `aisee:architecture` |
| 已有需求/架构输入，需要拆成可交付 OpenSpec changes | `aisee:change-plan` |
| 已有 change-plan 或明确 change 边界，但缺 OpenSpec artifacts | `/opsx:new --schema <schema>` 后 `aisee:change-author` |
| 已有 active change 且 artifacts 基本完整，准备实现 | `aisee:implementation-bridge` |
| 实现后需要检查 artifacts、tasks、source-map、evidence 或 validate | `aisee:verify` |
| 准备执行 `openspec archive` | `aisee:archive-guard` |
| 用户询问项目长期偏好、记住规则或检索项目记忆 | `aisee:memory` |
| 用户询问团队知识、guardrails、跨项目经验或知识库同步 | `aisee:knowledge` |
| 用户要复盘本次会话或沉淀候选经验 | `aisee:reflect` |
| 用户要审查并推广 reusable knowledge candidates | `aisee:knowledge-curate` |
| 用户要安装或审计 OpenSpec custom schemas | `aisee-schema-pack` |

若多个路径都合理，按“阻塞当前目标的最早缺口”排序。例如缺 OpenSpec 初始化时，不直接进入 `aisee:change-plan`；已有 active change 且用户要继续实现时，不重新走 SRS。

## 输出格式

```markdown
# Aisee Orient 报告

## 当前判断
- 项目状态：
- OpenSpec 状态：
- Aisee 配置状态：
- Baseline specs：
- Active changes：
- 用户意图：

## 推荐下一步
首选：
原因：

## 可选路径
- 如果目标是新需求：
- 如果目标是迁移已有系统：
- 如果目标是继续 active change：
- 如果目标是验证或归档：

## 需要确认
- ...

## 已检查
- ...
```

## Guardrails

- 只做定位和路由；需要写文件、安装 hooks、迁移 baseline 或生成 artifacts 时，转交对应 skill。
- 不把 active change 当 baseline，不把 migration 草稿当正式 spec。
- 不在用户未明确接入 OpenSpec 时生成 OpenSpec/Aisee 项目文件。
- 不为路由目的过度扫描或深读文档；需要业务细节时交给后续目标 skill。
- 不因找不到某个工具就停止定位；说明限制并使用文件状态 fallback。
- 最终回复必须明确“下一步首选”以及理由，避免只列泛泛选项。
