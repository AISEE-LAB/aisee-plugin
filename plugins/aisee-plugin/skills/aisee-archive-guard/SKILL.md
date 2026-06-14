---
name: aisee:archive-guard
description: OpenSpec archive 前的 schema-aware 最终门禁。用于读取当前 change artifacts、openspec validate、aisee:verify、tasks、review/test/manual evidence，判断是否建议执行 openspec archive。它只按当前 schema 的 artifacts、apply tracks、source-map/contracts 适用性和 domain evidence 做放行判断，不重新做深度验证、不重新跑测试、不替代 openspec archive。
---

# aisee:archive-guard

`aisee:archive-guard` 是 `openspec archive <change>` 前的最终放行建议器。它不创建新事实源，不替代 `aisee:verify`，也不替代 OpenSpec archive；OpenSpec artifact 合法性和 baseline merge 仍以 `openspec validate` / `openspec archive` 为准。

## Reviewer lens evidence 边界

Archive 前可以消费 Aisee 只读 reviewer 结论，但不得把它们当作 CE review/test 的替代品：

- `aisee-change-architect`、`aisee-spec-reviewer`、`aisee-implementation-reviewer` 只能证明 OpenSpec / schema / evidence 一致性。
- CE P0/P1、failed tests、failed validate、安全 High/Critical、设备必需验证缺失等仍按本 skill 的 blocker 规则处理。
- 接口、UI、硬件、固件、安全和验证 lenses 只帮助判断当前 schema evidence 是否闭合，不产生新的 archive 事实源。

触发时机：

- `aisee-implementation-reviewer`：archive guard 前可消费其结论，作为实现/evidence 一致性输入。
- `aisee-spec-reviewer`：仅在 archive guard 发现 artifacts/contracts/source-map/tasks 仍不闭合时建议回退触发。
- `aisee-change-architect`：仅在 archive guard 发现 change 边界或拆分错误时建议回退触发。

## 职责

- 识别当前 change schema，并按 schema 判断归档必需 artifacts、tasks、apply tracks、source-map、contracts 和验证证据。
- 读取已有 validate、verify、review、test、manual verification、preview、monitoring 或设备验证结果。
- 检查 `aisee:verify` 的 Review Recommendation 是否已有审查证据、本地重点自审证据或正式 accepted risk。
- 判断是否建议执行 `openspec archive <change>`。
- 输出 `可以 archive` / `有风险但可接受` / `暂不建议 archive`，并列出阻断项、接受风险和归档后基线影响。

## 不负责

- 创建、拆分或重新规划 change。
- 重新做 `aisee:verify`、代码 review、文档 review 或完整测试。
- 修改 change artifacts、代码、baseline specs 或 evidence。
- 替代 `openspec validate`、`openspec archive` 或自行判断 OpenSpec baseline merge 合法性。
- 为轻量 schema 强制补 app schema 才需要的 `source-map.md`、contracts 或 specs。
- 批准没有 owner、理由和后续处理方式的 accepted risk。

## 输入入口

按顺序读取或运行：

```bash
openspec validate <change>
```

同时读取当前 change 中记录的 `aisee:verify` 结果、CE review/test evidence、人工验证记录、构建/预览/监控/设备验证记录。

确认无 blocker 后才建议：

```bash
openspec archive <change>
```

## Schema 上下文

先确认：

- `schema_name`：当前 schema 名称。
- `source_map_required`：schema 是否生成 `source-map.md`。
- `apply_tracks`：schema archive 前必须关闭的任务或文件，通常是 `tasks.md`。
- `required_artifacts`：schema 声明且未标 N/A 的 artifacts。
- `required_contracts`：仅 source-map schema 中 Required=yes 的按需 artifacts。
- `domain_evidence`：当前 schema 特有的归档证据，如 docsite 构建/链接、infra 回滚/变更后验证、security review/test、device 验证记录。

如果当前 schema 不生成 `source-map.md`，`source_map_required=false` 应直接从当前 schema 判断；不要要求补伪 source-map。

## 归档前检查

