---
name: hw:change-plan
description: 将已确认的硬件 SRS、整体架构、工程事实和模块文档映射为可独立交付的 OpenSpec changes。用于规划硬件/嵌入式项目的 change 边界、依赖顺序、并行关系、aisee-device-spec-driven schema、source-map seed 和 /opsx:new 命令；不重新做需求、不重新做整体架构、不写实现代码。触发词包括“硬件change拆分”“硬件实施计划”“拆OpenSpec change”“source-map seed”“hw:change-plan”。
---

# hw:change-plan

把硬件整体输入拆成多个可执行的 OpenSpec changes。每个 change 应使用 `aisee-device-spec-driven`，除非用户明确选择其他 schema。

本技能参考 `aisee:change-plan` 的边界规划方式，但针对硬件/嵌入式项目增加 HW / FW / RT / VER 追踪。

## Inputs

必需：
- `docs/requirements/*-hw-srs.md`
- `docs/architecture/*-hw-architecture.md`

可选：
- `docs/modules/*.md`
- `docs/project-structure.md`
- `docs/clock-contract.md`
- `docs/memory-device-contract.md`
- `hw:init scan-existing` 的只读扫描摘要
- 现有 OpenSpec active changes

可选参数：
- `--strategy vertical|risk|parallel`，默认 `vertical`
- `--granularity fine|medium|coarse`，默认 `medium`
- `--schema <name>`，默认 `aisee-device-spec-driven`
- `--max-changes <N>`，默认 `8`
- `--single-if-small`

## References

需要拆分规则时读取：

`references/change-boundary-rules.md`

生成文档时读取：

`assets/change-plan-template.md`

## Output

保存到：

`docs/change-plan/<YYYY-MM-DD>-<slug>-hw-change-plan.md`

输出必须包含：
- Summary
- Dependency graph
- Change details
- 每个 change 的 schema，默认 `aisee-device-spec-driven`
- 每个 change 的 In Scope / Out of Scope
- 每个 change 的 Source-map seed：FR / HW / FW / RT / VER
- 每个 contract artifact 的适用性：hardware / firmware / runtime / verification
- Depends on / Parallel with
- Change rationale
- Copy-ready `/opsx:new "<change>" --schema aisee-device-spec-driven` 命令
- 整体拆分依据和 `[ASSUMPTION]` / `[RISK]` / `[ARCH-BLOCKER]`

## Phase 0 - Read Project Context

PowerShell:

```powershell
Get-Content -ErrorAction Stop docs/requirements/*-hw-srs.md
Get-Content -ErrorAction Stop docs/architecture/*-hw-architecture.md
Get-Content -ErrorAction SilentlyContinue docs/modules/*.md
Get-Content -ErrorAction SilentlyContinue docs/project-structure.md
Get-Content -ErrorAction SilentlyContinue docs/clock-contract.md
Get-Content -ErrorAction SilentlyContinue docs/memory-device-contract.md
cmd /c openspec list --json 2>nul
cmd /c openspec schemas --json 2>nul
```

POSIX shell:

```bash
cat docs/requirements/*-hw-srs.md
cat docs/architecture/*-hw-architecture.md
cat docs/modules/*.md 2>/dev/null
cat docs/project-structure.md 2>/dev/null
cat docs/clock-contract.md 2>/dev/null
cat docs/memory-device-contract.md 2>/dev/null
openspec list --json 2>/dev/null
openspec schemas --json 2>/dev/null
```

如果缺少 SRS，停止并输出 `[SRS-REQUIRED]`。
如果缺少 architecture，停止并输出 `[ARCHITECTURE-REQUIRED]`。
如果目标项目没有安装 `aisee-device-spec-driven` schema，停止并输出 `[SCHEMA-REQUIRED]`，提示先安装 schema pack；不要输出不可执行的 `/opsx:new --schema aisee-device-spec-driven` 命令。

## Phase 1 - Input Mode Detection

启用硬件输入模式，当文档中存在：
- `FR-xxx` functional requirements
- `HW-xxx` hardware resource/constraint
- `FW-xxx` firmware/module/interface
- `RT-xxx` runtime/timing/memory
- `VER-xxx` verification item
- “Change-Plan Hints” 或 “Change Candidate List”

使用这些 ID 作为 canonical units，不要重新发明编号。

