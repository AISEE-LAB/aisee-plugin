---
name: aisee:spec-migrate
description: 基于已有项目快速整理 OpenSpec baseline specs，把现有代码、路由、页面、测试、API 文档和业务文档反向归纳为 openspec/specs/ 下的当前行为规范。用于“把旧项目迁移到 OpenSpec 管理”“整理现有系统 spec 基线”“从代码生成 OpenSpec specs”“补齐 openspec/specs”“建立 baseline spec”时触发。不要用于新需求 SRS、change 边界规划、design.md、tasks.md、实现代码或未来功能规划。
---

# aisee:spec-migrate — 现有项目 Spec 基线迁移

把已有项目的当前行为整理成 OpenSpec 静态层 `openspec/specs/`。它回答“系统现在是什么”，为后续 `/opsx:new`、delta specs 和 archive 建立基线。

`aisee:spec-migrate` 不是 `aisee:srs`：不整理未来需求。
`aisee:spec-migrate` 不是 `aisee:change-plan`：不规划 OpenSpec change 边界。
`aisee:spec-migrate` 不写 change 级 `proposal.md`、`design.md` 或 `tasks.md`。

## 输入

用户提供以下任意一种输入：

- 现有项目目录
- 现有需求文档、README、接口文档、测试目录
- 已初始化的 OpenSpec 项目
- 指定模块或目录范围

可选参数：

- `--scope project|module|path|auto` — 迁移范围，默认 `auto`
- `--mode inventory|draft|write|auto` — 只盘点、生成草案或写入 baseline specs，默认 `auto`
- `--batch-size <n>` — 单批最多生成的 spec 文件数，默认 5
- `--write patch|direct|chat` — 写入方式，默认 `patch`
- `--lang zh|en` — 输出语言，默认 `zh`

## 输出边界

`aisee:spec-migrate` 只产出现有系统行为的 OpenSpec baseline 和迁移索引。

必须输出或写入：

- 迁移范围和证据来源
- 能力边界图：按业务能力 / 领域划分，不按文件类型机械划分
- `openspec/specs/` 目录规划
- `openspec/specs/project.md` 的缺口建议或补丁
- `openspec/specs/<capability>/spec.md` baseline specs
- 证据追踪、可信度、冲突和 Open Questions
- 迁移批次计划，避免一次生成巨型 spec

禁止输出：

- 新功能需求或未来规划
- active change 的 delta spec，除非用户明确要求 bootstrap change
- `/opsx:new`、`/opsx:propose`、`/opsx:apply` 执行命令
- `proposal.md`、`design.md`、`tasks.md`
- 数据库迁移、实现计划或代码修改
- 无证据的业务规则断言

## 事实源边界

- `openspec/specs/` 是 baseline 规范事实源。
- `aisee/docs/spec-migration/` 是迁移索引、草案、证据和冲突记录区，不是最终规范事实源。
- Active changes 只能作为“未归档变更上下文”，不能直接当作当前 baseline 行为。
- 低可信度推断只能进入迁移索引或 Open Questions，不能写入正式 baseline spec。

## Phase 0 — 预检与扫描

确认 OpenSpec 状态：

```bash
node -e "const fs=require('fs'); for (const p of ['openspec/config.yaml','openspec/specs']) { try { const s=fs.statSync(p); console.log(p + ':' + (s.isDirectory()?'dir':'file')); } catch { console.log(p + ':missing'); } }"
```

处理规则：

- 缺少 `openspec/config.yaml`：停止写入 `openspec/specs/`，建议先运行 `openspec init` 或 `aisee:init`。
- 缺少 `openspec/specs/`：可以创建目录补丁，但必须说明这是 baseline migration。
- 已有 `openspec/specs/`：先读取现有 spec，避免覆盖和重复建模。
- 已有 active changes：读取 `openspec/changes/`，标注可能冲突；不要把 active delta 当作 baseline 事实。

扫描项目结构时必须遵守 `.gitignore`。优先使用 `rg --files`，不要用全仓库裸 `find` 把依赖、构建产物、缓存或生成文件当作项目事实：

```bash
rg --files | rg '(^|/)(package.json|pyproject.toml|go.mod|Cargo.toml|pom.xml|Gemfile|README.md|openapi\.ya?ml|openapi\.json)$|route|controller|page|screen|model|schema|test|spec' | head -220
rg --files docs openspec aisee/docs 2>/dev/null | head -160
```

如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物和缓存目录，并只查迁移需要的文件类型。

## Workflow

先按 Phase 0 预检和扫描，再按需读取 [workflow.md](references/workflow.md) 执行证据读取、能力边界建模、迁移索引生成、baseline specs 生成和校验。

Reference loading：

- 需要追问时读取 `references/question-bank.md`。
- 生成迁移索引前读取 `assets/migration-index-template.md`。
- 写入 baseline specs 前读取 `references/workflow.md` 中的 OpenSpec 校验与写入规则。
- 不使用 skill 内置 spec 正文模板；spec 格式以当前项目的 OpenSpec CLI 校验结果为准。

## Guardrails

- 只描述当前系统行为，不描述未来要做什么。
- 不把 active change 的 delta 当作 baseline 已有能力。
- 不覆盖已有 `openspec/specs/`；先 diff，再 patch。
- 不生成巨型单文件 spec。
- 不按文件类型、技术层或数据库表机械拆 spec。
- 不把低可信度推断写入正式 baseline。
- 不把 `aisee/docs/spec-migration/` 当作 OpenSpec 规范来源；最终规范必须落在 `openspec/specs/`。
- 不从 ignored 文件、依赖包、构建输出、缓存内容或生成产物中提取 baseline 事实。
- 每条正式 Requirement 必须满足当前 OpenSpec 校验器规则，包括 `SHALL` / `MUST` 和 Scenario。
- 如果缺少 OpenSpec 初始化，先让用户运行 `openspec init` 或 `aisee:init`。

## 与 aisee 链路集成

```text
已有项目
  └─ aisee:init                 ← 初始化 OpenSpec 与项目上下文
       └─ aisee:spec-migrate    ← 反向整理现有系统 baseline specs
            └─ openspec/specs/  ← 当前系统行为基线

后续新需求
  ├─ aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:architecture
  └─ aisee:change-plan
       └─ /opsx:new <change>
            └─ aisee:change-author
                └─ schema artifacts + apply tracks
```
