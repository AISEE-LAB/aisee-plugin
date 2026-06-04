# Source Map: {{change-name}} / Source and ID Routing

> 完整 ID 格式：`<scope>:<TYPE>-<number>`。文档中可以显示短 ID，但跨文档引用必须使用完整 ID。正式 ID 必须来自 `aisee/registry/id-registry.json`；未注册、废弃、拆分或合并的 ID 必须标注。工具不可用时只能使用 `{{scope}}:<TYPE>-NEW-001` 形式的临时占位符，并标注 `[ID-RESERVATION-REQUIRED]`。
> Source Map 只记录来源、ID、artifact 适用性、追踪关系、候选影响路径和预期证据类型；不写 contract 细节、不写实现步骤、不写最终验证结论。

## ID Registry 状态

| 检查项 | 状态 | 证据 / 命令 | 备注 |
|---|---|---|---|
| 已运行 author preflight | yes / no | `aisee change author-check {{change-name}} --json` | |
| 已读取 `aisee/registry/id-registry.json` | yes / no | `aisee id check --json` | |
| 已为新增 ID 执行 reserve | yes / no / N/A | `aisee id reserve --scope {{scope}} --type <TYPE> --count <N> --json` | |
| 已为写入 artifact 的 ID 执行 activate | yes / no / N/A | `aisee id activate <id> --owner <path> --title "<title>"` | |
| 存在未注册 ID | yes / no | `author-check.ids.registry.missing` / `aisee trace <id> --json` | |
| 存在临时 ID | yes / no | `[ID-RESERVATION-REQUIRED]` | |
| 存在废弃 / 拆分 / 合并 / 删除 ID | yes / no | `author-check.ids.registry.inactive` / `aisee trace <id> --json` | |

## Author Check 摘要

| 项目 | 结果 | 处理 |
|---|---|---|
| status | ready / needs-work / blocked | |
| schema.valid | true / false | |
| missing_artifacts |  | 按 artifact_order 补齐；Required=no 且有原因的按需 artifact 不应列入 |
| blockers |  | 停止 author，先处理 |
| warnings |  | 写入阻塞项 / 假设 |
| next_actions |  | 执行后回填本文 |

## ID 处理动作

| 动作 | ID / 类型 | 命令 / 处理方式 | 状态 |
|---|---|---|---|
| reserve | SPEC / API / DATA / TASK / TEST | `aisee id reserve --scope {{scope}} --type <TYPE> --count <N> --json` | pending / done / N/A |
| activate | {{scope}}:SPEC-001 | `aisee id activate <id> --owner <path> --title "<title>"` | pending / done / N/A |
| fix missing | {{scope}}:TYPE-001 | 注册 / 替换 / 标注 `[ID-RESERVATION-REQUIRED]` | pending / done / N/A |
| replace inactive | {{scope}}:TYPE-001 | `aisee trace <id> --json` 后替换为有效 ID | pending / done / N/A |

## 上游来源

| 来源 | 路径 / 描述 | sources.json ID | 状态 | 备注 |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/... | SRC-001 | 已确认 / 缺失 / N/A | |
| UI Content | aisee/docs/ui-content/... | SRC-002 | 已确认 / 缺失 / N/A | |
| Design Spec / Assets | docs/design/... / assets/... | SRC-003 / N/A | 已确认 / 缺失 / N/A | |
| Architecture | aisee/docs/architecture/... | SRC-004 | 已确认 / 缺失 / N/A | |
| Change Plan | aisee/docs/change-plan/... | SRC-005 | 已确认 / 缺失 / N/A | |
| Issue / 用户输入 |  | SRC-006 / N/A | 已确认 / 缺失 / N/A | |

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

## Affected Paths Index

> 仅记录候选影响路径和 ID 关联，供 tasks.md 和实现阶段引用；不要在这里写具体修改步骤。

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/... | {{scope}}:API-001 / {{scope}}:DATA-001 | add / modify / remove / reference | |
| test | tests/... | {{scope}}:TEST-001 | add / modify / manual / N/A | |
| docs | docs/... | {{scope}}:SPEC-001 / {{scope}}:TASK-001 | update / reference | |

## Expected Evidence Index

> 仅记录预期证据类型、路径或命令。最终验证任务、执行状态和结论写入 tasks.md、验证报告或归档记录。

| Type | Path / Command | Status | IDs | Notes |
|---|---|---|---|---|
| openspec-validate | `openspec validate {{change-name}}` | expected / N/A | {{scope}}:SPEC-001 | 结果文件建议写入 docs/verification/{{change-name}}-openspec-validate.md |
| test | docs/verification/{{change-name}}-test-results.md | expected / N/A | {{scope}}:TEST-001 | |
| manual | docs/verification/{{change-name}}-manual.md | expected / N/A | {{scope}}:TEST-001 | |

## Artifact 适用性

> 最小闭环为 `proposal.md`、`source-map.md`、`specs/**/*.md` 和 `tasks.md`。
> 下列 artifacts 只在本 change 需要对应契约时 Required=yes。
> Required=no 时必须写具体 N/A 原因；可不展开对应完整模板。

| Artifact | Required | 依据上游 ID | 原因 / N/A 说明 | 相关约束转交 |
|---|---:|---|---|---|
| change-context.md | yes / no | {{scope}}:ARCH-001 / {{scope}}:DEC-001 / N/A | | tasks.md / N/A |
| ui-contract.md | yes / no | {{scope}}:PAGE-001 / {{scope}}:FLOW-001 / N/A | | service-contract.md / tasks.md / N/A |
| service-contract.md | yes / no | {{scope}}:FR-001 / {{scope}}:API-001 / N/A | | data-model.md / tasks.md / N/A |
| data-model.md | yes / no | {{scope}}:DATA-001 / N/A | | service-contract.md / tasks.md / N/A |

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
- change-context.md 仅在 Required=yes 时覆盖 ARCH / DEC / CONSTRAINT / RISK。
- ui-contract.md 仅在 Required=yes 时覆盖 PAGE / FLOW。
- data-model.md 仅在 Required=yes 时覆盖 DATA。
- service-contract.md 仅在 Required=yes 时覆盖 API / backend service / async job / CLI / integration，并满足适用的前端数据需求。
- 每个新增 ID 激活后必须回填到“本 Change 产出 ID”并记录 owner artifact。
- tasks.md 内新增 TASK / TEST ID 前必须先 reserve；无法 reserve 时只使用临时 ID。
- tasks.md 生成前必须重新运行 `aisee change author-check {{change-name}} --json`，确认 blocker 已清除或明确保留。
- tasks.md 生成前必须确认 Required=yes 的追踪关系闭合；Required=no 的 artifact 必须有明确原因。
