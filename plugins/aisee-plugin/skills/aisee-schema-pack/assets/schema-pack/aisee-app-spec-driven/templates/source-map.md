# Source Map: {{change-name}} / Context Routing

> 编号只是 skill/template 的写作约束，例如 `FR-001`、`SPEC-001`、`API-001`、`TASK-001`。编号用于减少重复命名和临时发明，不要求 CLI 单独追踪。
> Source Map 只记录来源、artifact 适用性、候选影响路径和预期证据类型；不写 contract 细节、不写实现步骤、不写最终验证结论。

## 编号状态

| 检查项 | 状态 | 证据 / 命令 | 备注 |
|---|---|---|---|
| 当前 change 产出编号已稳定 | yes / no / N/A | 文档内编号检查 | |
| 存在临时编号 | yes / no | `[NUMBERING-FINALIZATION-REQUIRED]` | |
| 编号无重复 | yes / no | 当前 change artifacts 本地检查 | |

## Context 摘要

| 项目 | 结果 | 处理 |
|---|---|---|
| status | ready / needs-work / blocked | |
| missing_artifacts |  | 按 artifact_order 补齐；Required=no 且有原因的按需 artifact 不应列入 |
| blockers |  | 停止 author，先处理 |
| warnings |  | 写入阻塞项 / 假设 |
| next_actions |  | 执行后回填本文 |

## 上游来源

| 来源 | 路径 / 描述 | 外部 Ref | 状态 | 备注 |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/... | ticket://... / N/A | 已确认 / 缺失 / N/A | |
| UI Content | aisee/docs/ui-content/... | ticket://... / N/A | 已确认 / 缺失 / N/A | |
| Design Spec / Assets | docs/design/... / assets/... | figma://... / N/A | 已确认 / 缺失 / N/A | |
| Architecture | aisee/docs/architecture/... | issue://... / N/A | 已确认 / 缺失 / N/A | |
| Change Plan | aisee/docs/change-plan/... | N/A | 已确认 / 缺失 / N/A | |
| Issue / 用户输入 | 1-5 句摘要化描述或外部链接 | issue://... / PR URL / N/A | 已确认 / 缺失 / N/A | 不保存原始长提示词全文 |

## 上游输入

| 类型 | Ref / 摘要 | 标题 / 名称 | 来源 | 本 change 处理方式 | 后续 artifact |
|---|---|---|---|---|---|
| FR | docs/requirements/...#FR-001 / N/A | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / tasks |
| NFR | docs/requirements/...#NFR-001 / N/A | | SRS / Architecture | 覆盖 / 部分覆盖 / 不覆盖 | specs / change-context / tasks |
| RULE | docs/requirements/...#RULE-001 / N/A | | SRS | 覆盖 / 部分覆盖 / 不覆盖 | specs / service-contract |
| PAGE | docs/ui-content/...#PAGE-001 | | UI Content | 新增 / 修改 / 复用 / 不覆盖 | ui-contract |
| FLOW | docs/ui-content/...#FLOW-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| STATE | docs/ui-content/...#STATE-001 | | UI Content / SRS | 新增 / 修改 / 复用 / 不覆盖 | specs / ui-contract / service-contract |
| ARCH | docs/architecture/...#ARCH-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context |
| DEC | docs/architecture/...#DEC-001 | | Architecture | 承接 / 局部补充 / 待确认 | change-context |
| CONSTRAINT | docs/architecture/...#CONSTRAINT-001 | | Architecture | 承接 / 不适用 / 待确认 | change-context / contracts / tasks |
| RISK | docs/architecture/...#RISK-001 | | Architecture / Change Plan | 规避 / 接受 / 待确认 | change-context / tasks |

## 本 Change 产出编号

| 类型 | 编号 | 标题 / 名称 | 产生 artifact | 关联来源 / 上游 Ref |
|---|---|---|---|---|
| SPEC | SPEC-001 | | specs/... | docs/requirements/...#FR-001 |
| API | API-001 | | service-contract.md | docs/requirements/...#FR-001 / docs/ui-content/...#PAGE-001 |
| DATA | DATA-001 | | data-model.md | docs/requirements/...#FR-001 / API-001 |
| TASK | TASK-001 | | tasks.md | SPEC-001 / API-001 |
| TEST | TEST-001 | | tasks.md / verification evidence | SPEC-001 |

## 不在本 Change 范围

- 

## Affected Paths Index

> 仅记录候选影响路径和编号关联，供 tasks.md 和实现阶段引用；不要在这里写具体修改步骤。

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

| Artifact | Required | 依据上游 Ref / 编号 | 原因 / N/A 说明 | 相关约束转交 |
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
- [NUMBERING-FINALIZATION-REQUIRED]
- [NUMBERING-CHECK-FAILED]

## 编号与路由规则

- 无前置 planning docs 时，在“上游来源”记录用户输入、issue、ticket 或 PR 摘要即可。不要为了消除空值伪造 `docs/...#FR-001`。
- specs 必须覆盖本 change 的全部 FR。
- change-context.md 仅在 Required=yes 时覆盖 ARCH / DEC / CONSTRAINT / RISK。
- ui-contract.md 仅在 Required=yes 时覆盖 PAGE / FLOW。
- data-model.md 仅在 Required=yes 时覆盖 DATA。
- service-contract.md 仅在 Required=yes 时覆盖 API / backend service / async job / CLI / integration，并满足适用的前端数据需求。
- 每个新增编号稳定后必须回填到“本 Change 产出编号”并记录 owner artifact。
- tasks.md 内新增 TASK / TEST 编号时，按当前文档顺序分配；无法确定最终编号时只使用临时编号。
- tasks.md 生成前必须重新检查当前 change 与 schema，确认 blocker 已清除或明确保留。
- tasks.md 生成前必须确认 Required=yes 的追踪关系闭合；Required=no 的 artifact 必须有明确原因。
