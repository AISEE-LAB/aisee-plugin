---
name: aisee:architecture
description: 在 aisee:change-plan 之前生成跨工程域技术架构文档，提取软件、Web、后端、CLI、Job、集成、数据、硬件、嵌入式、固件、RTOS、驱动等场景的技术栈/工具链状态、架构概览、全局工程约定、架构决策、现有架构边界、可复用能力、共享技术前置、技术耦合点、运行环境限制、技术风险和 schema artifact hints。用于用户要求“做架构”“生成架构文档”“分析技术架构”“补技术约束”“change-plan 前看技术边界”“现有项目技术栈扫描”“生成 architecture/tech-context”“判断技术栈/工具链是否已定”“为规划 change 边界提供技术输入”时触发。不要用于规划 change 边界、命名 change、做技术选型、写 API/DB/CLI/Job/硬件/固件详细契约或实现方案。
---

# aisee:architecture — 技术架构文档

在 `aisee:change-plan` 前运行，给 change 边界规划提供跨工程域的技术事实、架构概览、全局工程约定、架构决策、约束、缺口和 schema artifact hints。它不拆 change，不生成 change 名称，不安排阶段，不写具体契约或实现方案。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 输出的 SRS 文件
- `aisee:ui-content` 输出的 UI 内容规格
- `aisee:design-spec` 输出的设计规范
- 已确认需求文本
- 既有项目目录
- `openspec/project.md` 或架构文档
- 硬件 / 嵌入式 / 固件 / 驱动 / RTOS / 工具链相关文档

