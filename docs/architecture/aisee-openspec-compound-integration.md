# Aisee、OpenSpec 与 Compound Engineering 融合方案

## 背景

当前 `aisee*` 能力以多个独立 skill 的形式存在，覆盖需求澄清、UI 内容规格、技术架构、OpenSpec change 规划、schema pack、项目初始化、视觉资产、对象级图片处理和会话复盘等工作。

Compound Engineering 插件则更偏向工程执行、代码审查、测试、提交、PR、复盘和团队知识沉淀。OpenSpec 是规范状态机和 baseline source of truth。

因此，融合目标不是把所有能力压成一个超大 skill，而是建立清晰分层：

```text
Aisee = 需求澄清、上下文整理、change 边界规划、规范产物编排
OpenSpec = 规范状态机、schema、change artifacts、baseline source of truth
Compound Engineering = 工程执行、代码审查、测试、提交、PR、实现复盘
```

## 结论摘要

- 可以把所有 `aisee*` skill 整合成一个 `aisee-plugin`，形态类似 Compound 插件。
- 不建议把所有 aisee 能力合并为一个巨大的 `SKILL.md`。
- 应该保留专业 skill 的边界，新增编排型和守门型 skill。
- 应新增 `aisee CLI` 作为上下文总线，负责索引、ID Registry、context pack、doctor 和 bootstrap。
- `openspec archive` 不应被替代，它负责把已验证 change 合并进 baseline。
- `compound plan / ce-plan` 不应作为固定步骤；它只能按需细化 `tasks.md`，且结论必须回写 OpenSpec change。
- `compound work / ce-work` 的执行依据应是单个 OpenSpec change 工程包，而不是平行计划文档。
- App/Web 与硬件/嵌入式必须走不同 domain 适配层，不能共用同一套 UI/服务/数据产物。

## 推荐插件结构

```text
aisee-plugin/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  .cursor-plugin/plugin.json
  bin/
    aisee
  skills/
    aisee-flow/
    aisee-init/
    aisee-schema-pack/
    aisee-srs/
    aisee-ui-content/
    aisee-architecture/
    aisee-device-context/
    aisee-change-plan/
    aisee-change-author/
    aisee-implementation-bridge/
    aisee-verify/
    aisee-archive-guard/
    aisee-spec-migrate/
    aisee-reflect/
    aisee-design-assets/
    aisee-svg-assets/
    aisee-image-object/
  references/
    compound-bridge.md
    context-pack-contract.md
    id-policy.md
  scripts/
    context-parser/
    id-registry/
    bootstrap/
  README.md
```

Schema pack 的唯一维护源位于 `skills/aisee-schema-pack/assets/schema-pack/`，由 `aisee-schema-pack/scripts/setup-schemas.js` 安装到目标项目的 `openspec/schemas/`。仓库根目录不再保留第二份 `schemas/` 副本。

插件内部建议分层：

```text
aisee-core:
  flow / init / schema-pack / srs / architecture / change-plan / change-author / verify / archive-guard / reflect

aisee-app:
  ui-content / app schema / ui-contract / service-contract / data-model / frontend handoff

aisee-device:
  device-context / hardware-contract / firmware-contract / runtime-contract / verification-contract

aisee-visual-assets:
  design-assets / svg-assets / image-object

aisee-bridge:
  implementation-bridge / compound-bridge / context pack / ID registry
```

## 职责分工

### Aisee

Aisee 负责上游结构化和规范编排：

- 从模糊需求生成 SRS。
- 从 SRS 生成 UI 内容规格或设备上下文。
- 扫描项目技术事实和约束。
- 规划 OpenSpec changes 的边界、依赖、schema 和 source-map 初稿。
- 生成 OpenSpec change artifacts 初稿。
- 在实现前后检查 spec、tasks、source-map、验证记录是否一致。

Aisee 不应该直接成为最终规范基线，也不应该替代 OpenSpec 状态机。

### Aisee CLI

Aisee CLI 是 Aisee/OpenSpec/Compound 之间的上下文总线，也是 OpenSpec context companion：

