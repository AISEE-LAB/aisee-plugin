# Source Map: {{change-name}}

> 完整 ID 格式：`<scope>:<TYPE>-<number>`。文档中可以显示短 ID，但跨文档引用必须使用完整 ID。正式 ID 必须来自 `.aisee/id-registry.json`；未注册、废弃、拆分或合并的 ID 必须标注。工具不可用时只能使用 `{{scope}}:<TYPE>-NEW-001` 形式的临时占位符，并标注 `[ID-RESERVATION-REQUIRED]`。

## ID Registry 状态

| 检查项 | 状态 | 证据 / 命令 | 备注 |
|---|---|---|---|
| 已读取 `.aisee/id-registry.json` | yes / no | `aisee id check --json` | |
| 已为新增 ID 执行 reserve | yes / no / N/A | `aisee id reserve --scope {{scope}} --type <TYPE> --count <N> --json` | |
| 已为写入 artifact 的 ID 执行 activate | yes / no / N/A | `aisee id activate <id> --owner <path> --title "<title>"` | |
| 存在临时 ID | yes / no | `[ID-RESERVATION-REQUIRED]` | |
| 存在废弃 / 拆分 / 合并 ID | yes / no | `aisee trace <id> --json` | |

## 上游来源

| 来源 | 路径 / 描述 | sources.json ID | 状态 | 备注 |
|---|---|---|---|---|
| SRS | docs/requirements/... | SRC-001 | 已确认 / 缺失 / N/A | |
| UI Content | docs/ui-content/... | SRC-002 | 已确认 / 缺失 / N/A | |
| Architecture | docs/architecture/... | SRC-003 | 已确认 / 缺失 / N/A | |
| Change Plan | docs/change-plan/... | SRC-004 | 已确认 / 缺失 / N/A | |
| Issue / 用户输入 |  | SRC-005 / N/A | 已确认 / 缺失 / N/A | |

## 上游输入 ID

| 类型 | 完整 ID | 标题 / 名称 | 来源 | 本 change 处理方式 | 后续 artifact |
|---|---|---|---|---|---|
| FR | {{scope}}:FR-001 | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / tasks |
| NFR | {{scope}}:NFR-001 | | SRS / Architecture | 覆盖 / 部分覆盖 / 不覆盖 | specs / change-context / tasks |
| RULE | {{scope}}:RULE-001 | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / service-contract |
| PAGE | {{scope}}:PAGE-001 | | UI Content | 新增 / 修改 / 复用 / 不覆盖 | ui-contract |
| FLOW | {{scope}}:FLOW-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| STATE | {{scope}}:STATE-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| ARCH | {{scope}}:ARCH-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context |
| DEC | {{scope}}:DEC-001 | | Architecture | 承接 / 局部补充 / 待确认 | change-context |
| CONSTRAINT | {{scope}}:CONSTRAINT-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context / contracts / tasks |
| RISK | {{scope}}:RISK-001 | | Architecture / Change Plan | 规避 / 接受 / 待确认 | change-context / tasks |

## 本 Change 产出 ID

| 类型 | 完整 ID | 标题 / 名称 | 产生 artifact | 追踪到上游 ID |
|---|---|---|---|---|
| SPEC | {{scope}}:SPEC-001 | | specs/... | {{scope}}:FR-001 |
| API | {{scope}}:API-001 | | service-contract.md | {{scope}}:FR-001 / {{scope}}:PAGE-001 |
| DATA | {{scope}}:DATA-001 | | data-model.md | {{scope}}:FR-001 / {{scope}}:API-001 |
| TASK | {{scope}}:TASK-001 | | tasks.md | {{scope}}:SPEC-001 / {{scope}}:API-001 |
| TEST | {{scope}}:TEST-001 | | tasks.md / verification evidence | {{scope}}:SPEC-001 |

## 不在本 Change 范围

- 

## Artifact 适用性

| Artifact | Required | 原因 |
|---|---:|---|
| change-context.md | yes / no | |
| ui-contract.md | yes / no | |
| service-contract.md | yes / no | |
| data-model.md | yes / no | |

## 阻塞项 / 假设

- [ASSUMPTION] 
- [SPEC-GAP] 
- [STACK-CONTEXT-MISSING] 
- [STACK-DECISION-REQUIRED] 
- [ARCHITECTURE-DECISION-REQUIRED] 
- [STACK-CONFLICT] 
- [ID-RESERVATION-REQUIRED]
- [ID-CHECK-FAILED]

## 追踪规则

- specs 必须覆盖本 change 的全部 FR。
- change-context.md 必须覆盖 Required=yes 的 ARCH / DEC / CONSTRAINT / RISK。
- ui-contract.md 必须覆盖 Required=yes 的 PAGE / FLOW。
- data-model.md 必须覆盖 Required=yes 的 DATA。
- service-contract.md 必须覆盖 Required=yes 的 API / backend service / async job / CLI / integration，并满足 ui-contract.md 的前端数据需求。
- tasks.md 内新增 TASK / TEST ID 前必须先 reserve；无法 reserve 时只使用临时 ID。
- tasks.md 生成前必须确认上述追踪关系闭合。