可选参数：
- `--scope project|feature|auto` — 技术架构范围，默认 `auto`
- `--domain software|web|backend|cli|job|integration|data|hardware|embedded|firmware|rtos|driver|hybrid|auto` — 工程域，默认 `auto`
- `--mode scan|synthesize|auto` — 扫描现有项目或汇总用户提供材料，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:architecture` 只输出技术架构文档、全局工程约定、schema artifact hints 和 change-plan 输入提示。

必须覆盖：
- 技术域识别：software / web / backend / cli / job / integration / data / hardware / embedded / firmware / rtos / driver / hybrid
- 项目级技术栈 / 工具链状态：已确定 / 部分确定 / 未确定
- 技术栈 / 工具链来源与可信度
- 架构概览：系统分层、主要运行单元、端 / 服务 / 设备协作关系
- 全局工程约定：已有约定或待决策缺口，不创造新契约
- 架构决策：已确认决策、待确认决策、禁止假设的内容
- 现有架构边界和模块边界
- 已有可复用能力：鉴权、权限、数据访问、队列、缓存、文件、通知、审计、日志等
- 共享技术前置：多个 FR / 页面共同依赖的技术基础
- 技术耦合点：数据模型、权限、异步任务、外部集成、多端能力等
- 平台 / 端 / 板级 / 运行环境能力限制
- 按需 Domain Context Blocks：Web、Backend、CLI、Job、Integration、Data、Hardware、Firmware、RTOS、Driver、Verification 等
- Schema Artifact Hints：只提示后续契约类型，不绑定具体 schema 文件名
- 技术风险和阻塞决策
- 给 `aisee:change-plan` 的技术提示

禁止输出：
- change 边界规划方案
- change 名称
- phase / dependency graph
- `/opsx:new`、`/opsx:propose` 命令
- `design.md` 内容
- 数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 调度/重试详细契约、寄存器表、引脚表、时序表、ORM 代码或实现计划
- 技术栈选型结论；缺失时只能标注 `[STACK-CONTEXT-MISSING]` / `[STACK-DECISION-REQUIRED]`

---

## ID 规则

`aisee:architecture` 负责架构侧上游 ID：

- `ARCH`：架构边界、架构上下文项、系统分层或运行单元。
- `DEC`：已确认或局部待确认的架构决策。
- `CONSTRAINT`：技术约束、平台约束、集成约束、运行环境限制。
- `RISK`：技术风险、阻塞项、冲突或需要验证的风险。

正式 ID 必须来自 `aisee/registry/id-registry.json`。新增架构项前，使用：

```bash
aisee id reserve --scope <scope> --type ARCH --count <N> --json
aisee id reserve --scope <scope> --type DEC --count <N> --json
aisee id reserve --scope <scope> --type CONSTRAINT --count <N> --json
aisee id reserve --scope <scope> --type RISK --count <N> --json
```

写入文档后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活；交付前运行或建议运行 `aisee id check --json`。

如果 Aisee CLI 或 ID registry 不可用，只能使用临时占位符，例如 `{{scope}}:DEC-NEW-001`，并在文档 ID 状态中标注 `[ID-RESERVATION-REQUIRED]`。不要声称占位符是正式 ID。

Architecture 不负责 `API / DATA / TASK / TEST`，也不负责 UI 的 `PAGE` 分配。它只输出后续 `change-context.md` 可以引用的架构 ID。

---

## Phase 0 — 读取输入与项目上下文

先读取用户提供的输入文件或文本。若路径不存在，停止并说明。

静默收集项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -160
cat CLAUDE.md 2>/dev/null | head -80
cat aisee/registry/id-registry.json 2>/dev/null || true
find . -maxdepth 3 \( -name package.json -o -name pnpm-lock.yaml -o -name yarn.lock -o -name package-lock.json -o -name pyproject.toml -o -name requirements.txt -o -name Gemfile -o -name go.mod -o -name Cargo.toml -o -name pom.xml -o -name build.gradle -o -name composer.json -o -name prisma -o -name drizzle -o -name migrations -o -name schema.sql -o -name openapi.yaml -o -name openapi.json \) 2>/dev/null | head -80
find . -maxdepth 4 \( -iname 'CMakeLists.txt' -o -iname 'Makefile' -o -iname '*.ioc' -o -iname '*.dts' -o -iname '*.dtsi' -o -iname 'platformio.ini' -o -iname 'west.yml' -o -iname 'Kconfig' -o -iname '*.ld' -o -iname '*.sv' -o -iname '*.v' -o -iname '*.xdc' -o -iname '*.sdc' \) 2>/dev/null | head -80
find docs -maxdepth 3 \( -iname '*architecture*' -o -iname '*tech*' -o -iname '*stack*' -o -iname '*design*' -o -iname '*hardware*' -o -iname '*firmware*' -o -iname '*rtos*' -o -iname '*driver*' \) 2>/dev/null | head -80
```

如果是既有项目：
- 只读与输入需求相关的目录和文件
- 查找路由、页面、控制器、服务、模型、schema、migration、API contract、权限中间件、任务队列、测试目录
- 硬件 / 嵌入式项目还要查找板级配置、设备树、引脚/时钟/内存配置、启动文件、链接脚本、驱动、RTOS 配置、构建/烧录/调试工具链、验证目录
- 不要因为文件名猜测项目事实；关键结论必须标注来源

当涉及具体框架、SDK、ORM、数据库、云服务、API、RTOS、MCU SDK、驱动框架或工具链用法判断时，使用 Context7 获取当前官方文档；没有文档支撑时标注为假设。

---

## Phase 1 — 技术域与技术栈状态判断

先判断技术域：

| Domain | 适用场景 |
|--------|----------|
| software / web / backend | Web、App、小程序、桌面、后端服务、管理后台 |
| cli / job / integration / data | CLI 工具、异步任务、第三方集成、数据能力 |
| hardware / embedded / firmware / rtos / driver | 硬件、嵌入式、固件、RTOS、驱动、板级 bring-up |
| hybrid | 同时包含软件服务与硬件 / 固件 / 设备侧能力 |

再判断项目级技术栈 / 工具链状态：

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
- 硬件 / 嵌入式域：MCU/SoC/FPGA、板卡、RTOS/裸机/Linux、编译器、构建系统、烧录/调试工具、驱动框架、外设/总线、时钟/电源/内存、验证工具

