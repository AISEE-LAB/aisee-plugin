# aisee:tech-context — 技术上下文模板

本模板用于生成 change-plan 前的技术上下文摘要。它不是 change 边界规划模板，不输出 change 名称或阶段计划。

---

## 质量检查清单

- [ ] 没有输出 change 边界规划方案
- [ ] 没有输出 change 名称、phase、依赖图或 `/opsx:*` 命令
- [ ] 技术栈状态已标注：已确定 / 部分确定 / 未确定
- [ ] 每条关键技术事实都有来源和可信度
- [ ] 技术栈缺失时使用 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`
- [ ] 给 `aisee:change-plan` 的内容只包含事实、约束和原因
- [ ] 没有写数据库表结构、API endpoint、ORM 代码或实现步骤

---

## 文档模板

```markdown
# 技术上下文摘要：{需求 / 功能 / 产品名}

**文档编号**：TC-{YYYY-MM-DD}-{slug}
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**来源输入**：{SRS / UI 内容规格 / 项目目录 / 用户输入}

---

## 1. 范围

### 1.1 本文覆盖
- 需求 / 模块：{name}
- 覆盖 FR：{FR-xxx or 无}
- 覆盖平台：{platforms}
- 用途：为 `aisee:change-plan` 提供技术事实和约束

### 1.2 不在范围
- 不规划 change 边界
- 不命名 change
- 不输出 `/opsx:*` 命令
- 不生成 `design.md`
- 不做技术栈选型
- 不写实现方案

---

## 2. 技术栈状态

**状态**：已确定 / 部分确定 / 未确定

| 层 | 技术 / 现状 | 来源 | 可信度 | 备注 |
|----|-------------|------|--------|------|
| 前端 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 后端 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 数据库 | {tech or 未确认} | {source} | high/medium/low | {note} |
| ORM / 数据访问 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 鉴权 / 权限 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 队列 / 异步 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 缓存 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 文件存储 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 通知 / 消息 | {tech or 未确认} | {source} | high/medium/low | {note} |
| 部署环境 | {tech or 未确认} | {source} | high/medium/low | {note} |

---

## 3. 来源与可信度

| 信息 | 来源 | 可信度 | 说明 |
|------|------|--------|------|
| {fact} | {file / doc / user input} | high/medium/low | {note} |

---

## 4. 现有架构边界

| 边界 | 当前事实 | 来源 | 对 change-plan 的影响 |
|------|----------|------|----------------|
| {boundary} | {fact} | {source} | {impact note} |

---

## 5. 已有可复用能力

| 能力 | 当前事实 | 来源 | 可复用方式 | 注意事项 |
|------|----------|------|------------|----------|
| 鉴权 | {fact} | {source} | {reuse note} | {risk} |
| 权限 | {fact} | {source} | {reuse note} | {risk} |
| 数据访问 | {fact} | {source} | {reuse note} | {risk} |
| 队列 / 异步 | {fact} | {source} | {reuse note} | {risk} |
| 文件存储 | {fact} | {source} | {reuse note} | {risk} |
| 通知 | {fact} | {source} | {reuse note} | {risk} |
| 审计 / 日志 | {fact} | {source} | {reuse note} | {risk} |

---

## 6. 共享技术前置

| 前置项 | 为什么是共享前置 | 影响 FR / 页面 | 来源 | 阻塞程度 |
|--------|------------------|----------------|------|----------|
| {prereq} | {reason} | {FR/PAGE} | {source} | blocker/risk/info |

---

## 7. 技术耦合点

| 耦合点 | 涉及范围 | 原因 | 给 change-plan 的影响 |
|--------|----------|------|----------------|
| {coupling} | {FR/PAGE/module} | {reason} | {impact note} |

---

## 8. 平台 / 端能力限制

| 平台 | 能力限制 | 影响范围 | 给 change-plan 的提示 |
|------|----------|----------|----------------|
| PC Web / Admin | {limit or 无} | {scope} | {note} |
| H5 | {limit or 无} | {scope} | {note} |
| App | {limit or 无} | {scope} | {note} |
| 微信小程序 | {limit or 无} | {scope} | {note} |

---

## 9. 给 aisee:change-plan 的技术提示

> 只写事实、约束和原因，不写边界规划结果。

### 9.1 共享技术前置提示
- {note}

### 9.2 技术耦合提示
- {note}

### 9.3 可并行边界提示
- {note}

### 9.4 不应横切的能力
- {note}

### 9.5 高风险区域
- {note}

---

## 10. 阻塞决策与风险

| 编号 | 标记 | 内容 | 影响 | 建议处理 |
|------|------|------|------|----------|
| B-001 | [STACK-CONTEXT-MISSING] / [STACK-GAP] / [STACK-DECISION-REQUIRED] / [SPEC-GAP] / [STACK-CONFLICT] | {content} | {impact} | {next step} |

---

## 11. Open Questions

| 编号 | 问题 | 影响范围 | 是否阻塞 change-plan |
|------|------|----------|----------------|
| Q-001 | {question or 无} | {scope} | 是/否 |
```

---

## 写作规则

- 如果某项信息未确认，写“未确认”，不要猜。
- 如果没有发现某类能力，写“未发现可信来源”，不要写“无”。
- 给 change-plan 的提示不得出现 “Change 1 / Phase 1 / depends on” 等边界规划结果词。
- 阻塞项必须使用明确标签。
