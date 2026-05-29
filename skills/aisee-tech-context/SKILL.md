---
name: aisee:tech-context
description: 在 aisee:change-plan 之前生成技术上下文摘要，提取项目级技术栈状态、现有架构边界、可复用能力、共享技术前置、技术耦合点、平台/端能力限制、技术风险和给 change-plan 的技术提示。用于用户要求“分析技术上下文”“补技术约束”“change-plan 前看技术边界”“现有项目技术栈扫描”“生成 tech-context”“判断技术栈是否已定”“为规划 change 边界提供技术输入”时触发。不要用于规划 change 边界、命名 change、生成 design.md、做技术选型或写实现方案。
---

# aisee:tech-context — 技术上下文摘要

在 `aisee:change-plan` 前运行，给 change 边界规划提供技术事实和约束输入。它不拆 change，不生成 change 名称，不安排阶段，不写 `design.md`。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 输出的 SRS 文件
- `aisee:ui-content` 输出的 UI 内容规格
- 已确认需求文本
- 既有项目目录
- `openspec/project.md` 或架构文档

可选参数：
- `--scope project|feature|auto` — 技术上下文范围，默认 `auto`
- `--mode scan|synthesize|auto` — 扫描现有项目或汇总用户提供材料，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:tech-context` 只输出技术上下文和 change-plan 输入提示。

必须覆盖：
- 项目级技术栈状态：已确定 / 部分确定 / 未确定
- 技术栈来源与可信度
- 现有架构边界和模块边界
- 已有可复用能力：鉴权、权限、数据访问、队列、缓存、文件、通知、审计、日志等
- 共享技术前置：多个 FR / 页面共同依赖的技术基础
- 技术耦合点：数据模型、权限、异步任务、外部集成、多端能力等
- 平台 / 端能力限制
- 技术风险和阻塞决策
- 给 `aisee:change-plan` 的技术提示

禁止输出：
- change 边界规划方案
- change 名称
- phase / dependency graph
- `/opsx:new`、`/opsx:propose` 命令
- `design.md` 内容
- 数据库表结构、API endpoint、ORM 代码或实现计划
- 技术栈选型结论；缺失时只能标注 `[STACK-CONTEXT-MISSING]` / `[STACK-DECISION-REQUIRED]`

---

## Phase 0 — 读取输入与项目上下文

先读取用户提供的输入文件或文本。若路径不存在，停止并说明。

静默收集项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat CLAUDE.md 2>/dev/null | head -160
cat AGENTS.md 2>/dev/null | head -160
find . -maxdepth 3 \( -name package.json -o -name pnpm-lock.yaml -o -name yarn.lock -o -name package-lock.json -o -name pyproject.toml -o -name requirements.txt -o -name Gemfile -o -name go.mod -o -name Cargo.toml -o -name pom.xml -o -name build.gradle -o -name composer.json -o -name prisma -o -name drizzle -o -name migrations -o -name schema.sql -o -name openapi.yaml -o -name openapi.json \) 2>/dev/null | head -80
find docs -maxdepth 3 \( -iname '*architecture*' -o -iname '*tech*' -o -iname '*stack*' -o -iname '*design*' \) 2>/dev/null | head -40
```

如果是既有项目：
- 只读与输入需求相关的目录和文件
- 查找路由、页面、控制器、服务、模型、schema、migration、API contract、权限中间件、任务队列、测试目录
- 不要因为文件名猜测项目事实；关键结论必须标注来源

当涉及具体框架、SDK、ORM、数据库、云服务或 API 用法判断时，使用 Context7 获取当前官方文档；没有文档支撑时标注为假设。

---

## Phase 1 — 技术栈状态判断

判断项目级技术栈状态：