- `aisee doctor`：检查 OpenSpec、Aisee、Compound 能力是否可用。
- `aisee bootstrap --plan/--apply`：生成或执行项目初始化计划。
- `aisee sources`：登记 SRS、UI 内容、architecture、device-context 等 change 外部产物来源。
- `aisee index`：建立可删除、可重建的解析缓存，用于加速查询；不是内容事实源。
- `aisee get <id>`：根据稳定 ID 查询需求、页面、硬件约束、固件行为、任务等详情。
- `aisee trace <id>`：查询 ID 上下游关系。
- `aisee change inspect <change>`：衔接单个 OpenSpec change，返回 schema/artifact metadata、ID、路径和 evidence。
- `aisee context pack --change <change> --for <target>`：调用时汇总 OpenSpec metadata、sources、ID registry、source-map 和 evidence，生成给 Aisee skill 或 CE skill 的最小上下文包。
- `aisee id reserve/activate/check`：维护 `aisee/registry/id-registry.json`。

Aisee CLI 不替代 OpenSpec CLI。它只负责来源登记、ID/路径/证据追踪、metadata scan、查询、初始化编排和 AI 友好 JSON 输出。JSON 是当前 OpenSpec/Aisee/CE 事实的上下文视图，不是第二份事实源。OpenSpec artifacts 的合法性仍以 `openspec validate` 和 OpenSpec schema 机制为准。详细设计见 [aisee-cli-context-and-id-registry.md](aisee-cli-context-and-id-registry.md)。

### OpenSpec

OpenSpec 负责规范状态：

- 维护 `openspec/specs/` baseline。
- 维护 `openspec/changes/` active changes。
- 通过 schema 约束 artifacts。
- 通过 validate 检查 change 合法性。
- 通过 archive 把完成且验证通过的 change 合并进 baseline。

`/opsx:apply` 是 OpenSpec 原生实现入口，不是规划工具；在 Aisee + Compound 链路中，工程实现由 `aisee:implementation-bridge` 交接给 `ce-work` 承接。

### Compound Engineering

Compound Engineering 负责工程审核和执行：

- 按需对单个已确认 change 做实现策略补充。
- 审核 SRS、当前 schema artifacts、apply tracks、source-map（如适用）等文档产物。
- 执行代码修改、测试、review、提交、PR。
- 解决 PR 反馈和 CI 失败。
- 沉淀工程经验。

Compound 不应该直接绕过 OpenSpec 修改 baseline spec。如果实现过程中发现需求变化，应回写当前 OpenSpec change，再重新 validate。

CE 相关 skill 的定位：

```text
ce-doc-review
= 文档审核 gate，审核 SRS / 当前 schema artifacts / apply tracks / source-map（如适用）

ce-plan
= 可选任务细化器，不是长期事实源；有效结论必须回写当前 schema apply tracks；仅 source-map schema 需要回写 source-map.md

ce-work
= 按单个 OpenSpec change 工程包执行实现

ce-debug
= 处理失败、异常和阻塞

ce-code-review / ce-test-*
= 实现后审核和专项验证

ce-commit / ce-commit-push-pr / ce-resolve-pr-feedback
= 交付、PR 和反馈处理
```

## 是否继续使用 /opsx:apply、archive 和 compound plan

继续使用，但要限定边界：`/opsx:apply` 属于实现入口，`openspec archive` 才是已完成 change 合入 baseline 的最终动作。

```text
aisee:change-plan
= 需求 / 页面 / 技术架构 -> OpenSpec change 边界、依赖、schema、source-map 初稿

compound plan / ce-plan
= 单个已确认 OpenSpec change -> 工程实现步骤、测试策略、代码修改路径

openspec archive
= 已实现、已验证、spec 与代码一致的 change -> baseline
```

推荐流程：

```text
需求想法
  ↓
aisee:srs
  ↓
aisee:ui-content 或 aisee:device-context
  ↓
aisee:architecture
  ↓
aisee:change-plan
  ↓
aisee:change-author
  ↓
openspec validate
  ↓
aisee:implementation-bridge
  ↓
compound plan / work / review / test
  ↓
aisee:verify
  ↓
aisee:archive-guard
  ↓
openspec archive
```

## 保持独立的接入 Skill

不再保留独立 setup skill。该能力会与 `aisee:flow`、`aisee:init`、`aisee-schema-pack` 和 `aisee doctor` 重叠，不能解决独立问题域。

