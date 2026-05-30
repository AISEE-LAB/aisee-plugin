---
name: aisee:change-design
description: >-
  Legacy compatibility skill，待 aisee-app-spec-driven 与 device schema 定型后删除。仅当当前 OpenSpec change 的 schema 明确包含 design.md artifact 时，生成、补齐或审查 design.md。aisee-app-spec-driven v2 不再适用本技能，应改补 change-context.md 和相关 contracts。用于 proposal 已存在后，读取当前 change 使用的 OpenSpec schema，确认该 schema 存在 generates: design.md，并严格按照官方 design.md 模板与 artifact instruction 填充设计内容。触发词包括 aisee:change-design、补 design.md、生成 design.md、完善 change design、OpenSpec design。若 schema 不包含 design.md，应停止并提示改用该 schema 的对应 artifact；不要用于创建业务需求、直接写 specs、执行代码实现、替代 tasks，或自造 design.md 模板。
---

# aisee:change-design — Legacy OpenSpec Change Design

> Legacy：本技能仅作为仍包含 `design.md` 的旧 schema / 兼容 schema 的过渡能力。`aisee-app-spec-driven` v2 已改用 `change-context.md`，不要再对 app schema 创建或补齐 `design.md`。待 app/device schema 定型后，本技能可以删除。

在 OpenSpec change 中负责 **design.md 阶段**。它不是后端专用技能，而是单个 change 的设计补齐器：页面如何承载、前端如何取数和反馈、后端接口如何协作、数据如何落库、权限和状态如何流转。

本技能只适用于当前 schema 明确定义了 `generates: design.md` 的 change。若当前 schema 没有 design artifact，不要强行创建 `design.md`。

关键约束：**不得自造 design.md 顶层模板**。必须先确认当前 schema 包含 design artifact，再读取该 schema 的官方 design 模板，并按模板填充。

## 输入

优先输入：
- `openspec/changes/<change>/` 目录
- `openspec/changes/<change>/proposal.md`

可附加输入：
- `aisee:srs` 输出的 SRS
- `aisee:ui-content` 输出的 UI 内容规格
- `aisee:architecture` 或项目级技术栈摘要
- 本 change 的特殊技术约束（必须与项目级技术栈兼容）

