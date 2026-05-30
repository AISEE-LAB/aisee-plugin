# aisee:change-plan — 输入边界规则

在规划 OpenSpec change 前读取本文件。它用于防止 change-plan 被 SRS 模块名、输入材料章节、技术层或页面类型误导。

## 核心原则

`aisee:change-plan` 的输出是可独立交付的 OpenSpec change 边界，不是 SRS 模块复制、页面清单复制、架构分层复制或任务列表复制。

## 输入材料处理

| 输入来源 | 使用方式 | 不得做什么 |
|----------|----------|------------|
| SRS | 使用 FR、优先级、依赖、假设、Open Questions、需求域、交付形态 | 不把 SRS 模块名直接当 change 名 |
| UI Content | 使用 PAGE / FLOW、角色可见性、页面状态、跨页面流程 | 不把页面类型直接当 change 边界 |
| Design Spec | 使用设计策略、组件策略、tokens、screen patterns、设计阻塞项 | 不把设计规范拆成独立实现 change，除非它是明确前置能力 |
| Architecture | 使用架构决策、技术事实、共享前置、耦合点、阻塞标签 | 不把架构层、技术层或 artifact hint 直接当 change |
| 原始草稿 | 先提取真实需求和约束 | 不把“背景 / API / 数据库 / 测试 / 上线计划”等章节当 change |

## 有效 Change 候选信号

一个候选 change 至少满足以下条件：

- 它能交付一组可验证的用户、操作者、系统或设备可观察行为。
- 它合并后系统仍保持工作状态，必要时可通过 feature flag 隐藏未完成能力。
- 它有相对清晰的 owner 和边界，不要求多个团队在同一 change 内做互相阻塞的决策。
- 它能映射到明确的 FR / PAGE / FLOW / HW / FW / RT / VER 或其他 source-map seed。
- 它的 Out of Scope 能明确排除相邻能力。

## 无效 Change 候选信号

不要仅因为以下内容出现就创建 change：

- 输入文档章节：背景、目标、范围、假设、风险、路线图、上线计划
- 技术层：前端、后端、数据库、API、缓存、队列、部署、可观测性
- UI 页面类型：列表页、详情页、弹窗、设置页，除非该页面本身就是一个可独立交付的用户场景
- schema artifact：design.md、ui-contract.md、data-model.md、service-contract.md、hardware-contract.md
- 实施阶段：初始化、搭框架、写测试、联调、发布

如果这些内容包含真实需求，提取背后的用户场景、业务能力、设备能力或风险前置。

## 候选审查表

输出最终计划前，内部完成候选审查：

| 候选 change | 保留 / 合并 / 拆分 / 拒绝 | 原因 | 主要来源 |
|-------------|----------------------------|------|----------|
| {name} | 保留 | {独立可交付的业务能力} | FR-001 / PAGE-001 / ARCH-001 |

规则：

- 只作为同一用户流程步骤存在的候选项，应合并。
- 横切多个独立能力且 owner 不同的候选项，应拆分。
- 只是输入章节、技术层或实施任务的候选项，应拒绝。
- 如果拒绝或合并了用户材料里的章节，在整体理由中简要说明。

## 阻塞项处理

- `[ARCHITECTURE-DECISION-REQUIRED]`、`[STACK-DECISION-REQUIRED]`、`[DESIGN-DECISION-REQUIRED]` 如果影响 change 是否可独立交付，应作为 blocker 写入相关 change rationale。
- 阻塞项不一定阻止输出 plan，但必须阻止把未确认决策伪装成已确认边界。
- 如果关键架构决策缺失导致无法判断边界，输出一个“需要先补 Architecture 决策”的阻塞结论，不要硬拆 change。
