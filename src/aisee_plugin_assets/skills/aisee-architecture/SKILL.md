---
name: aisee:architecture
description: 在 aisee:change-plan 之前生成软件项目技术架构文档，提取 App、小程序、Web、桌面、后端/API、CLI、Job、集成、数据和设备协作软件场景的技术栈状态、架构概览、全局工程约定、架构决策、现有边界、可复用能力、共享技术前置、技术耦合点、平台限制、技术风险和 schema artifact hints。用于用户要求“做架构”“生成架构文档”“分析技术架构”“补技术约束”“change-plan 前看技术边界”“现有项目技术栈扫描”“判断技术栈是否已定”“为规划 change 边界提供技术输入”时触发。不要用于规划 change 边界、命名 change、做技术选型、写 API/DB/CLI/Job 详细契约、硬件/固件设计或实现方案。
---

# aisee:architecture — 技术架构文档

在 `aisee:change-plan` 前运行，给 change 边界规划提供软件项目的技术事实、架构概览、全局工程约定、架构决策、约束、缺口和 schema artifact hints。它不拆 change，不生成 change 名称，不安排阶段，不写具体契约或实现方案。

当前主流程面向 App、小程序、Web、桌面、后端/API、CLI、Job、集成、数据和设备协作软件。纯硬件、嵌入式、固件、RTOS、驱动、板级 bring-up、PCB、BOM 或制造相关架构后续按专用硬件流程整理；本 skill 只记录软件侧需要知道的设备协作约束。

## 输入

用户提供以下任意一种输入：

- `aisee:srs` 输出的 SRS 文件
- `aisee:ui-content` 输出的 UI 内容规格
- `aisee:design-spec` 输出的设计规范
- 已确认需求文本
- 既有项目目录、代码、配置或架构文档
- `openspec/project.md`、OpenSpec baseline specs 或 active change artifacts

可选参数：

- `--scope project|feature|auto` — 技术架构范围，默认 `auto`
- `--domain app|web|mini-program|desktop|backend-service|cli-tool|job-async|integration|data|hybrid-software|auto` — 软件技术域，默认 `auto`
- `--mode scan|synthesize|auto` — 扫描现有项目或汇总用户提供材料，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

## 输出边界

`aisee:architecture` 只输出技术架构文档、全局工程约定、schema artifact hints 和 `aisee:change-plan` 输入提示。

必须覆盖：

- 技术域识别：App / Web / 小程序 / 桌面 / 后端服务 / CLI / Job / 集成 / 数据 / 设备协作软件
- 项目级技术栈状态：已确定 / 部分确定 / 未确定
- 技术栈来源与可信度
- 架构概览：系统分层、主要运行单元、端 / 服务 / 设备协作关系
- 全局工程约定：已有约定或待决策缺口，不创造新契约
- 架构决策：已确认决策、待确认决策、禁止假设的内容
- 现有架构边界、模块边界和可复用能力
- 共享技术前置、技术耦合点、平台 / 运行环境能力限制
- 按需 Domain Context Blocks：Frontend、Backend、CLI、Job、Integration、Data、Verification、Device Collaboration
- Schema Artifact Hints：只提示后续契约类型，不绑定具体 schema 文件名
- 技术风险、阻塞决策和给 `aisee:change-plan` 的技术提示

禁止输出：

- change 边界规划方案、change 名称、phase / dependency graph 或 `/opsx:*` 命令
- `design.md` 内容
- 技术栈选型结论；缺失时只能标注 `[STACK-CONTEXT-MISSING]` / `[STACK-DECISION-REQUIRED]`
- 数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 调度/重试详细契约、ORM 代码或实现计划
- 引脚表、寄存器表、时序表、RTOS 任务设计、驱动结构、固件实现步骤、BOM、PCB 布局或制造工艺
- 当前 schema 一定存在某个 artifact 文件名的断言

## ID 规则

`aisee:architecture` 负责架构侧上游 ID：

- `ARCH`：架构边界、架构上下文项、系统分层或运行单元
- `DEC`：已确认或局部待确认的架构决策
- `CONSTRAINT`：技术约束、平台约束、集成约束、运行环境限制
- `RISK`：技术风险、阻塞项、冲突或需要验证的风险

正式 ID 必须来自 `aisee/registry/id-registry.json`。新增架构项前，使用：

```bash
aisee id reserve --scope <scope> --type ARCH --count <N> --json
aisee id reserve --scope <scope> --type DEC --count <N> --json
aisee id reserve --scope <scope> --type CONSTRAINT --count <N> --json
aisee id reserve --scope <scope> --type RISK --count <N> --json
```

写入文档后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活；交付前运行或建议运行 `aisee id check --json`。

如果 Aisee CLI 或 ID registry 不可用，只能使用临时占位符，例如 `{{scope}}:DEC-NEW-001`，并在文档 ID 状态中标注 `[ID-RESERVATION-REQUIRED]`。不要声称占位符是正式 ID。

