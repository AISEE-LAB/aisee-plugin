# aisee:architecture — Core 模板

所有软件技术域都必须使用。用于生成通用部分：范围、技术域、来源、架构概览、全局工程约定、架构决策、架构边界、可复用能力、共享前置、耦合点、运行环境限制、风险和 Open Questions。

```markdown
# 技术架构文档：{需求 / 功能 / 产品名}

**文档编号**：ARCH-{YYYY-MM-DD}-{slug}
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**来源输入**：{SRS / UI 内容规格 / 设计规范 / 项目目录 / 用户输入}
**技术域**：{app / web / mini-program / desktop / backend-service / cli-tool / job-async / integration / data / hybrid-software}
**ID Scope**：{scope}

> 正式 ARCH / DEC / CONSTRAINT / RISK ID 必须来自 `aisee/registry/id-registry.json`。工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 临时占位符，并标注 `[ID-RESERVATION-REQUIRED]`。

---

## 1. 范围

### 1.1 本文覆盖
- 需求 / 模块：{name}
- 覆盖 FR：{FR-xxx or 无}
- 覆盖平台 / 运行环境：{platforms / runtime}
- 用途：为 `aisee:change-plan` 提供技术事实、架构决策、工程约定、约束和 schema artifact hints

### 1.2 不在范围
- 不规划 change 边界
- 不命名 change
- 不输出 `/opsx:*` 命令
- 不生成 `design.md`
- 不做技术栈 / 工具链选型
- 不写具体契约或实现方案

---

## 2. 技术域与技术栈 / 工具链状态

### 2.0 ID Registry 状态

| 检查项 | 状态 | 证据 / 命令 | 备注 |
|---|---|---|---|
| 已读取 `aisee/registry/id-registry.json` | yes / no | `aisee id check --json` | |
| 已为新增 ARCH / DEC / CONSTRAINT / RISK 执行 reserve | yes / no / N/A | `aisee id reserve --scope {scope} --type <TYPE> --count <N> --json` | |
| 存在临时 ID | yes / no | `[ID-RESERVATION-REQUIRED]` | |

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
| 测试 / 可观测性 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 设备协作 / 上位机 / IoT | {tech or 未确认} | {source} | high/medium/low | 只记录软件可见协作约束 |

---

## 3. 来源与可信度

| 信息 | 来源 | 可信度 | 说明 |
|------|------|--------|------|
| {fact} | {file / doc / user input} | high/medium/low | {note} |

---

## 4. 架构概览

| ARCH ID | 项 | 当前事实 / 决策 | 来源 | 可信度 | 对 change-plan 的影响 |
|----|----|-----------------|------|--------|------------------------|
| {scope}:ARCH-001 | 系统分层 | {fact/decision or 未确认} | {source} | high/medium/low | {impact} |
| {scope}:ARCH-002 | 主要运行单元 | {fact/decision or 未确认} | {source} | high/medium/low | {impact} |
| {scope}:ARCH-003 | 端 / 服务 / 设备协作关系 | {fact/decision or 未确认} | {source} | high/medium/low | {impact} |
| {scope}:ARCH-004 | 模块边界原则 | {fact/decision or 未确认} | {source} | high/medium/low | {impact} |

---

## 5. 全局工程约定

> 只记录已有约定或待决策缺口，不在本节创造新的 API、数据、CLI、Job、硬件或固件契约。

| CONSTRAINT ID | 类型 | 当前约定 / 现状 | 来源 | 可信度 | 影响范围 | 后续 artifact 提示 |
|------|------|-----------------|------|--------|----------|--------------------|
| {scope}:CONSTRAINT-001 | API 响应 / 错误码 / 分页 / 时间格式 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 鉴权 / 权限 / Trace ID / 日志 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 配置 / Feature Flag / Secrets | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| CLI 输出 / 退出码 / 配置优先级 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| Job 幂等 / 重试 / 可观测性 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 命名 / 错误码 / 日志等级 / 断言 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |
| 设备状态 / 上报 / 告警协作 | {convention or 未发现可信来源} | {source} | high/medium/low | {scope} | {suggested artifact type} |

---

## 6. 架构决策

### 6.1 已确认决策

| DEC ID | 决策 | 来源 | 可信度 | 影响范围 | 后续约束 |
|------|------|------|--------|----------|----------|
| {scope}:DEC-001 | {decision or 无} | {source} | high/medium/low | {scope} | {constraint} |

### 6.2 待确认决策

| DEC ID | 待确认事项 | 影响范围 | 阻塞程度 | 建议处理 |
|------|------------|----------|----------|----------|
| {scope}:DEC-NEW-001 | {question or 无} | {scope} | blocker/risk/info | {next step} |

### 6.3 禁止假设项

| 项 | 为什么不能假设 | 影响范围 |
|----|----------------|----------|
| {item or 无} | {reason} | {scope} |

---

## 7. 现有架构边界

| ARCH ID | 边界 | 当前事实 | 来源 | 对 change-plan 的影响 |
|------|------|----------|------|------------------------|
| {scope}:ARCH-001 | {boundary} | {fact} | {source} | {impact note} |

---

## 8. 已有可复用能力

| 能力 | 当前事实 | 来源 | 可复用方式 | 注意事项 |
|------|----------|------|------------|----------|
| 鉴权 / 权限 | {fact} | {source} | {reuse note} | {risk} |
| 数据访问 / 状态机 | {fact} | {source} | {reuse note} | {risk} |
| 队列 / 异步 / 调度 | {fact} | {source} | {reuse note} | {risk} |
| 文件 / 通知 / 审计 / 日志 | {fact} | {source} | {reuse note} | {risk} |
| 测试 / 可观测性 | {fact} | {source} | {reuse note} | {risk} |
| 设备协作 / 上位机 / IoT | {fact} | {source} | {reuse note} | {risk} |

---

## 9. 共享技术前置

| 前置项 | 为什么是共享前置 | 影响 FR / 页面 / 模块 / 设备协作能力 | 来源 | 阻塞程度 |
|--------|------------------|----------------------------------|------|----------|
| {prereq} | {reason} | {FR/PAGE/module/device-collaboration} | {source} | blocker/risk/info |

---

## 10. 技术耦合点

| 耦合点 | 涉及范围 | 原因 | 给 change-plan 的影响 |
|--------|----------|------|------------------------|
| {coupling} | {FR/PAGE/module/data/job/integration/device-collaboration} | {reason} | {impact note} |

---

## 11. 平台 / 运行环境限制

| 平台 / 环境 | 能力限制 | 影响范围 | 给 change-plan 的提示 |
|-------------|----------|----------|------------------------|
| PC Web / Admin | {limit or 无} | {scope} | {note} |
| H5 / App / 微信小程序 | {limit or 无} | {scope} | {note} |
| Desktop / CLI / Server | {limit or 无} | {scope} | {note} |
| 设备协作 / 上位机 / IoT | {limit or 无} | {scope} | {note} |

---

## 14. 给 aisee:change-plan 的架构提示

> 只写事实、约束和原因，不写边界规划结果。

### 14.1 共享技术前置提示
- {note}

### 14.2 技术耦合提示
- {note}

### 14.3 可并行边界提示
- {note}

### 14.4 不应横切的能力
- {note}

### 14.5 高风险区域
- {note}

---

## 15. 阻塞决策与风险

| RISK ID | 标记 | 内容 | 影响 | 建议处理 |
|------|------|------|------|----------|
| {scope}:RISK-001 | [STACK-CONTEXT-MISSING] / [STACK-DECISION-REQUIRED] / [DOC-CONTEXT-MISSING] / [ARCH-DECISION-REQUIRED] / [SPEC-GAP] / [STACK-CONFLICT] / [TECH-CONVENTION-MISSING] / [SCHEMA-HINT-UNCLEAR] / [ID-RESERVATION-REQUIRED] | {content} | {impact} | {next step} |

---

## 16. Open Questions

| 编号 | 问题 | 影响范围 | 是否阻塞 change-plan |
|------|------|----------|----------------------|
| Q-001 | {question or 无} | {scope} | 是/否 |
```