---

## Phase 2 — 技术架构事实与决策提取

读取 `references/question-bank.md`，只追问会影响技术架构判断的问题。

提取并标注来源：
- 技术栈事实
- 架构概览：系统分层、运行单元、端 / 服务 / 设备协作关系
- 全局工程约定
- 已确认架构决策与待确认架构决策
- 禁止假设项：没有可信来源时不能替用户决定的架构内容
- 模块边界
- 数据模型现状
- 权限体系现状
- API / 路由 / 服务边界
- 异步任务、队列、定时任务、通知现状
- 外部集成现状
- CLI / 工具入口、输出格式和分发现状
- 硬件 / 固件 / RTOS / 驱动 / 外设 / 工具链现状
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
- Schema Artifact Hints：哪些后续契约类型需要承接，artifact 名称以 schema pack 为准
- 高风险区域：外部集成、迁移、权限、安全、性能

禁止写：
- “Change 1 / Change 2”
- change 名称
- 阶段依赖图
- 具体 `/opsx:*` 命令
- 最终 change 边界规划结论
- 具体 artifact 文件名必须存在的断言；schema 仍可能调整

---

## Phase 4 — 生成与保存文档

先读取 `assets/architecture-template.md` 入口索引，再按技术域读取必要模板；每次生成都必须同时读取 `references/writing-rules.md`。

始终读取：
- `assets/architecture-template-core.md`
- `assets/architecture-template-artifact-hints.md`
- `references/writing-rules.md`

按需读取：
- 软件域：`assets/architecture-template-software.md`
- 硬件 / 嵌入式域：`assets/architecture-template-embedded.md`
- 混合域：同时读取 software 与 embedded 模板

默认保存：

```bash
mkdir -p aisee/docs/architecture
```

文件：

`aisee/docs/architecture/<YYYY-MM-DD>-<slug>-architecture.md`

如果用户只要求分析，可以只在聊天中输出。

---

## 完成输出

完成后输出：

> 技术架构文档已生成：`aisee/docs/architecture/{filename}.md`
>
> 技术栈状态：已确定 / 部分确定 / 未确定
> 识别：{A} 个架构决策、{N} 个架构边界、{M} 个可复用能力、{K} 个共享技术前置、{R} 个风险、{Q} 个阻塞决策。
>
> 下一步：将本文档与 SRS、UI 内容规格、设计规范一起交给 `aisee:change-plan`。

若存在阻塞项：

> 存在技术架构阻塞项：{tags}
> 这些阻塞项会影响 change 边界规划，但本技能不会直接规划 change 边界。

---

## Guardrails

- 不要规划 change 边界，不要命名 change，不要输出 phase 或依赖图。
- 不要生成 `/opsx:new`、`/opsx:propose` 或其他执行命令。
- 不要生成 `design.md`。
- 不要做技术选型；技术栈缺失时标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`。
- 不要把推断写成事实；每条关键技术事实都要有来源和可信度。
- 不要把待确认架构决策写成已确认结论；没有来源时标注阻塞或 Open Question。
- 不要输出数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 详细调度策略、寄存器表、引脚表、时序表、ORM 代码或实现步骤。
- 不要把建议 artifact 类型写死为当前 schema 的固定文件名；schema pack 未来可调整。
- 如果发现需求与现有技术约束冲突，标注 `[SPEC-GAP]` 或 `[STACK-CONFLICT]`，不要静默绕过。
- 给 `aisee:change-plan` 的技术提示只能是事实、约束和原因，不是边界规划结果。
- 正式 ARCH / DEC / CONSTRAINT / RISK ID 必须来自 ID registry；工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 并标注 `[ID-RESERVATION-REQUIRED]`。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:design-spec        ← UI 设计规范事实源（UI 型需求可选）
  ├─ aisee:architecture       ← 本技能：change-plan 前技术架构事实、决策与约束
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