可选参数：
- `--stack <description>` — 补充本 change 的技术约束；不得覆盖项目级技术栈
- `--mode standard|deep|auto` — 设计深度，默认 `auto`
- `--write patch|direct|chat` — 写入方式，默认 `patch`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:change-design` 输出 OpenSpec change 的 `design.md` 内容或补丁建议，结构必须来自 OpenSpec schema 模板。

适用 schema：
- `aisee-device-spec-driven`
- `security-audit`
- 官方或自定义 schema 中其他明确包含 `generates: design.md` 的 schema

不适用 schema：
- `aisee-app-spec-driven` v2：改补 `change-context.md` 和相关 contracts
- `aisee-docsite-driven`：改补 `doc-change.md`
- `quick-fix`：改补 `solution.md`
- `quick-research`：改补 `findings.md` / `recommendation.md`
- `infra-change`：改补 `impact-assessment.md` / `rollback-plan.md`
- `opsx-collab-pr-loop`：改补 `implementation.md` / `checkpoints.md`

必须覆盖当前 schema 下适用的设计面；不适用项写明 N/A 原因或跳过，不要为 device/security schema 强行套 Web 字段：
- 来源与范围：proposal、SRS、UI 内容规格、全局技术栈、现有代码事实
- 技术栈识别与约束来源
- 页面 / 前端设计：页面承载、路由、状态、数据流、表单提交、错误反馈
- 数据模型、关系、约束、迁移与数据兼容策略
- 接口 / 能力契约、鉴权、幂等、分页、错误语义
- 权限模型、数据可见范围、安全与隐私
- 业务流程、状态机、异步任务、事件、外部集成
- 性能、可靠性、可观测性、审计、日志、告警
- 发布、回滚、数据迁移、兼容策略
- 测试策略
- 如果 schema instruction 要求，可以列出后续 specs 应覆盖的用户可观察行为；但不要直接生成 specs
- Open Questions、风险、需要修改 proposal 或上游需求的事项

禁止输出：
- 直接创建或改写 specs 内容
- 新增未确认业务需求
- 大段实现代码、逐文件 coding plan
- 与现有项目事实冲突但未标注的设计
- 未查证的框架/API/ORM 用法断言
- 在项目级技术栈缺失时仍继续生成具体数据库、接口、ORM、队列或部署设计
- 自造 `design.md` 顶层章节或替换官方 schema 模板

---

## Phase 0 — 读取 change 与上游上下文

必须先确认当前是否已有 OpenSpec change。

如果用户输入是 change 目录：
1. 读取 `proposal.md`
2. 读取现有 `design.md`（如果存在）
3. 读取 `specs/` 仅作冲突检查；注意正常流程中 specs 可能尚未生成
4. 读取 `tasks.md` 仅作已存在任务约束；注意正常流程中 tasks 可能尚未生成
5. 读取 `.openspec.yaml`，确认当前 change 使用的 schema

如果用户没有提供 change：
- 不要假装生成正式 `design.md`
- 输出 `[CHANGE-REQUIRED]`，建议先创建 change 骨架，例如 `/opsx:new <change-name>`
- 只有用户明确要求“先草拟”时，才输出聊天中的设计草案，不写入 `docs/tech-design/`

静默收集项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -160
cat CLAUDE.md 2>/dev/null | head -80
find . -maxdepth 3 \( -name package.json -o -name pnpm-lock.yaml -o -name yarn.lock -o -name package-lock.json -o -name pyproject.toml -o -name requirements.txt -o -name Gemfile -o -name go.mod -o -name Cargo.toml -o -name pom.xml -o -name build.gradle -o -name composer.json -o -name prisma -o -name drizzle -o -name migrations -o -name schema.sql -o -name openapi.yaml -o -name openapi.json \) 2>/dev/null | head -80
```

如果是既有项目二次开发，继续做轻量代码库扫描：
- 查找路由、页面、控制器、服务、模型、schema、migration、API contract、权限中间件、测试目录
- 只读与当前 change 相关的文件
- 不要因为命名猜测项目事实；关键断言必须来自文件内容

当涉及具体框架、SDK、ORM、数据库、云服务或 API 用法时，必须使用 Context7 获取当前官方文档；没有文档支撑时，把结论标为假设或 Open Question。

---

## Phase 0.5 — 解析 OpenSpec Design 模板

必须在生成任何 design 内容前解析模板。

步骤：
1. 从 `openspec/changes/<change>/.openspec.yaml` 读取 schema 名称；如果不存在，默认 `spec-driven`，并标注为假设。
2. 运行：

```bash
openspec templates --schema <schema> --json
```

3. 检查 JSON 中是否存在 `design.path`，或 schema artifacts 中是否存在 `generates: design.md`。
4. 如果当前 schema 不包含 design artifact：
   - 停止生成正式 `design.md`
   - 输出 `[DESIGN-ARTIFACT-NOT-APPLICABLE]`
   - 说明当前 schema 应补齐的 artifact，例如 `doc-change.md`、`solution.md`、`findings.md`、`impact-assessment.md`
   - 不要创建 `design.md`，不要把 design 内容塞进其他 artifact
5. 从 JSON 中取得 `design.path` 并读取该文件。
6. 如需 artifact instruction，读取 schema 文件：
   - custom schema：`openspec/schemas/<schema>/schema.yaml`
   - package schema：可用 `openspec templates --schema <schema>` 输出的 package 路径辅助定位
7. 生成或补齐 `design.md` 时，保持官方模板的顶层结构和顺序。

对默认 `spec-driven`，官方模板目前由 OpenSpec 包提供；不要把本 skill 的资源文件当作模板来源。

本 skill 的 `assets/template-rules.md` 只是模板定位和填充规则，不是 `design.md` 模板。