接入阶段分工：

- `aisee doctor`：检查 OpenSpec、Aisee、schema pack、sources、ID registry 和 hooks 等基础状态。
- `aisee:init`：初始化或审计 `AGENTS.md`、`openspec/project.md`、`aisee/memory/` 和 Codex hooks。
- `aisee-schema-pack`：安装、审计和维护 Aisee schema pack。
- `aisee:flow`：在基础设施缺失时提示上述入口，但不执行初始化或 schema 安装。

### 保持独立的资产类 Skill

不再保留独立资产入口 skill。视觉资产路由本身不是一个稳定产物，会与三个专业 skill 的 description 重叠。

资产类能力保持独立：

- `aisee:design-assets`：参考图、StyleSpec 草稿、视觉素材计划、Figma brief 和开发视觉 brief。
- `aisee:svg-assets`：SVG 图标、logo、装饰图形、位图矢量化、SVG 优化与校验。
- `aisee:image-object`：对象分割、去背景、mask、透明切图、背景修补和图层包。

OpenSpec change 只引用资产路径、StyleSpec 路径和必要验证任务；不要把完整视觉文档复制进 change artifacts。

资产类 skill 不进入每个 OpenSpec change 的必经流程。它们只在 App/Web、品牌、视觉、前端素材相关 change 中按需触发：

```text
aisee:ui-content
= 页面、字段、状态、操作、权限、流程

aisee:design-assets
= 视觉风格、参考图、StyleSpec、素材计划、Figma handoff

aisee:svg-assets
= 可交付 SVG 资产、logo、图标、校验和优化

aisee:image-object
= 可交付位图素材、透明切图、mask、背景修补
```

OpenSpec change 只通过 `ui-contract.md`、`source-map.md` 和 `tasks.md` 引用资产路径和验收约束，不复制整份 StyleSpec 或素材说明。

### 删除 change-design，统一由 change-author 编排

不要保留独立 `aisee:change-design`。`design.md` 不再是 App/Web change 的默认产物；只有当前 schema 明确生成 `design.md` 时，`aisee:change-author` 才按该 schema 的官方模板直接补齐对应 artifact。

这样可以避免弱 skill 引入旧 OpenSpec `design.md` 默认流程，也避免和 `change-context.md`、`ui-contract.md`、`service-contract.md`、`data-model.md` 的边界重叠。

```text
aisee:change-author
  ├─ proposal.md
  ├─ source-map.md        -> sources / ID trace / artifact applicability
  ├─ specs/**/spec.md
  ├─ tasks.md
  ├─ change-context.md    -> App/Web schema Required=yes 时承接 Architecture 的局部上下文
  ├─ design.md            -> 仅当 schema 明确包含 design.md 时按 schema 模板直接生成
  ├─ ui-contract.md       -> App/Web schema Required=yes 时生成
  ├─ service-contract.md  -> App/Web schema Required=yes 时生成
  ├─ data-model.md        -> App/Web schema Required=yes 时生成
  ├─ hardware-contract.md
  ├─ firmware-contract.md
  ├─ runtime-contract.md
  └─ verification-contract.md
```

## 不建议合并的 Skill

### aisee:srs

保留独立。它负责需求契约，不写 UI 视觉、技术实现或代码计划。

### aisee:ui-content

保留独立。它负责 App/Web 的页面、元素、状态、权限可见性和跨页面流程，不负责视觉设计或实现方案。

### aisee:architecture

保留独立。它负责技术架构事实、架构决策和约束，不负责拆 change、技术选型或实现方案。

### aisee-spec-migrate

保留独立。它用于既有项目反向整理 baseline specs，触发条件和风险不同于新需求规划。

### aisee:reflect

保留独立。它用于会话复盘和知识沉淀，不应进入每次需求规划主链。

## 建议新增的 Skill

### aisee:flow

工作流状态编排器。

职责：

- 读取项目、OpenSpec change、Aisee sources、ID registry、source-map、CE review/test 记录。
- 判断当前 workflow stage。
- 识别缺口、断链、过期和冲突。
- 编排下一组 Aisee skill、OpenSpec 操作和 CE gate。
- 阻止错误跳步，例如没有 change artifacts 时直接进入 `ce-work`。
- 输出工作流状态卡，而不是生成核心文档。

