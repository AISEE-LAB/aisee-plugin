# Source Map: {{change-name}}

## 上游来源

| 来源 | 路径 / 描述 | 状态 | 备注 |
|---|---|---|---|
| SRS | docs/requirements/... | 已确认 / 缺失 / N/A | |
| UI Content | docs/ui-content/... | 已确认 / 缺失 / N/A | |
| Architecture | docs/architecture/... | 已确认 / 缺失 / N/A | |
| Change Plan | docs/change-plan/... | 已确认 / 缺失 / N/A | |
| Issue / 用户输入 |  | 已确认 / 缺失 / N/A | |

## 本 Change 覆盖

| 类型 | ID | 标题 / 名称 | 来源 | 后续 artifact |
|---|---|---|---|---|
| FR | FR-001 | | SRS / proposal | specs |
| PAGE | PAGE-001 | | UI Content | ui-contract |
| FLOW | FLOW-001 | | UI Content / SRS | specs / ui-contract / service-contract |
| API | API-001 | | design / service-contract | service-contract |
| DATA | DATA-001 | | design / data-model | data-model |

## 不在本 Change 范围

- 

## Artifact 适用性

| Artifact | Required | 原因 |
|---|---:|---|
| ui-contract.md | yes / no | |
| data-model.md | yes / no | |
| service-contract.md | yes / no | |

## 阻塞项 / 假设

- [ASSUMPTION] 
- [SPEC-GAP] 
- [STACK-CONTEXT-MISSING] 
- [STACK-DECISION-REQUIRED] 
- [ARCHITECTURE-DECISION-REQUIRED] 
- [STACK-CONFLICT] 

## 追踪规则

- specs 必须覆盖本 change 的全部 FR。
- ui-contract.md 必须覆盖 Required=yes 的 PAGE / FLOW。
- data-model.md 必须覆盖 Required=yes 的 DATA。
- service-contract.md 必须覆盖 Required=yes 的 API，并满足 ui-contract.md 的前端数据需求。
- tasks.md 生成前必须确认上述追踪关系闭合。