如果无法解析模板路径：
- 停止生成正式 `design.md`
- 输出 `[SCHEMA-TEMPLATE-REQUIRED]`
- 提示用户先修复 OpenSpec schema 或运行 `openspec templates --schema <schema>`

---

## Phase 1 — 项目技术栈约束校验

`aisee:change-design` 运行时已经进入 OpenSpec change 阶段。正常情况下，项目级技术栈应已在 `openspec/project.md`、`aisee:architecture` 或既有项目文件中确认。

本阶段只做校验，不做技术选型。

必须确认：
- 项目级技术栈来源：`openspec/project.md` / architecture / 现有项目文件 / 用户明确确认
- 本 change 是否有特殊技术约束
- 特殊约束是否与项目级技术栈兼容
- 当前设计需要的关键基础设施是否已存在或已被项目级技术栈覆盖（数据库、ORM、鉴权、队列、缓存、文件存储、外部服务等）

规则：
- 项目事实优先于用户临时偏好。
- 如果 `--stack` 或用户输入与项目级技术栈冲突，标注 `[STACK-CONFLICT]`，解释冲突并等待确认，不要静默改栈。
- 如果 change 需要的关键基础设施没有在项目级技术栈中定义，标注 `[STACK-GAP]` 或 `[STACK-DECISION-REQUIRED]`，暂停具体设计，不要临场选型。
- 如果完全找不到项目级技术栈来源，标注 `[STACK-CONTEXT-MISSING]`，建议先更新 `openspec/project.md` 或运行 `aisee:architecture`。
- 只有在技术栈来源已确认的情况下，才写具体数据库、接口、ORM、队列或部署相关设计。

---

## Phase 2 — Design 输入完整性检查

读取 `references/question-bank.md`，只追问阻塞 design.md 的问题。

必须追问或标注的情况：
- proposal 范围不清，无法判断本 change 的设计边界
- UI 内容规格缺失，且 change 明显涉及页面/交互
- 需求没有明确数据所有者、权限边界或状态流转
- 写入操作缺少幂等、并发或重复提交规则
- 外部集成缺少失败处理、重试、超时或数据一致性要求
- 项目级技术栈缺少本 change 需要的关键组件

追问规则：
- 每轮最多 3 个问题
- 优先问会改变页面承载、数据模型、接口契约、权限模型的问题
- 不超过 3 轮；仍不明确时，写入 Open Questions

---

## Phase 3 — 设计深度选择

默认 `auto`。

### standard

适用于单个中等复杂度 change。输出一份 `design.md`。

### deep

满足任意条件时使用：
- 涉及 5 个以上核心实体
- 涉及复杂页面流程、复杂状态机、审批流、支付、外部集成、批量导入导出、异步任务
- 涉及安全、隐私、审计、合规、迁移或兼容风险
- 涉及多端一致性、离线、弱网或高并发

如果范围明显超过一个 OpenSpec change，应建议回到 `aisee:change-plan` 重新规划 change 边界，不要把过大的 Epic 强行写成一份 design。

---

## Phase 4 — 生成 / 补齐 design.md

读取 Phase 0.5 解析出的官方 `design.md` 模板，按该模板生成或补齐。

设计原则：
- 基于 `proposal.md`、SRS、UI 内容规格、技术架构和现有项目事实推导
- 每个关键设计都标注来源：proposal、SRS FR、UI 内容规格、现有代码事实或用户约束
- 保持 schema 官方模板的顶层章节；补充细节只能写入对应官方章节内部
- 如果 schema instruction 要求但模板未显式包含某节，可在最接近的官方章节中用子标题表达，不要重排整份模板
- design.md 可以说明后续 specs 应覆盖哪些行为，但不直接生成 specs
- 对会影响实现的风险使用 `[RISK]`
- 对 proposal 或上游需求缺口使用 `[SPEC-GAP]`
- 对需要正式修改 proposal / SRS / UI content 的冲突使用 `[SPEC-CHANGE-REQUIRED]`
- 对项目级技术栈缺口使用 `[STACK-GAP]` / `[STACK-DECISION-REQUIRED]` / `[STACK-CONTEXT-MISSING]`
- 对 change 技术约束和项目级技术栈冲突使用 `[STACK-CONFLICT]`