它不负责：

- 写 SRS 全文。
- 拆 change 边界。
- 为多个 change 决定最终 schema。
- 生成 `design.md`、`tasks.md` 或代码。
- 替代 `openspec validate/archive`。
- 替代 CE review/work/test。

它和 `aisee:change-plan` 的边界：

```text
aisee:flow
= 判断是否应该进入 change-plan，以及进入前缺什么

aisee:change-plan
= 真正拆 change、定依赖、定粒度、定每个 change 的最终 schema
```

`aisee:flow` 只能给 domain hint 或 schema family hint。只在跳过 `change-plan` 的 quick-fix 等单 change 快路径中，才可以推荐轻量 schema。

每次运行建议输出一张状态卡：

```md
# Aisee Workflow State

## Current Stage

`context-ready`

## Domain

`app`

## Known Inputs

- SRS: `aisee/docs/requirements/auth-srs.md`
- UI Content: `aisee/docs/ui-content/auth-ui.md`
- Architecture: `aisee/docs/architecture/auth-architecture.md`

## Missing / Blocking

- 尚未生成 change-plan
- 尚无 OpenSpec change artifacts
- 不能进入 ce-work

## Recommended Path

1. 运行 `aisee:change-plan`
2. 生成 change 边界、依赖、schema
3. 对每个 change 运行 `aisee:change-author`
4. 运行 `ce-doc-review`
5. 运行 `aisee:verify`

## Guardrails

- 不要直接进入 `ce-work`
- 不要让 `ce-plan` 生成长期任务清单
- schema 由 `aisee:change-plan` 对每个 change 最终决定
```

推荐 workflow stage：

```text
uninitialized
= 项目未准备好，先运行 aisee doctor，并按缺口进入 aisee:init 或 aisee-schema-pack

idea
= 只有模糊想法，先 aisee:srs

requirement-ready
= 已有 SRS，但缺 UI/device/tech context

context-ready
= SRS + UI/device + tech context 已具备，可以 change-plan

change-planned
= 已有 change-plan，但还没生成 OpenSpec artifacts

change-authored
= 已有 OpenSpec change artifacts，但未审核/未 validate

doc-reviewed
= CE 文档审核已完成，P0/P1 已处理或接受

implementation-ready
= validate 通过，当前 schema apply tracks 和 Affected Paths Index / implementation references 足够清楚，可以 ce-work

implemented
= 代码已完成，等待 review/test/verify

verified
= review/test/verify 通过，等待 archive-guard

archive-ready
= 可以 openspec archive
```

### aisee:change-author

把 `aisee:change-plan` 的结果转成 OpenSpec change artifacts 初稿。

它是 OpenSpec change 产物编排器。它应读取 schema，判断需要哪些 artifacts，再按 schema 模板直接生成或补齐：

```text
change-context.md
  -> app architecture context author

design.md
  -> 仅当当前 schema 明确包含 design.md 时按 schema 模板直接补齐

ui-contract.md / service-contract.md / data-model.md
  -> app domain author

hardware-contract.md / firmware-contract.md / runtime-contract.md / verification-contract.md
  -> device domain author

source-map.md
  -> sources / ID trace / OpenSpec artifacts
```

它应通过 `aisee CLI` 查询上游 ID 和上下文：

```bash
aisee change inspect <change> --json
aisee get <id> --json
aisee trace <id> --json
```

App/Web 常见 artifacts：

```text
proposal.md
source-map.md
specs/**/*.md
tasks.md
change-context.md    # Required=yes 时
ui-contract.md       # Required=yes 时
service-contract.md  # Required=yes 时
data-model.md        # Required=yes 时
```

硬件/嵌入式常见 artifacts：

```text
proposal.md
design.md
spec.md
tasks.md
source-map.md
hardware-contract.md
firmware-contract.md
runtime-contract.md
verification-contract.md
```

### aisee:implementation-bridge

连接 OpenSpec change 与 Compound Engineering。

输入应是单个已确认 OpenSpec change，输出给 `ce-work` 或按需 `ce-plan` 的工程上下文：