## Phase 2 - Clarify Only When Needed

最多问 2 个问题，只在以下情况追问：
- 一个 FR 跨多个互斥硬件方案，无法决定 change 边界
- 架构文档存在 `[ARCH-BLOCKER]` 或 `[BUDGET-FAIL]`
- 不清楚某个模块是否必须先完成才能让其他 change 独立推进

否则记录 `[ASSUMPTION]` 并继续。

## Phase 3 - Apply Hardware Change Boundary Rules

读取 `references/change-boundary-rules.md`。

核心规则：
- 如果缺少可构建工程、项目目录结构、构建入口、工具链工程文件、`docs/project-structure.md`、`docs/clock-contract.md` 或 `docs/memory-device-contract.md`，第一个 change 必须是 `initialize-hardware-project`。
- `initialize-hardware-project` 必须在 implementation helper 中注明：Use `hw:init generate-skeleton` during `/opsx:apply`.
- 每个 change 合并后项目应保持可构建、可烧录或至少不破坏已有工作路径。
- 避免按文件类型拆分；优先按可验证的硬件/固件能力拆分。
- 全局资源或契约先行：基础工程、时钟/存储契约、硬件资源冻结可作为早期 prerequisite。
- 一个 change 应有明确 owner 领域：硬件资源、驱动、算法、显示、通信、验证等。
- 不能把同一状态机拆到多个互相依赖不清的 change。
- 高风险算法、库、硬件链路可以先规划 spike，但必须写明非生产范围。
- 默认不超过 8 个 changes；超过则提示这是 epic，需要再分层规划。

## Phase 3.5 - Initialization Change Rule

如果满足任一条件，必须把 `initialize-hardware-project` 作为 Phase 1 第一个 change：
- 新项目没有可构建工程。
- 需要按 `Drivers + Core + Function` 或 architecture 确认的模板创建目录。
- 需要引入或引用厂商库 / SDK。
- 需要创建或整理 Keil / IAR / CMake / Makefile 工程。
- 需要生成 `docs/project-structure.md`。
- 需要生成 `docs/clock-contract.md`。
- 需要生成 `docs/memory-device-contract.md`。
- 后续 changes 依赖工程目录、构建命令、时钟或存储契约。

`initialize-hardware-project` 的范围必须限于：
- 创建/整理目录结构。
- 建立工程文件和构建入口。
- 建立 `Drivers + Core + Function` 或已确认目录语义。
- 生成项目结构、时钟、存储/型号契约。
- 验证最小构建、打开工程或烧录链路。

不得包含业务功能、算法、显示、采样、通信协议等后续能力实现。

## Phase 4 - Source-map Seed Rules

每个 planned change 必须包含：
- `FR`: 来自 SRS
- `HW`: 来自 architecture 或 `TBD in hardware-contract`
- `FW`: 来自 architecture/module docs 或 `TBD in firmware-contract`
- `RT`: 来自 architecture/init contracts 或 `TBD in runtime-contract`
- `VER`: 来自 architecture 或 `TBD in verification-contract`

Artifact applicability 必须写明：
- `hardware-contract.md`: yes/no — reason
- `firmware-contract.md`: yes/no — reason
- `runtime-contract.md`: yes/no — reason
- `verification-contract.md`: yes — reason，通常必须适用

## Phase 5 - Generate And Save

读取 `assets/change-plan-template.md`，生成 change plan 并保存。

同时输出 copy-ready commands。

## Guardrails

- 不重新做需求；需求缺口回到 `hw:srs`。
- 不重新做整体架构；架构缺口回到 `hw:architecture`。
- 不创建 OpenSpec change；只输出 `/opsx:new` 命令。
- 不写 `tasks.md`；任务由每个 OpenSpec change 的 schema artifact 生成。
- 不把没有 source-map seed 的 change 输出为可执行 change。
- 如果需要初始化却没有输出 `initialize-hardware-project`，这是规划错误。
- OpenSpec schema 默认使用 `aisee-device-spec-driven`。

## Next

按 dependency graph 创建 changes：

```text
/opsx:new "<change-name>" --schema aisee-device-spec-driven
/opsx:continue <change-name>
...
/opsx:apply <change-name>
/opsx:verify <change-name>
/opsx:archive <change-name>
```