如果已有 `design.md`：
- 先读取并保留已存在的架构决策
- 不静默覆盖
- 只补充缺口或提出 patch
- 与已有设计冲突时标注 `[SPEC-CHANGE-REQUIRED]`

---

## Phase 5 — 写入策略

默认目标是当前 change：

`openspec/changes/<change>/design.md`

写入方式：
- `--write patch`：默认。输出可审查补丁建议，适合已有 design 或不确定是否覆盖。
- `--write direct`：用户明确要求时直接写入/更新 `design.md`。
- `--write chat`：只在聊天中输出，不落盘。

不要默认写入 `docs/tech-design/`。如果没有 change，优先让用户先创建 change；只有用户明确要求草案时才在聊天中输出。

---

## 完成输出

完成后输出：

> Change design 已生成 / 已补齐：`openspec/changes/{change}/design.md`
>
> 技术栈来源：openspec/project.md / architecture / 现有项目文件 / 用户确认
> 覆盖：{pages} 个页面承载、{entities} 个核心实体、{apis} 个接口能力、{jobs} 个异步任务、{risks} 个风险、{questions} 个待确认事项。
>
> 下一步：根据 design.md 的 “后续 specs 应覆盖的行为” 生成 specs，然后补 tasks。

若存在阻塞项：

> Change design 存在阻塞项：{tags}
> 请先确认这些决策，再进入 specs 或 tasks 阶段。

---

## Guardrails

- 必须遵守当前项目约定的 OpenSpec 状态机；同时遵守当前 change 的 schema artifact 依赖。
- 没有 change 时，不要默认生成正式 design.md；先提示创建 change。
- 当前 schema 不包含 `design.md` artifact 时，必须停止并输出 `[DESIGN-ARTIFACT-NOT-APPLICABLE]`，提示改用该 schema 的对应 artifact。
- 必须读取当前 schema 的官方 `design.md` 模板；不得使用本 skill 自造模板。
- 不要新增官方模板之外的顶层章节，除非当前 schema 的 artifact instruction 明确要求。
- 不要直接生成 specs；只在 design.md 中列出后续 specs 应覆盖的行为。
- change 阶段不做技术选型；技术栈缺失时必须暂停并标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`。
- 既有项目中，现有架构和 `openspec/project.md` 优先。
- change 技术约束与项目事实冲突时，必须标注 `[STACK-CONFLICT]` 并等待确认。
- 涉及框架/API/ORM/SDK/云服务细节时，必须使用 Context7 查当前官方文档。
- 不要把需求缺口包装成技术假设；标注 `[SPEC-GAP]`。
- 不要在 design.md 中新增业务需求；需要变更需求时标注 `[SPEC-CHANGE-REQUIRED]`。
- 不要输出大段代码或逐文件实现计划；执行细节留给 `tasks.md`、`aisee:implementation-bridge` 和后续工程实现阶段。
- 每个页面相关 change 必须说明页面承载、数据流、加载/错误/提交反馈。
- 每个接口能力必须说明鉴权、错误、幂等或为什么不需要。
- 每个写入数据模型都必须说明唯一性、数据所有权、删除/归档、迁移或兼容影响。
- 每个外部集成都必须说明超时、重试、幂等、失败恢复和可观测性。
- device schema 的硬件、固件、运行时和验证总体决策必须映射到后续 contract artifacts。
- security schema 的威胁模型、安全边界和缓解措施必须映射到 threat-model.md 与后续 tasks。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:architecture / stack decision  # 可选，change-plan 前技术边界
  └─ aisee:change-plan
       └─ /opsx:new <change>
            └─ 补 proposal.md
            └─ aisee:change-design        ← 仅当 schema 包含 design.md 时生成 / 补齐 design.md
            └─ 补 specs/
            └─ 补 tasks.md
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```

大 Epic 推荐先用 `aisee:change-plan` 规划为独立 change，再逐个运行 `aisee:change-design`。不要对整个 Epic 直接生成一份过大的 design。