- 当前 change 目标。
- 当前 schema 生成的相关 artifacts。
- 当前 schema 的 apply tracks（常见是 `tasks.md`，无 apply schema 可为 N/A）。
- `source-map.md`（仅当前 schema 生成时）。
- schema/domain 约束。
- 测试要求。
- 禁止越界项。

该 skill 的核心价值是避免 `aisee:change-plan` 和 `compound plan` 在同一层级重复规划。

推荐由 Aisee CLI 生成最小上下文包：

```bash
aisee context pack --change <change> --for ce-work --json
```

输出应包含执行规则：

```text
- OpenSpec change 是事实源。
- 当前 schema artifacts 是本 change 的规范事实。
- 当前 schema apply tracks 是唯一长期执行清单；常见是 tasks.md，无 apply schema 可为 N/A。
- source-map.md 只在当前 schema 生成时作为代码定位和追踪入口；不生成 source-map 的 schema 使用当前 artifacts / apply tracks 的显式路径引用。
- 不创建平行 plan 文档。
- 如果实现发现需求/spec 不一致，先回写当前 OpenSpec change。
```

### aisee:verify

统一验证入口。

职责：

- 运行或建议运行 `openspec validate`。
- 检查 schema artifact DAG。
- 检查 `spec`、`source-map`、`tasks`、contract artifacts 的一致性。
- 检查实现后是否出现 spec drift。
- 按 domain 推荐最小验证集。
- 消费 `ce-doc-review`、`ce-code-review`、`ce-test-*` 的结果，检查 P0/P1 是否处理或记录接受理由。

推荐 CLI 输入：

```bash
aisee gaps --change <change> --json
aisee context pack --change <change> --for aisee-verify --json
```

### aisee:archive-guard

OpenSpec archive 前的守门 skill。

职责：

- 检查 change 是否完成。
- 检查 tasks 是否关闭。
- 检查实现是否偏离 source-map。
- 检查 spec 是否同步。
- 检查验证记录是否满足 schema/domain 要求。
- 给出是否可以执行 `openspec archive` 的结论。

它不替代 `openspec archive`，只判断 archive 前是否具备条件。

它不应重复 `ce-work` 或 `ce-code-review`。它只读取已有结果，输出短结论：

```text
结论：可以 archive / 暂不建议 archive
阻断项：
- ...
依据：
- openspec validate 结果
- tasks.md 完成状态
- review / test / verification 记录
```

## Compound Engineering Handoff 规则

每个 aisee skill 不应硬编码完整 CE 流程，而应在输出中提供统一交接块：

```md
## Next Recommended Gate

- Gate: `compound-doc-review | compound-work | compound-code-review | none`
- Reason:
- Required input:
- Output must be recorded at:
- Must write back to:
```

推荐交接点：

```text
aisee:srs
  -> 可选 ce-doc-review，审核需求完整性、冲突和可验证性

aisee:ui-content
  -> 可选 ce-doc-review，审核页面状态、权限、异常流和跨页面流程

aisee:architecture / aisee:device-context
  -> 可选 ce-doc-review，审核技术约束、硬件/固件/运行时约束缺口

aisee:change-plan
  -> 通常不使用 ce-plan；可选 ce-doc-review 审查 change 拆分是否合理

aisee:change-author
  -> 强烈建议 ce-doc-review，审核当前 schema artifacts、apply tracks、contracts 和 source-map（如适用）一致性

aisee:implementation-bridge
  -> ce-work；apply tracks 或 Affected Paths Index / implementation references 不清楚时，才按需 ce-plan 并回写

aisee:verify
  -> 消费 CE review/test/debug 结果

aisee:archive-guard
  -> 消费 CE 结果，判断是否可 archive
```

CE 输出归档规则：

```text
ce-doc-review
  -> docs/reviews/<change-id>-doc-review.md
  -> findings 需要长期保留时回写 owner 文档

ce-work
  -> 修改代码和必要的 tasks/verification 记录
  -> 不长期保存平行任务清单

ce-code-review
  -> docs/reviews/<change-id>-code-review.md 或 PR review
  -> P0/P1 必须处理或记录接受理由

ce-debug
  -> 可写入 verification record 或 implementation note
  -> 影响规范时回写 OpenSpec change
```

## 建议新增的 Agent