| 状态 | 条件 | 处理 |
|------|------|------|
| 已确定 | `openspec/project.md` 或既有项目文件明确说明关键技术栈 | 记录来源并继续 |
| 部分确定 | 只确认部分层，例如前端/后端已定但队列/缓存/部署未定 | 标注缺口并继续生成上下文 |
| 未确定 | 没有可信来源确认关键技术栈 | 标注 `[STACK-CONTEXT-MISSING]`，不要替用户选型 |

关键技术栈包括：
- 前端框架 / 客户端形态
- 后端框架 / 服务边界
- 数据库
- ORM / 数据访问
- 鉴权与权限体系
- 队列 / 异步任务
- 缓存
- 文件存储
- 通知 / 消息
- 部署环境

---

## Phase 2 — 技术事实提取

读取 `references/question-bank.md`，只追问会影响技术上下文判断的问题。

提取并标注来源：
- 技术栈事实
- 模块边界
- 数据模型现状
- 权限体系现状
- API / 路由 / 服务边界
- 异步任务、队列、定时任务、通知现状
- 外部集成现状
- 多端能力限制
- 已有测试和验证方式

来源可信度：
- `high`：来自 `openspec/project.md`、代码、schema、配置、官方架构文档
- `medium`：来自 SRS、UI 内容规格、用户明确说明
- `low`：从命名或上下文推断，必须标注为假设

---

## Phase 3 — 生成给 change-plan 的技术提示

只写会影响 `aisee:change-plan` 的技术提示，不写 change 边界规划方案。

允许写：
- 共享技术前置：多个需求共同依赖的技术基础
- 技术耦合点：应被 change-plan 考虑的技术关联
- 可并行边界：哪些模块从技术上相互独立
- 不应横切的能力：例如不要把同一状态机拆散
- 阻塞性技术决策：缺队列、缺鉴权、缺数据库方案等
- 高风险区域：外部集成、迁移、权限、安全、性能

禁止写：
- “Change 1 / Change 2”
- change 名称
- 阶段依赖图
- 具体 `/opsx:*` 命令
- 最终 change 边界规划结论

---

## Phase 4 — 保存文档

读取 `assets/tech-context-template.md`，生成文档。

默认保存：

```bash
mkdir -p docs/tech-context
```

文件：

`docs/tech-context/<YYYY-MM-DD>-<slug>.md`

如果用户只要求分析，可以只在聊天中输出。

---

## 完成输出

完成后输出：

> 技术上下文摘要已生成：`docs/tech-context/{filename}.md`
>
> 技术栈状态：已确定 / 部分确定 / 未确定
> 识别：{N} 个架构边界、{M} 个可复用能力、{K} 个共享技术前置、{R} 个风险、{Q} 个阻塞决策。
>
> 下一步：将本文档与 SRS、UI 内容规格一起交给 `aisee:change-plan`。

若存在阻塞项：

> 存在技术上下文阻塞项：{tags}
> 这些阻塞项会影响 change 边界规划，但本技能不会直接规划 change 边界。

---

## Guardrails

- 不要规划 change 边界，不要命名 change，不要输出 phase 或依赖图。
- 不要生成 `/opsx:new`、`/opsx:propose` 或其他执行命令。
- 不要生成 `design.md`。
- 不要做技术选型；技术栈缺失时标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`。
- 不要把推断写成事实；每条关键技术事实都要有来源和可信度。
- 不要输出数据库表结构、API endpoint、ORM 代码或实现步骤。
- 如果发现需求与现有技术约束冲突，标注 `[SPEC-GAP]` 或 `[STACK-CONFLICT]`，不要静默绕过。
- 给 `aisee:change-plan` 的技术提示只能是事实、约束和原因，不是边界规划结果。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:tech-context       ← 本技能：change-plan 前技术事实与约束
  └─ aisee:change-plan              ← 基于 SRS + UI content + tech-context 拆 change
       └─ /opsx:new <change>
            └─ aisee:change-design  # 仅当 schema 包含 design.md
            └─ specs/
            └─ tasks.md
            └─ /opsx:apply
```
