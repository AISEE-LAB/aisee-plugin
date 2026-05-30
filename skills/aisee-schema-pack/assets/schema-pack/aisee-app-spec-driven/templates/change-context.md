# Change Context: {{change-name}}

状态：适用 / N/A

N/A 原因：

> 本文只承接本 change 相关的 Architecture 决策、约束和风险，不重写全局 Architecture，不写接口字段、数据表字段、页面视觉布局或实现步骤。

## 架构来源

| 来源 ID | 类型 | 标题 / 摘要 | 来源文件 | 对本 change 的影响 |
|---|---|---|---|---|
| {{scope}}:ARCH-001 | ARCH / DEC / CONSTRAINT / RISK | | docs/architecture/... | |

## 本 Change 技术边界

| 边界项 | 结论 | 来源 ID | 影响 artifact |
|---|---|---|---|
| 前端 / 客户端边界 | | {{scope}}:DEC-001 | ui-contract.md |
| 服务 / 后端边界 | | {{scope}}:DEC-001 | service-contract.md |
| 数据归属 | | {{scope}}:CONSTRAINT-001 | data-model.md |
| 同步 / 异步策略 | | {{scope}}:DEC-002 | service-contract.md / tasks.md |
| 权限 / 安全边界 | | {{scope}}:CONSTRAINT-002 | ui-contract.md / service-contract.md |
| 集成边界 | | {{scope}}:ARCH-002 | service-contract.md |

## 局部决策

| 决策 ID | 决策 | 依据 | 影响 | 是否需要回写 Architecture |
|---|---|---|---|---|
| {{scope}}:DEC-NEW-001 [ID-RESERVATION-REQUIRED] | | proposal.md / source-map.md / specs | | 是 / 否 |

## 约束传递

| 约束 ID | 必须传递到 | 具体要求 | 验证方式 |
|---|---|---|---|
| {{scope}}:CONSTRAINT-001 | service-contract.md / data-model.md / tasks.md | | |
| {{scope}}:CONSTRAINT-NEW-001 [ID-RESERVATION-REQUIRED] |  |  |  |

## 风险与阻塞

| 风险 ID | 风险 / 阻塞 | 影响 | 处理方式 | 状态 |
|---|---|---|---|---|
| {{scope}}:RISK-001 | | | 规避 / 接受 / 待确认 | Open / Accepted / Closed |
| {{scope}}:RISK-NEW-001 [ID-RESERVATION-REQUIRED] | | | 规避 / 接受 / 待确认 | Open / Accepted / Closed |

## 禁止假设

- 不得发明 Architecture 中未确认的技术栈、服务边界、数据归属或集成方式。
- 存在 `[ARCHITECTURE-DECISION-REQUIRED]`、`[STACK-DECISION-REQUIRED]` 或 `[STACK-CONFLICT]` 时，不得把待确认项写成已确认结论。
