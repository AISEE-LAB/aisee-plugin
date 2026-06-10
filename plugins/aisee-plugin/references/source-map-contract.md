# Source Map Contract

本文是 `source-map.md` 结构化解析规则的维护源。

`source-map.md` 是 Aisee 的 OpenSpec companion artifact。OpenSpec 负责管理它是否属于 change、是否存在和是否归档；Aisee CLI 负责解析其中的上下文路由语义。

## Boundary

Aisee CLI 只结构化解析 `source-map.md`，不把其它 OpenSpec artifacts 变成业务语义 parser。

`source-map.md` 只适用于当前 schema 明确生成 source-map 的 change。缺少结构化表格时，CLI 必须降级为 L0 metadata scan，不得失败或猜测自由文本语义。

JSON 字段名保持兼容：`Affected Paths Index` 解析后输出为 `implementation_paths`，`Expected Evidence Index` 解析后输出为 `verification_evidence`，`Contract Ownership / Sync` 解析后输出为 `contract_sync`。兼容字段名中的 `local_ids` / `anchor_refs` 表示解析到的短编号或 `path#编号` source ref。

## Required Sections

### Upstream Sources

中文标题可用 `上游来源`、`上游规划来源` 或 `上游事实来源`。

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/auth-srs.md | aisee/docs/requirements/auth-srs.md#FR-001 | confirmed | |
| user-input | 登录改造摘要 | issue://AUTH-9 | confirmed | |

Rules:

- `Path / Description` 可以是文件路径、URL 或经过压缩的人工输入说明。
- `Ref` 可以是 `path#编号`、外部 issue/ticket/PR 引用或 `N/A`。
- 无前置 planning docs 时，在本表记录用户输入、issue、ticket 或 PR 摘要；不要伪造 SRS 或 UI 引用。
- `Status` 建议使用 `confirmed / missing / N/A / risk`，中文可写 `已确认 / 缺失 / N/A / 风险`。

### Source Context

中文标题可用 `来源上下文`、`Context Routing`、`上游输入`、`本 Change 覆盖` 或 `本 Change 产出`。

| Type | Ref | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | aisee/docs/requirements/auth-srs.md#FR-001 | 用户登录 | SRS | covered | specs/auth.md |
| SPEC | SPEC-001 | 登录规格 | current change | produced | specs/auth.md |

Rules:

- 已有 planning docs 使用 `path#编号`。
- 当前 change 新产出的对象只写短编号，例如 `SPEC-001`、`API-001`、`TASK-001`、`TEST-001`。
- 无前置文档时允许只出现当前 change 产出编号；这不是缺口。
- 不要为了满足模板创建无用编号或无用来源引用。

### Artifact Applicability

中文标题可用 `Artifact 适用性`。

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | SPEC-001 | 需要后端接口 | tasks.md |

Rules:

- `Required` 使用 `yes / no`。
- `Required=no` 时必须写 `Reason`。
- app 和 device 可以列不同 artifacts。
- 对 app schema，`proposal.md`、`source-map.md`、`specs/**/*.md`、`tasks.md` 是最小闭环；`change-context.md`、`ui-contract.md`、`service-contract.md`、`data-model.md` 按本表 Required=yes/no 决定是否展开。
- `Required=no` 且有原因时，CLI 不应把缺失的按需 artifact 报为 missing artifact。

### Contract Ownership / Sync

中文标题可用 `契约归属`、`契约同步` 或 `Contract Sync`。

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | |
| canonical_source | contracts/openapi.yaml | confirmed | |
| provider_repo | backend-api | confirmed | |
| consumer_repo | frontend-app | confirmed | |
| sync_mode | local-http | confirmed | |
| conflict_rule | canonical-source-wins | confirmed | |
| machine_readable_contract | contracts/openapi.yaml | confirmed | |
| version_ref | commit:abc123 | confirmed | |

Rules:

- 本表用于前后端分仓、BFF、独立契约仓库或外部服务场景。
- `service-contract.md` Required=yes 时建议填写本表；缺失时 verify 应输出契约同步风险。
- `machine_readable_contract` 只登记可选附件路径，例如 `contracts/openapi.yaml`、`contracts/events.yaml`、`contracts/webhooks.yaml` 或 `contracts/proto/*.proto`；不要求默认生成。
- 本表只记录同步路由和权威来源，不写接口字段、错误码或业务规则。

### Affected Paths Index

中文标题可用 `影响路径索引`、`候选影响路径`、`实现路径`、`代码路径` 或 `Implementation Paths`。

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | SPEC-001 | modify | |
| test | tests/auth/test_session.py | TEST-001 | add | |

Rules:

- `Kind` 建议使用 `code / test / config / docs / asset / reference`。
- 对生成 source-map 的 schema，`ce-work` 的 `allowed_paths` 优先来自这里；缺表时只能从 `source-map.md` 本文 metadata fallback，并输出 risk。
- artifact 文本中提到但未在本表声明的实现路径只能进入 `unmapped_reference_paths` 和 gap，不能自动放行。
- 没有本表时，CLI 可以从 source-map 全文路径降级抽取。

### Expected Evidence Index

中文标题可用 `预期证据索引`、`验证证据` 或 `Verification Evidence`。

| Type | Path / Command | Status | Refs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | expected | TEST-001 | |

Rules:

- `Status` 在 author 阶段可使用 `expected / N/A`，实现后证据可使用 `passed / failed / blocked / risk / pending`。
- evidence 文件的轻量状态仍由 `docs/verification/**` 解析。

### Out of Scope / Follow-up

中文标题可用 `不在本 Change 范围`、`Follow-up` 或 `后续处理`。

Use bullets. 如需引用对象，优先使用短编号或 `path#编号` source ref。

## CLI Behavior

- Missing `source-map.md` is a blocker for schema changes that require it.
- Missing structured tables is a risk, not a hard failure; CLI falls back to numbering/path/heading scan.
- Table parsing never overrides source files. It only builds context pack routing data.
- Free text is not parsed for business semantics.