如果 agent 指 `agents/openai.yaml` 这类 UI 元数据，应为主要 skill 都补齐：

```text
aisee:flow
aisee:init
aisee-schema-pack
aisee:srs
aisee:ui-content
aisee:architecture
aisee:device-context
aisee:change-plan
aisee:change-author
aisee:implementation-bridge
aisee:verify
aisee:archive-guard
aisee:spec-migrate
aisee:reflect
aisee:design-assets
aisee:svg-assets
aisee:image-object
```

如果 agent 指专职子代理，建议只新增三个：

### aisee-change-architect

审查 change 边界、依赖关系、粒度和可独立交付性。

### aisee-spec-reviewer

审查 OpenSpec artifacts 是否完整、一致、可验证，是否符合 schema。

### aisee-implementation-reviewer

实现后比对代码、tasks、source-map、spec 和验证记录，判断是否可进入 archive。

## App/Web 与硬件/嵌入式的冲突风险

硬件/嵌入式不能直接套 App/Web 链路。主要冲突包括：

### UI content vs hardware contract

App/Web 需要页面、入口、表单、权限可见性；硬件/嵌入式需要芯片、引脚、外设、总线、电源、时钟、板级约束和硬件版本兼容。

### service/data contract vs firmware/runtime contract

Web 后端关注 API、数据库、权限、队列、缓存；嵌入式关注驱动、中断、协议栈、任务调度、Flash/RAM、功耗、实时性和看门狗。

### 常规测试 vs verification contract

软件项目通常依赖 unit/integration/e2e；硬件/嵌入式还需要 HIL、台架测试、仪器测试、仿真、烧录验证、硬件版本矩阵、量产测试记录。

### archive 时机

纯软件 change 可能代码测试通过即可 archive；硬件/嵌入式 change 还要考虑样机版本、板级验证、固件版本、生产测试和回归记录。

## 领域分层

推荐把 aisee 拆成通用内核和领域适配层。

```text
aisee-core
  init
  schema-pack
  srs
  architecture
  change-plan
  change-author
  verify
  archive-guard
  reflect

aisee-app
  ui-content
  app schema
  service-contract
  data-model
  frontend bridge

aisee-device
  device-context
  hardware-contract
  firmware-contract
  runtime-contract
  verification-contract
  device schema
  bench-test bridge
```

## Domain 路由规则

`aisee:flow` 启动时应先判定 domain：

```text
app:
  有页面、用户流程、管理后台、App、小程序、H5、权限可见性、表单、列表等信号。

device:
  有 MCU、传感器、执行器、外设、RTOS、固件、PCB、功耗、协议、驱动、烧录、台架测试等信号。

docsite:
  有文档站、知识库、内容结构、导航、文档迁移等信号。

infra:
  有部署、云资源、网络、权限策略、CI/CD、运维、迁移、回滚等信号。

security:
  有威胁建模、权限、审计、漏洞、加密、合规、访问控制等信号。

auto:
  信号不足时先询问，不默认套 app。
```

## Schema 选择规则

`aisee:change-plan` 应按 domain 选择 schema：

```text
app      -> aisee-app-spec-driven
device   -> aisee-device-spec-driven
docsite  -> aisee-docsite-driven
infra    -> infra-change
security -> security-audit
research -> quick-research
quickfix -> quick-fix
collab   -> opsx-collab-pr-loop
```

## ID、Source Map 与 Context Pack

为了避免重复文档和上下文漂移，长期产物必须通过稳定 ID 关联。当前 schema 生成 `source-map.md` 时，再用 source-map 记录 change 级追踪关系；不生成 source-map 的 schema 不能为了关联而补假文件。

Aisee CLI 的 JSON 输出应调用时解析，不维护第二份内容数据：

```text
aisee/docs/**/*.md / openspec/**/*.md
= Aisee 上游产物与 OpenSpec 内容事实源

aisee/registry/id-registry.json
= ID 分配和生命周期事实源

aisee/registry/sources.json
= change 外部 Aisee 产物的来源登记事实源

aisee/cache/context-index.json
= 可删除、可重建的解析缓存，不是事实源
```

