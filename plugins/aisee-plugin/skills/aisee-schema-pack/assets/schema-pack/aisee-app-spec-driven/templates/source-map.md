# Source Map: {{change-name}} / Anchor Routing

> 正式 authoring 只使用 local ID，例如 `FR-001`、`SPEC-001`、`API-001`。跨文档引用必须使用 `doc-ref#LOCAL-ID` 或 alias anchor，例如 `docs/requirements/auth-srs.md#FR-001`、`srs:auth-login#FR-001`。如需临时占位，使用 `TYPE-NEW-001` 并标注 `[ID-FINALIZATION-REQUIRED]`。
> Source Map 只记录来源、anchor refs、artifact 适用性、追踪关系、候选影响路径和预期证据类型；不写 contract 细节、不写实现步骤、不写最终验证结论。

## Anchor 状态

| 检查项 | 状态 | 证据 / 命令 | 备注 |
|---|---|---|---|
| 已运行 author preflight | yes / no | `aisee change author-check {{change-name}} --json` | |
| 已运行 author preflight | yes / no | `aisee change author-check {{change-name}} --json` | |
| anchor refs 可解析 | yes / no | `aisee get <anchor-ref> --json` / `aisee trace <anchor-ref> --json` | |
| 存在未解析 anchor | yes / no | `author-check.anchors.resolution.missing_references` | |
| 存在临时 local ID | yes / no | `[ID-FINALIZATION-REQUIRED]` | |
| 存在 legacy full ID 文本 | yes / no | `LEGACY_FULL_ID_REFERENCE` 诊断 | |

## Author Check 摘要

| 项目 | 结果 | 处理 |
|---|---|---|
| status | ready / needs-work / blocked | |
| schema.valid | true / false | |
| missing_artifacts |  | 按 artifact_order 补齐；Required=no 且有原因的按需 artifact 不应列入 |
| blockers |  | 停止 author，先处理 |
| warnings |  | 写入阻塞项 / 假设 |
| next_actions |  | 执行后回填本文 |

## Anchor 处理动作

| 动作 | ID / 类型 | 命令 / 处理方式 | 状态 |
|---|---|---|---|
| finalize local id | SPEC-NEW-001 | 替换为最终 local ID，并同步当前文档锚点 | pending / done / N/A |
| fix missing anchor | docs/...#FR-001 | 修正文档路径、alias 或 local ID | pending / done / N/A |
| replace legacy full ID | `docs/...#FR-001` 的旧 full ID 文本 | 改写为 `doc-ref#LOCAL-ID` 或 alias anchor | pending / done / N/A |

## 上游来源

| 来源 | 路径 / 描述 | sources.json ID | 状态 | 备注 |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/... | SRC-001 | 已确认 / 缺失 / N/A | |
| UI Content | aisee/docs/ui-content/... | SRC-002 | 已确认 / 缺失 / N/A | |
| Design Spec / Assets | docs/design/... / assets/... | SRC-003 / N/A | 已确认 / 缺失 / N/A | |
| Architecture | aisee/docs/architecture/... | SRC-004 | 已确认 / 缺失 / N/A | |
| Change Plan | aisee/docs/change-plan/... | SRC-005 | 已确认 / 缺失 / N/A | |
| Issue / 用户输入 |  | SRC-006 / N/A | 已确认 / 缺失 / N/A | |

## 上游输入 Anchor

| 类型 | Ref | 标题 / 名称 | 来源 | 本 change 处理方式 | 后续 artifact |
|---|---|---|---|---|---|
| FR | docs/requirements/...#FR-001 | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / tasks |
| NFR | docs/requirements/...#NFR-001 | | SRS / Architecture | 覆盖 / 部分覆盖 / 不覆盖 | specs / change-context / tasks |
| RULE | docs/requirements/...#RULE-001 | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / service-contract |
| PAGE | docs/ui-content/...#PAGE-001 | | UI Content | 新增 / 修改 / 复用 / 不覆盖 | ui-contract |
| FLOW | docs/ui-content/...#FLOW-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| STATE | docs/ui-content/...#STATE-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| ARCH | docs/architecture/...#ARCH-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context |
| DEC | docs/architecture/...#DEC-001 | | Architecture | 承接 / 局部补充 / 待确认 | change-context |
| CONSTRAINT | docs/architecture/...#CONSTRAINT-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context / contracts / tasks |
| RISK | docs/architecture/...#RISK-001 | | Architecture / Change Plan | 规避 / 接受 / 待确认 | change-context / tasks |

## 本 Change 产出 Local ID

