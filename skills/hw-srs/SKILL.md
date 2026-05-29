---
name: hw:srs
description: 通过结构化多轮对话澄清硬件、嵌入式、仪器、控制系统、边缘设备或板级项目需求，并在需求阶段完成硬件/平台适配评估、候选方案取舍和需求调整记录，生成可供 hw:architecture 与 hw:change-plan 使用的硬件 SRS 文档。适用于需求模糊、需要确认目标场景、性能边界、成本/体积/功耗/制造难度、硬件候选与验收方式的场景。触发词包括“硬件需求”“硬件SRS”“需求和硬件匹配”“硬件选型一起考虑”“成本和性能取舍”“hw:srs”。
---

# hw:srs

把自然语言想法收敛为硬件/嵌入式项目的需求与硬件适配输入文档。

本技能是 OpenSpec 前置输入层，不直接创建 OpenSpec change，不写 `proposal.md`、`specs/**`、`design.md` 或 `tasks.md`。后续由 `hw:change-plan` 把本文档映射到 `aisee-device-spec-driven` change 的 `source-map.md` seed。

## Inputs

用户可提供：
- 原始想法、目标或问题现象
- 旧项目说明、竞品、测试记录、规格书
- 成本、周期、体积、功耗、可靠性、制造难度、维护性等约束
- 候选 MCU/CPU/FPGA/传感器/执行器/模组/平台
- 已有库存、采购限制、团队熟悉工具链
- 既有 OpenSpec specs、历史需求或 active changes

可选参数：
- `--lang zh|en`，默认 `zh`
- `--depth shallow|standard|deep`，默认 `standard`
- `--baseline-aware`，存在 `openspec/specs/`、`openspec/changes/` 或历史 SRS 时默认启用

## References

需求澄清时读取：

`references/question-bank.md`

硬件能力评估维度不足时读取：

`references/capability-checklist.md`

## Output

保存到：

`docs/requirements/<YYYY-MM-DD>-<slug>-hw-srs.md`

生成时读取：

`assets/srs-template.md`

必须包含：
- 项目目标、边界、非目标
- 用户/操作者、使用场景、环境
- 功能需求 FR，使用 `FR-001` 形式编号
- 非功能需求 NFR
- 成本、周期、体积、功耗、制造、维护、可靠性和合规约束
- 需求可调整项与不可调整项
- 硬件/平台候选矩阵
- 需求与硬件能力不匹配项
- 需求调整与取舍记录
- 最终硬件/平台方向或待确认项
- 验收目标和证据形式
- `[ASSUMPTION]`、`[OPEN]`、`[FIT-DATA-MISSING]`、`[SPEC-GAP]`
- 给 `hw:architecture` 的输入提示
- 给 `hw:change-plan` 的 FR 变更候选清单

## Phase 0 - Read Context

先读取已有上下文，避免重复提问。

PowerShell:

```powershell
Get-Content -ErrorAction SilentlyContinue README.md
Get-Content -ErrorAction SilentlyContinue openspec/project.md
if (Test-Path openspec/specs) { rg --files openspec/specs }
if (Test-Path openspec/changes) { Get-ChildItem openspec/changes -Directory | Select-Object -ExpandProperty Name }
if (Test-Path docs/requirements) { rg --files docs/requirements }
```

POSIX shell:

```bash
cat README.md 2>/dev/null
cat openspec/project.md 2>/dev/null
test -d openspec/specs && rg --files openspec/specs
test -d openspec/changes && find openspec/changes -maxdepth 1 -type d
test -d docs/requirements && rg --files docs/requirements
```

## Phase 1 - Anchor Scope

第一轮只问一个最关键的范围问题。优先确认：
- 新产品、旧产品改版、验证样机、课程/竞赛项目，还是量产项目
- 目标用户或操作者
- 主要物理对象：信号、传感器、执行器、通信链路、显示、人机交互、控制对象、供电系统等

## Phase 2 - Discovery Dialogue

读取 `references/question-bank.md` 后按主题推进。

规则：
- 每轮最多 3 个问题。
- 同一主题最多追问 3 次。
- 每轮结束判断：已明确 / 可假设推进 / 必须继续追问 / 暂记 `[OPEN]`。
- 不得把未确认指标写成硬约束。

推荐主题：
- 项目边界
- 使用场景与操作者
- 功能目标
- 性能指标
- 成本、体积、功耗、周期、制造难度
- 候选硬件/平台与团队工具链
- 硬件能力碰撞与需求调整
- 验收方式

## Phase 3 - Hardware Fit Loop

需求信息足够后执行硬件/平台适配循环：
- 判断项目类型，可多选：MCU、RTOS、Embedded Linux、FPGA、模拟前端、传感器、执行器、通信、显示、低功耗、边缘 AI、工业/车规/医疗/安规。
- 至少比较用户候选、保守候选和提升候选；候选不足则标记 `[FIT-DATA-MISSING]`。
- 对每个候选写清满足项、不满足项、成本/采购、开发难度、工具链、可验证性、资源余量和扩展空间。
- 如果候选无法满足需求，必须暂停并给出选项：降低需求、更换硬件、增加成本、延长周期、分阶段实现、保留风险继续。
- 不得替用户自动降级需求。

## Phase 4 - Confirmation Gate

生成摘要并等待用户确认。未确认不得写最终文档。

摘要必须列出：
- 当前确认的需求
- 用户明确的取舍偏好
- 未确认问题
- 影响硬件适配的关键指标
- 候选硬件/平台对比结论
- 需要调整的需求
- 最终建议硬件方向
- 后续 `hw:architecture` 必须确认的全局架构问题

## Phase 5 - Generate Document

读取 `assets/srs-template.md` 并写入文档。

SRS 只写需求和硬件适配方向，不写：
- 最终引脚表
- 详细电路实现
- 固件模块内部设计
- 任务清单
- OpenSpec change 边界
- 工程目录结构

这些分别交给 `hw:architecture`、`hw:init` 和 `hw:change-plan`。

## Guardrails

- 不要把详细技术方案伪装成需求。
- 对硬件项目，必须记录“需求可调整项”和“不可调整项”。
- MCU 同系列换型不能只看 Flash/RAM；必须把封装引脚、外设差异、时钟树、模拟外设、DMA/中断、工程宏、启动文件、链接/下载配置列为后续检查项。
- 如果缺少关键数据，标记 `[FIT-DATA-MISSING]`，不要猜测。
- `hw:srs` 的 FR ID 是后续 `hw:change-plan` 和 OpenSpec `source-map.md` 的追踪根。

## Next

完成后：
- 新项目：进入 `hw:architecture`。
- 已有基础工程：可先运行 `hw:init scan-existing` 只读提取工程事实，再进入 `hw:architecture`。