SRS、UI content、architecture、device-context 等不在 OpenSpec change 目录内，不能只靠 change schema 发现。必须通过 `aisee/registry/sources.json` 登记；当前 schema 生成 `source-map.md` 时，再通过 source-map 衔接到具体 change：

```text
aisee/registry/sources.json
= 项目级来源登记，知道所有 Aisee 上游产物在哪里

openspec/changes/<change>/source-map.md
= change 级追踪关系；仅当前 schema 生成 source-map 时存在
```

### ID 规则

完整 ID 使用：

```text
<scope>:<TYPE>-<number>
```

示例：

```text
auth:FR-001
auth:PAGE-001
payment:FR-001
device-sampling:HW-001
device-sampling:FW-001
```

人类文档可以显示短 ID，但机器索引用完整 ID：

```md
### FR-001 用户登录
<!-- aisee:id auth:FR-001 -->
```

ID 分配和生命周期由 `aisee/registry/id-registry.json` 管理，禁止人工或 AI 随手编新编号。Aisee CLI 负责：

```bash
aisee id reserve --scope auth --type FR --count 3 --json
aisee id activate auth:FR-005 --owner aisee/docs/requirements/auth-srs.md --title "用户扫码登录"
aisee id check --json
```

### Source Map 规则

`source-map.md` 是 OpenSpec change 内的上下文路由表，负责连接：

```text
SRS / UI Content / Architecture / Device Context
  -> OpenSpec artifacts
  -> tasks
  -> code paths
  -> tests / verification
  -> CE review records
```

示例：

```text
auth:FR-001
  -> auth:PAGE-001
  -> change:add-auth-login
  -> auth:SPEC-001
  -> auth:TASK-002
  -> src/auth/session.ts
  -> tests/auth/session.test.ts
```

### Context Pack 规则

不同 skill 不应自行通读全部文档，而应优先使用 Aisee CLI 生成目标上下文包：

```bash
aisee context pack --change <change> --for ce-doc-review --json
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for ce-code-review --json
aisee context pack --change <change> --for aisee-verify --json
```

这让 Aisee skill 和 CE skill 都消费同一个结构化上下文，减少复制、遗漏和误读。

字段级契约见 `references/context-pack-contract.md`。核心约束：

- `--change` 是唯一入口。
- `facts.parsed` 来自当前文件和模板直接解析。
- `facts.derived` 来自 source-map、ID registry、schema DAG 和文件关系推导。
- `generated` 默认为空；显式 `--with-summary` 才允许出现。
- `ce-work` 只消费当前 change 的实现上下文，不能自由扩大范围。
- source-map schema 的执行路径优先来自 `Affected Paths Index`；缺表时只允许 source-map metadata fallback 并保留 risk。
- `aisee-verify` 可诊断 drift 和 evidence 缺口，但不做 archive 放行审批。

## 推荐端到端流程

### App/Web

```text
aisee:flow
  ↓ 判定 domain = app
aisee:srs
  ↓
aisee:ui-content
  ↓
aisee:architecture
  ↓
aisee:change-plan --schema aisee-app-spec-driven
  ↓
aisee:change-author
  ↓
openspec validate
  ↓
aisee:implementation-bridge
  ↓
compound plan / work / review / test
  ↓
aisee:verify
  ↓
aisee:archive-guard
  ↓
openspec archive
```

### 硬件/嵌入式

```text
aisee:flow
  ↓ 判定 domain = device
aisee:srs
  ↓
aisee:device-context
  ↓
aisee:change-plan --schema aisee-device-spec-driven
  ↓
aisee:change-author
  ↓
hardware-contract.md
firmware-contract.md
runtime-contract.md
verification-contract.md
  ↓
openspec validate
  ↓
aisee:implementation-bridge 或 bench-test bridge
  ↓
compound plan / work / review / test
  ↓
aisee:verify
  ↓
aisee:archive-guard
  ↓
openspec archive
```

## 冲突治理规则

