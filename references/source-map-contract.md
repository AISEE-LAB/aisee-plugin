# Source Map Contract

`source-map.md` 是 Aisee 的 OpenSpec companion artifact。OpenSpec 负责管理它是否属于 change、是否存在和是否归档；Aisee CLI 负责解析其中的路由语义。

## Boundary

Aisee CLI 只结构化解析 `source-map.md`，不把其它 OpenSpec artifacts 变成业务语义 parser。

`source-map.md` 可以按 app、device、infra 或 quick-fix 使用不同内容，但应尽量保留以下最小表格。缺少表格时，CLI 必须降级为 L0 metadata scan，不得失败或猜测自由文本语义。

## Required Sections

### Upstream Sources

中文标题可用 `上游来源`、`上游规划来源` 或 `上游事实来源`。

| Source | Path / Description | Source ID | Status | Notes |
|---|---|---|---|---|
| SRS | docs/requirements/auth-srs.md | SRC-001 | confirmed | |

Rules:

- `Path / Description` 可以是文件路径、URL 或人工输入说明。
- `Status` 建议使用 `confirmed / missing / N/A / risk`，中文可写 `已确认 / 缺失 / N/A / 风险`。

### ID Trace

中文标题可用 `上游输入 ID`、`本 Change 覆盖` 或 `本 Change 产出 ID`。

| Type | ID | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | auth:FR-001 | 用户登录 | SRS | covered | specs / tasks |

Rules:

- `ID` 必须使用完整 ID，例如 `auth:FR-001`。
- 产出 ID 可通过 `Artifact` 指向 owner artifact。
- 不覆盖的 ID 应写入 `Handling`，不要删除。

### Artifact Applicability

中文标题可用 `Artifact 适用性`。

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | auth:API-001 | 需要后端接口 | tasks.md |

Rules:

- `Required` 使用 `yes / no`。
- `Required=no` 时必须写 `Reason`。
- app 和 device 可以列不同 artifacts。
- 对 app schema，`proposal.md`、`source-map.md`、`specs/**/*.md`、`tasks.md` 是最小闭环；`change-context.md`、`ui-contract.md`、`service-contract.md`、`data-model.md` 按本表 Required=yes/no 决定是否展开。
- `Required=no` 且有原因时，CLI 不应把缺失的按需 artifact 报为 missing artifact。

### Implementation Paths

中文标题可用 `实现路径`、`代码路径` 或 `Implementation Paths`。

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |
| test | tests/auth/test_session.py | auth:TEST-001 | add | |

Rules:

- `Kind` 建议使用 `code / test / config / docs / asset / reference`。
- `ce-work` 的 `allowed_paths` 只来自这里。
- artifact 文本中提到但未在本表声明的实现路径只能进入 `unmapped_reference_paths` 和 gap，不能自动放行。
- 没有本表时，CLI 可以从 source-map 全文路径降级抽取。

### Verification Evidence

中文标题可用 `验证证据`、`Verification Evidence`。

| Type | Path / Command | Status | IDs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | passed | auth:TEST-001 | |

Rules:

- `Status` 使用 `passed / failed / blocked / risk / pending`。
- evidence 文件的轻量状态仍由 `docs/verification/**` 解析。

### Out of Scope / Follow-up

中文标题可用 `不在本 Change 范围`、`Follow-up` 或 `后续处理`。

Use bullets. IDs should be complete when present.

## CLI Behavior

- Missing `source-map.md` is a blocker for app/device schema changes that require it.
- Missing structured tables is a risk, not a hard failure; CLI falls back to ID/path/heading scan.
- Table parsing never overrides source files. It only builds context pack routing data.
- Free text is not parsed for business semantics.