Architecture 不负责 `API / DATA / TASK / TEST`，也不负责 UI 的 `PAGE` 分配。它只输出后续 `change-context.md` 或 change artifacts 可以引用的架构 ID。

## Phase 0 — 读取输入与项目上下文

先读取用户提供的输入文件或文本。若路径不存在，停止并说明。

静默收集软件项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -160
cat aisee/registry/id-registry.json 2>/dev/null || true
rg --files | rg '(^|/)(package\.json|pnpm-lock\.yaml|yarn\.lock|package-lock\.json|pyproject\.toml|requirements\.txt|Gemfile|go\.mod|Cargo\.toml|pom\.xml|build\.gradle|composer\.json|schema\.sql|openapi\.ya?ml|openapi\.json)$|(^|/)(prisma|drizzle|migrations)(/|$)' | head -80
rg --files docs aisee/docs openspec 2>/dev/null | rg '(architecture|tech|stack|design|api|schema)' | head -80
rg --files openspec/specs openspec/changes 2>/dev/null | head -80
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查架构分析需要的文件类型。

只读与输入需求相关的目录和文件。查找路由、页面、控制器、服务、模型、schema、migration、API contract、权限中间件、任务队列、测试目录和既有架构文档。不要因为文件名猜测项目事实；关键结论必须标注来源。

当涉及具体框架、SDK、ORM、数据库、云服务、API、CLI 或工具链用法判断时，优先读取项目文件、锁文件、配置、测试和已有架构文档；需要判断当前官方用法、版本能力或兼容性时，使用 Context7 或官方文档。若无法查证，不得写成架构事实；标注 `[STACK-CONTEXT-MISSING]`、`[DOC-CONTEXT-MISSING]` 或 `[ARCH-DECISION-REQUIRED]`，并写明需要补充的来源。

CHECKPOINT: 生成或写入 Architecture 前，必须确认或显式标注技术域、技术栈状态、主要来源、现有架构边界、平台/运行环境约束、集成/数据/权限/任务等相关 domain block、阻塞风险、待确认架构决策和 ID 状态。技术栈、架构决策或平台约束会影响 change-plan 时，先暂停让用户确认；用户要求继续但证据不足时，只能写缺口标签和 Open Questions，不得把推断写成既定架构。

## Workflow

先按 Phase 0 读取项目上下文，再按需读取 [workflow.md](references/workflow.md) 执行技术域判断、技术事实提取、架构提示生成、文档生成和保存。

Reference loading：

- 需要追问时读取 `references/question-bank.md`。
- 生成前读取 `assets/architecture-template.md` 入口索引和 `references/writing-rules.md`。
- 每次生成都读取 `assets/architecture-template-core.md` 和 `assets/architecture-template-artifact-hints.md`。
- 软件主流程读取 `assets/architecture-template-software.md`。
- 不读取 `assets/architecture-template-embedded.md`，除非用户明确要求临时审查历史硬件模板；纯硬件/嵌入式/固件架构进入后续专用流程。

## Guardrails

- 不要规划 change 边界，不要命名 change，不要输出 phase 或依赖图。
- 不要生成 `/opsx:new`、`/opsx:propose` 或其他执行命令。
- 不要生成 `design.md`。
- 不要做技术选型；技术栈缺失时标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`。
- 不要靠记忆判断框架、SDK、CLI、云服务或数据库能力；项目来源和官方文档都不可用时标注 `[DOC-CONTEXT-MISSING]`。
- 不要把推断写成事实；每条关键技术事实都要有来源和可信度。
- 不要把待确认架构决策写成已确认结论；没有来源时标注 `[ARCH-DECISION-REQUIRED]`、阻塞或 Open Question。
- 不要输出数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 详细调度策略、ORM 代码或实现步骤。
- 不要输出硬件架构、固件设计、引脚、寄存器、RTOS 任务、驱动结构、BOM、PCB 或制造细节。
- 不要把建议 artifact 类型写死为当前 schema 的固定文件名；schema pack 未来可调整。
- 如果发现需求与现有技术约束冲突，标注 `[SPEC-GAP]` 或 `[STACK-CONFLICT]`，不要静默绕过。
- 给 `aisee:change-plan` 的技术提示只能是事实、约束和原因，不是边界规划结果。
- 正式 `ARCH / DEC / CONSTRAINT / RISK` ID 必须来自 ID registry；工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 并标注 `[ID-RESERVATION-REQUIRED]`。

## 与 OpenSpec 工作流集成

```text
aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:design-spec        ← UI 设计规范事实源（UI 型需求可选）
  ├─ aisee:architecture       ← 本技能：change-plan 前软件技术架构事实、决策与约束
  └─ aisee:change-plan              ← 基于 SRS + UI content + design-spec + architecture 拆 change
       └─ /opsx:new <change>
            └─ aisee:change-author
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```