| 类型 | Local ID | 标题 / 名称 | 产生 artifact | 追踪到上游 Ref |
|---|---|---|---|---|
| SPEC | SPEC-001 | | specs/... | docs/requirements/...#FR-001 |
| API | API-001 | | service-contract.md | docs/requirements/...#FR-001 / docs/ui-content/...#PAGE-001 |
| DATA | DATA-001 | | data-model.md | docs/requirements/...#FR-001 / API-001 |
| TASK | TASK-001 | | tasks.md | SPEC-001 / API-001 |
| TEST | TEST-001 | | tasks.md / verification evidence | SPEC-001 |

## 不在本 Change 范围

- 

## Affected Paths Index

> 仅记录候选影响路径和 ID 关联，供 tasks.md 和实现阶段引用；不要在这里写具体修改步骤。

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/... | API-001 / DATA-001 | add / modify / remove / reference | |
| test | tests/... | TEST-001 | add / modify / manual / N/A | |
| docs | docs/... | SPEC-001 / TASK-001 | update / reference | |

## Expected Evidence Index

> 仅记录预期证据类型、路径或命令。最终验证任务、执行状态和结论写入 tasks.md、验证报告或归档记录。

| Type | Path / Command | Status | Refs | Notes |
|---|---|---|---|---|
| openspec-validate | `openspec validate {{change-name}}` | expected / N/A | SPEC-001 | 结果文件建议写入 docs/verification/{{change-name}}-openspec-validate.md |
| test | docs/verification/{{change-name}}-test-results.md | expected / N/A | TEST-001 | |
| manual | docs/verification/{{change-name}}-manual.md | expected / N/A | TEST-001 | |

## Artifact 适用性

> 最小闭环为 `proposal.md`、`source-map.md`、`specs/**/*.md` 和 `tasks.md`。
> 下列 artifacts 只在本 change 需要对应契约时 Required=yes。
> Required=no 时必须写具体 N/A 原因；可不展开对应完整模板。

| Artifact | Required | 依据上游 Ref / Local ID | 原因 / N/A 说明 | 相关约束转交 |
|---|---:|---|---|---|
| change-context.md | yes / no | docs/architecture/...#ARCH-001 / docs/architecture/...#DEC-001 / N/A | | tasks.md / N/A |
| ui-contract.md | yes / no | docs/ui-content/...#PAGE-001 / docs/ui-content/...#FLOW-001 / N/A | | service-contract.md / tasks.md / N/A |
| service-contract.md | yes / no | docs/requirements/...#FR-001 / API-001 / N/A | | data-model.md / tasks.md / N/A |
| data-model.md | yes / no | DATA-001 / N/A | | service-contract.md / tasks.md / N/A |

## Contract Ownership / Sync

> 当前后端分仓、独立契约仓库、BFF 或外部服务适用时填写。`service-contract.md` Required=no 且无跨仓库协作时，可全部写 N/A 并说明原因。
> 本表是机器可解析的同步路由；不要在这里展开接口字段、请求响应或业务规则。

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend / frontend-bff / contract-repo / external-provider / shared / N/A | confirmed / pending / N/A | 权威维护方 |
| canonical_source | service-contract.md / contracts/openapi.yaml / contracts/events.yaml / contracts/webhooks.yaml / contracts/proto/*.proto / external | confirmed / pending / N/A | 冲突时以此为准 |
| provider_repo | repo name / package / URL / N/A | confirmed / pending / N/A | 服务提供方 |
| consumer_repo | repo name / package / URL / N/A | confirmed / pending / N/A | 服务消费方，可多个 |
| sync_mode | manual-copy / git-submodule / package / local-http / artifact-export / N/A | confirmed / pending / N/A | 跨仓库同步方式 |
| conflict_rule | canonical-source-wins / provider-wins / consumer-request-provider-approval / N/A | confirmed / pending / N/A | 冲突解决规则 |
| machine_readable_contract | contracts/openapi.yaml / contracts/events.yaml / contracts/webhooks.yaml / contracts/proto/*.proto / N/A | confirmed / pending / N/A | 可选附件路径；不默认要求生成 |
| version_ref | commit / tag / package version / document version / N/A | confirmed / pending / N/A | 同步版本或引用 |

## 阻塞项 / 假设

- [ASSUMPTION] 
- [SPEC-GAP] 
- [STACK-CONTEXT-MISSING] 
- [STACK-DECISION-REQUIRED] 
- [ARCHITECTURE-DECISION-REQUIRED] 
- [STACK-CONFLICT] 
- [ID-FINALIZATION-REQUIRED]
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
