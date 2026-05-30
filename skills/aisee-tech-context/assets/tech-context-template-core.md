# aisee:tech-context — Core 模板

所有技术域都必须使用。用于生成跨工程域通用部分：范围、技术域、来源、全局工程约定、架构边界、可复用能力、共享前置、耦合点、运行环境限制、风险和 Open Questions。

```markdown
# 技术上下文摘要：{需求 / 功能 / 产品名}

**文档编号**：TC-{YYYY-MM-DD}-{slug}
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**来源输入**：{SRS / UI 内容规格 / 设计规范 / 项目目录 / 用户输入}
**技术域**：{software / web / backend / cli / job / integration / data / hardware / embedded / firmware / rtos / driver / hybrid}

---

## 1. 范围

### 1.1 本文覆盖
- 需求 / 模块：{name}
- 覆盖 FR：{FR-xxx or 无}
- 覆盖平台 / 运行环境：{platforms / runtime / board}
- 用途：为 `aisee:change-plan` 提供技术事实、工程约定、约束和 schema artifact hints

### 1.2 不在范围
- 不规划 change 边界
- 不命名 change
- 不输出 `/opsx:*` 命令
- 不生成 `design.md`
- 不做技术栈 / 工具链选型
- 不写具体契约或实现方案

---

## 2. 技术域与技术栈 / 工具链状态

**状态**：已确定 / 部分确定 / 未确定

| 层 / 类别 | 技术 / 现状 | 来源 | 可信度 | 备注 |
|-----------|-------------|------|--------|------|
| 前端 / 客户端 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 后端 / 服务 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 数据库 / 数据访问 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 鉴权 / 权限 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 队列 / 异步 / 调度 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 缓存 / 文件 / 通知 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 部署 / 运行环境 | {tech or 未确认} | {source} | high/medium/low | {note} |
| MCU / SoC / FPGA / Board | {tech or 未确认} | {source} | high/medium/low | {note} |
| RTOS / Bare-metal / Linux | {tech or 未确认} | {source} | high/medium/low | {note} |
| 编译 / 构建 / 烧录 / 调试 | {toolchain or 未确认} | {source} | high/medium/low | {note} |

---

## 3. 来源与可信度

| 信息 | 来源 | 可信度 | 说明 |
|------|------|--------|------|
| {fact} | {file / doc / user input} | high/medium/low | {note} |

---

## 4. 全局工程约定

> 只记录已有约定或待决策缺口，不在本节创造新的 API、数据、CLI、Job、硬件或固件契约。

| 类型 | 当前约定 / 现状 | 来源 | 可信度 | 影响范围 | 后续 artifact 提示 |
|------|-----------------|------|--------|----------|--------------------|
| API 响应 / 错误码 / 分页 / 时间格式 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 鉴权 / 权限 / Trace ID / 日志 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 配置 / Feature Flag / Secrets | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| CLI 输出 / 退出码 / 配置优先级 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| Job 幂等 / 重试 / 可观测性 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 命名 / 错误码 / 日志等级 / 断言 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 时钟单位 / 中断 / 内存对齐 / 外设初始化 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |

---

## 5. 现有架构边界

| 边界 | 当前事实 | 来源 | 对 change-plan 的影响 |
|------|----------|------|------------------------|
| {boundary} | {fact} | {source} | {impact note} |

---

## 6. 已有可复用能力

| 能力 | 当前事实 | 来源 | 可复用方式 | 注意事项 |
|------|----------|------|------------|----------|
| 鉴权 / 权限 | {fact} | {source} | {reuse note} | {risk} |
| 数据访问 / 状态机 | {fact} | {source} | {reuse note} | {risk} |
| 队列 / 异步 / 调度 | {fact} | {source} | {reuse note} | {risk} |
| 文件 / 通知 / 审计 / 日志 | {fact} | {source} | {reuse note} | {risk} |
| 构建 / 烧录 / 调试 / 测试夹具 | {fact} | {source} | {reuse note} | {risk} |
| 驱动 / HAL / BSP / 外设抽象 | {fact} | {source} | {reuse note} | {risk} |

---

## 7. 共享技术前置

| 前置项 | 为什么是共享前置 | 影响 FR / 页面 / 模块 / 硬件能力 | 来源 | 阻塞程度 |
|--------|------------------|----------------------------------|------|----------|
| {prereq} | {reason} | {FR/PAGE/module/HW/FW} | {source} | blocker/risk/info |

---

## 8. 技术耦合点

| 耦合点 | 涉及范围 | 原因 | 给 change-plan 的影响 |
|--------|----------|------|------------------------|
| {coupling} | {FR/PAGE/module/data/job/integration/HW/FW/RT/driver} | {reason} | {impact note} |

---

## 9. 平台 / 运行环境限制

| 平台 / 环境 | 能力限制 | 影响范围 | 给 change-plan 的提示 |
|-------------|----------|----------|------------------------|
| PC Web / Admin | {limit or 无} | {scope} | {note} |
| H5 / App / 微信小程序 | {limit or 无} | {scope} | {note} |
| Desktop / CLI / Server | {limit or 无} | {scope} | {note} |
| MCU / SoC / Board / RTOS / Linux | {limit or 无} | {scope} | {note} |

---

## 12. 给 aisee:change-plan 的技术提示

> 只写事实、约束和原因，不写边界规划结果。

### 12.1 共享技术前置提示
- {note}

### 12.2 技术耦合提示
- {note}

### 12.3 可并行边界提示
- {note}

### 12.4 不应横切的能力
- {note}

### 12.5 高风险区域
- {note}

---

## 13. 阻塞决策与风险

| 编号 | 标记 | 内容 | 影响 | 建议处理 |
|------|------|------|------|----------|
| B-001 | [STACK-CONTEXT-MISSING] / [STACK-GAP] / [STACK-DECISION-REQUIRED] / [SPEC-GAP] / [STACK-CONFLICT] / [TECH-CONVENTION-MISSING] / [SCHEMA-HINT-UNCLEAR] | {content} | {impact} | {next step} |

---

## 14. Open Questions

| 编号 | 问题 | 影响范围 | 是否阻塞 change-plan |
|------|------|----------|----------------------|
| Q-001 | {question or 无} | {scope} | 是/否 |
```