- 若 blocker 来自 `SCHEMA_METADATA_MISSING` / `SCHEMA_MISMATCH` / `SCHEMA_NOT_INSTALLED` / `SCHEMA_NOT_FOUND`，必须先回到 change metadata 或 schema 安装修复；不得 archive。
- `aisee:verify` 无未处理 BLOCKER。
- `openspec validate <change>` 已通过。未运行或失败时，不得输出 `可以 archive`。
- `tasks.md` 或 schema apply tracks 中的实现、验证、证据记录和 archive gate 任务已关闭；N/A 必须有原因。
- 需要 `source-map.md` 的 schema：ID、Required=yes contracts、代码路径、测试路径和 evidence 必须闭合；Required=no contracts 以 source-map N/A 原因为准。
- 不生成 `source-map.md` 的 schema：只检查 schema artifacts、tasks/apply tracks、当前 artifacts 明确引用的路径和 schema 所需 evidence。
- 如果 `aisee:verify` 建议 Tier 2 code review，必须存在 CE / harness 审查 evidence、本地重点自审 evidence，或带 owner、理由、影响范围和后续处理方式的 accepted risk；否则不得输出 `可以 archive`。
- CE P0/P1、failed validate、failed test evidence、未处理安全 High/Critical、infra 回滚不可执行、device 必需验证缺失，均视为 archive blocker。
- accepted risk 只能在有 owner、理由、影响范围和后续处理方式时成立；否则仍按 blocker 或 risk 输出。

## Schema 归档门槛

| Schema 类型 | archive 前必须闭合 | 不作为默认阻断 |
|---|---|---|
| `aisee-app-spec-driven` | validate、verify、tasks、source-map、specs、Required=yes contracts、代码/测试/evidence 追踪 | Required=no contracts 展开全文 |
| `aisee-device-spec-driven` | validate、verify、tasks、source-map、device specs、固件/硬件/验证证据 | app-only contracts |
| `quick-fix` | problem/solution/tasks 已完成；修复验证、回滚或监控记录存在；validate 通过 | SRS、specs、source-map、contracts |
| `quick-research` | question/findings/recommendation 完整；结论回答原问题；依据可追溯；validate 通过 | 生产实现、测试矩阵、source-map |
| `aisee-docsite-driven` | proposal/doc-change/tasks 完成；构建、链接、预览或人工校对证据；Archive Updates 已处理 | app specs/contracts/source-map |
| `infra-change` | impact、rollback、tasks 完成；预检、变更后验证、回滚可行性证据 | app contracts/UI/data specs |
| `security-audit` | threat-model、security specs/design/tasks、security review/test evidence；Critical/High 已修复或正式接受 | 非安全相关冗余 contract |

## 判定规则

- `暂不建议 archive`：存在 blocker；validate 未运行或失败；verify 缺失且无等价证据；tasks/apply tracks 未关闭；P0/P1 未处理；schema 必需 evidence 缺失；verify 建议 Tier 2 review 但没有审查 evidence 或 accepted risk。
- `有风险但可接受`：无 blocker，但存在 risk；每项 risk 均有 owner、接受理由、影响范围和后续处理方式。
- `可以 archive`：validate 通过、verify 无 blocker、tasks/apply tracks 关闭、schema 必需 artifacts/evidence 闭合，且无未接受 risk。

如果缺少 `aisee:verify` 报告，不得给出 `可以 archive`；最多输出 `有风险但可接受`，并说明缺少的门禁证据。

## 输出

```md
# Archive Guard

## Decision

可以 archive / 暂不建议 archive / 有风险但可接受

## Schema Context

- Schema:
- Source-map required: yes / no
- Apply tracks:
- Required artifacts:
- Required contracts:
- Domain evidence:

## Evidence

- Author check:
- Gaps:
- Verify check:
- Archive check:
- OpenSpec validate:
- Aisee verify report:
- Review / test / manual evidence:

## Review Gate

- Review recommendation from verify:
- Review evidence:
- Local self-review fallback:
- Accepted risk, if any:

## Blocking Items

## Accepted Risks

## Baseline Impact

- 是否需要回写 baseline specs / project docs:
- 归档后需确认的路径:
- 不应进入 baseline 的临时材料:

## Next Action

- If `可以 archive`: `openspec archive <change>`
- If `有风险但可接受`: record accepted risks, then decide whether to run `openspec archive <change>`
- If `暂不建议 archive`: fix blocking items first
```
