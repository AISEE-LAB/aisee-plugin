# aisee:tech-context — 问题库

Phase 2 使用。只问会影响技术上下文和 change-plan 输入提示的问题。

---

## 追问优先级

1. 项目级技术栈来源
2. 技术域：software / web / backend / cli / job / integration / data / hardware / embedded / firmware / rtos / driver / hybrid
3. 全局工程约定来源
4. 关键基础设施 / 工具链缺口
5. 现有架构边界
6. 可复用能力
7. 平台、板级或运行环境限制
8. 技术耦合点与 schema artifact hints

每轮最多 3 个问题。超过 3 轮仍不明确时写入 Open Questions。

---

## 技术栈状态

- 项目级技术栈记录在哪里：`openspec/project.md`、架构文档、tech-context，还是既有代码？
- 当前哪些技术栈已经确定，哪些还未确认？
- 是否存在技术栈迁移、替换或禁用某些技术的约束？
- 当前需求属于软件 Web/后端、CLI、Job、集成、数据，还是硬件/嵌入式/固件/RTOS/驱动，或混合域？

---

## 全局工程约定

- 是否已有统一 API 响应 envelope、错误码、分页、排序、时间格式或鉴权 header 约定？
- 是否已有日志、Trace ID、审计、错误处理、监控告警或可观测性约定？
- 是否已有配置、环境变量、feature flag、secrets 管理或多环境配置约定？
- CLI 工具是否已有输出格式、退出码、配置优先级和分发方式约定？
- Job / 异步任务是否已有幂等、重试、失败处理、死信、回放或告警约定？
- 硬件 / 嵌入式是否已有命名、错误码、日志等级、时钟单位、中断、内存对齐、外设初始化或断言约定？

---

## 既有项目架构

- 当前项目的主要模块边界是什么？
- 是否已有统一的认证、权限、数据访问、错误处理和日志机制？
- 是否已有队列、异步任务、缓存、文件存储、通知或审计能力？
- 哪些目录或文档最能代表项目事实？
- 是否已有组件库、theme/token、设计系统工程接入方式？这些技术事实是否需要与 `aisee:design-spec` 对齐？

---

## 需求相关技术事实

- 这些需求会复用哪些已有模块或能力？
- 是否需要共享数据模型、共享状态机或共享权限规则？
- 是否涉及导入导出、报表、通知、审批、支付、外部集成或定时任务？
- 是否存在必须先确认的技术基础设施？
- 是否涉及 CLI 命令、批处理工具、开发者工具、运维工具或本地文件系统访问？
- 是否涉及数据迁移、历史兼容、回滚、报表口径或旧状态枚举？
- 哪些后续契约类型可能需要承接：UI、服务、数据、CLI、Job、集成、安全、观测性、配置、迁移？

---

## 多端与平台限制

- 目标端有哪些：PC Web、H5、App、微信小程序？
- 小程序、H5、App 是否有文件下载、授权、推送、扫码、定位、支付等能力差异？
- 哪些平台限制会影响后续 change 边界规划？

---

## 硬件 / 嵌入式 / 固件

- 目标硬件、MCU/SoC/FPGA、板卡版本和运行环境是什么？
- 是裸机、RTOS、嵌入式 Linux、驱动、Bootloader，还是混合系统？
- 构建、烧录、调试工具链是否已确定：CMake/Make/West/PlatformIO、编译器、J-Link/OpenOCD 等？
- 是否已有板级配置、设备树、引脚、时钟、电源、内存布局、链接脚本或启动文件？
- 是否涉及外设、总线、DMA、中断、低功耗、热设计、启动时序或实时性约束？
- 是否已有 HIL/SIL/仿真/实验室夹具/产测/校准流程？

---

## 风险与阻塞

- 是否有未知技术栈会阻塞 change-plan 判断？
- 是否有现有架构和需求方向冲突？
- 是否有需要先做调研或 PoC 的技术风险？
- 是否有安全、合规、审计、迁移或性能风险会影响 change 边界规划？
- 是否有全局工程约定缺失，会导致多个 change 或后续 artifact 反复决策？
- 是否有 schema artifact 类型不明确，需要 schema pack 后续确认？

---

## 标签使用

缺少项目级技术栈来源：

`[STACK-CONTEXT-MISSING] 缺少项目级技术栈来源；影响 change-plan 判断。`

技术栈中缺少本需求需要的组件：

`[STACK-GAP] 缺少 {component}；影响 {FR/PAGE/module}。`

需要正式技术决策：

`[STACK-DECISION-REQUIRED] 需要确认 {decision}。`

需求与技术约束冲突：

`[SPEC-GAP] {需求缺口} — 影响技术上下文判断。`

change 技术约束与项目事实冲突：

`[STACK-CONFLICT] 输入约束：{constraint}；项目事实：{fact}。`

缺少全局工程约定：

`[TECH-CONVENTION-MISSING] 缺少 {convention}；影响 {artifact/domain/change-plan input}。`

后续 schema artifact 提示不明确：

`[SCHEMA-HINT-UNCLEAR] {scope} 需要后续契约承接，但 schema artifact 类型未确认。`