- `aisee:change-plan` 只规划 OpenSpec change 边界，不规划具体代码修改。
- `compound plan / ce-plan` 只作为可选任务细化器，不作为长期任务事实源。
- 当前 schema 的 apply tracks 是唯一长期执行清单；常见是 `tasks.md`，但不是所有 schema 都需要 tasks。
- `ce-work` 的依据是单个 OpenSpec change 工程包。
- OpenSpec `archive` 只在 change 已实现、已验证、spec 与代码一致后执行。
- Compound 不直接修改 baseline spec。
- 实现中发现需求变化，必须回写当前 OpenSpec change，再重新 validate。
- App/Web 不默认生成硬件 contract。
- 硬件/嵌入式不默认生成 UI content。
- `aisee:flow` 在 domain 不明确时应先询问，而不是默认走 app。
- 每个 schema 决定自己的 artifact 集合、验证规则和 archive guard 检查表。
- ID 必须通过 `aisee/registry/id-registry.json` 分配和校验。
- 当前 schema 生成 `source-map.md` 时，跨文档关系优先写入 `source-map.md`；不生成 source-map 的 schema 不应补假 source-map。

## 推荐落地里程碑

### V0：Aisee CLI 原型

- 新增 `aisee doctor --json`。
- 新增 `aisee bootstrap --plan`。
- 新增 `aisee/registry/id-registry.json`。
- 新增 `aisee id reserve / activate / check`。
- 新增 `aisee index / get / trace` 的只读原型。

### V1：插件化

- 创建 `aisee-plugin`。
- 添加 `.codex-plugin/plugin.json`。
- 把现有 `aisee*` skill 纳入插件目录。
- 补齐主要 skill 的 `agents/openai.yaml`。
- 增加 `references/compound-bridge.md`、`references/context-pack-contract.md`、`references/id-policy.md`。
- 验证插件可被 Codex 加载。

### V2：Workflow State Orchestrator

- 新增 `aisee:flow`，定位为 workflow state orchestrator，而不是简单路由器。
- 不再合并 `aisee:init` 与 `aisee-schema-pack`；二者保持独立，避免形成弱入口 skill。
- 明确 domain 路由规则。
- 明确 workflow stage、状态卡格式和跳步拦截规则。
- `aisee:flow` 优先调用 Aisee CLI 获取 doctor/index/gaps/context pack 结果。
- `aisee:flow` 只给 domain/schema family hint；per-change schema 由 `aisee:change-plan` 决定。

### V3：OpenSpec Authoring

- 新增 `aisee:change-author`。
- 删除独立 `aisee:change-design`，由 `aisee:change-author` 在 schema 明确生成 `design.md` 时直接按模板补齐。
- 按 schema 生成 artifacts 初稿。
- 增加 artifact DAG 和 source-map 检查。
- 要求所有上游引用通过 ID 和 source-map 串联。

### V4：Compound Bridge

- 新增 `aisee:implementation-bridge`。
- 新增 `aisee context pack --change <change> --for ce-work --json`。
- 约束 Compound 只处理单个 OpenSpec change 的文档审核、工程实现和代码审核。
- 输出明确的工程上下文和禁止越界项。
- `ce-plan` 仅在当前 schema apply tracks 或实现路径不足时按需使用，并把结论回写当前 schema artifacts；仅 source-map schema 需要回写 `source-map.md`。

### V5：验证与 Archive 守门

- 新增 `aisee:verify`。
- 新增 `aisee:archive-guard`。
- 针对 App/Web 与硬件/嵌入式分别建立检查表。
- 消费 CE review/test/debug 结果，不重复执行 CE 的工作。

### V6：Assets 与多 domain 扩展

- 不新增独立资产入口 skill。
- 保留 `aisee:design-assets`、`aisee:svg-assets`、`aisee:image-object` 作为专业 skill。
- 用当前 schema 的相关 artifacts 引用视觉资产产物；app schema 通常通过 `ui-contract.md`、`source-map.md` 和 `tasks.md` 串联。
- 补齐 device/docsite/infra/security 的 context pack 与 archive-guard 检查表。

## 最终建议

不要把 Aisee、OpenSpec、Compound Engineering 融成一个没有边界的超级系统。更稳妥的结构是：

```text
Aisee 插件化
  + OpenSpec schema/status 作为权威规范层
  + Compound Engineering 作为实现执行层
  + domain adapter 区分 App/Web、硬件/嵌入式、文档、基础设施、安全
```

这样可以同时支持软件产品和硬件/嵌入式开发，并避免需求规划、规范状态和工程实现三者互相覆盖。
