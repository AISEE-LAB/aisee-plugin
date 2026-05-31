# Tasks: {{change-name}}

## 生成前一致性检查

- [ ] 已运行 `aisee change author-check {{change-name}} --json`，且无 blocker。
- [ ] `author-check.missing_artifacts` 已处理，所有 N/A artifact 已写明原因。
- [ ] `author-check.ids.actions.reserve / activate` 已执行，或已在 source-map.md 标注 `[ID-RESERVATION-REQUIRED]`。
- [ ] 每个 FR 已映射到 specs。
- [ ] Architecture 相关 ARCH / DEC / CONSTRAINT / RISK 已映射到 change-context.md。
- [ ] 涉及页面的 FR 已映射到 ui-contract.md。
- [ ] 涉及接口的 FR 已映射到 service-contract.md。
- [ ] 涉及持久化的 FR 已映射到 data-model.md。
- [ ] N/A artifact 已写明原因。
- [ ] source-map.md 已回填新增 SPEC / API / DATA / TASK / TEST ID 的 owner artifact。
- [ ] source-map.md 的阻塞项已处理或明确保留风险。
- [ ] 新增 TASK / TEST ID 已通过 `aisee id reserve` 预留，或已标注 `[ID-RESERVATION-REQUIRED]`。

## 1. 规格与上下文确认

- [ ] 1.1 确认 source-map.md 覆盖范围与 proposal.md 一致。
- [ ] 1.2 确认 specs 覆盖全部本 change 的 FR。
- [ ] 1.3 确认 change-context.md 的架构约束和风险没有未处理阻塞项。

## 2. 实现

- [ ] {{scope}}:TASK-001 实现 {{scope}}:SPEC-001 对应行为，并满足相关 contract。
- [ ] {{scope}}:TASK-002 更新 source-map.md 中本任务覆盖的追踪关系。

## 3. 验证

- [ ] {{scope}}:TEST-001 验证 specs 中的验收场景。
- [ ] {{scope}}:TEST-002 验证 UI / API / 数据 / 架构约束追踪关系闭合。
- [ ] {{scope}}:TEST-003 运行相关测试和检查命令。

## 4. 收尾

- [ ] 4.1 更新必要文档或示例。
- [ ] 4.2 确认无未处理的 [SPEC-GAP] / [STACK-CONFLICT]。
- [ ] 4.3 运行 `aisee change author-check {{change-name}} --json` 并记录状态。
- [ ] 4.4 运行 `aisee gaps --change {{change-name}} --json` 并记录状态。
- [ ] 4.5 运行 / 记录 `aisee:verify` 结果。
- [ ] 4.6 归档前运行 / 记录 `aisee:archive-guard` 结果。

## 追踪矩阵

| TASK / TEST ID | 类型 | 覆盖对象 | 证据 / 命令 | 状态 |
|---|---|---|---|---|
| {{scope}}:TASK-001 | 实现 | {{scope}}:FR-001 / {{scope}}:API-001 | | 未开始 / 进行中 / 完成 |
| {{scope}}:TEST-001 | 验证 | {{scope}}:SPEC-001 | | 未开始 / 通过 / 失败 / N/A |

## Author / Verify / Archive 复查记录

| 命令 | 状态 | blocker | risk | 备注 |
|---|---|---:|---:|---|
| `aisee change author-check {{change-name}} --json` | ready / needs-work / blocked | | | |
| `aisee gaps --change {{change-name}} --json` | clear / risk / blocked | | | |
| `aisee:verify` | pass / pass-with-risk / fail | | | |
| `aisee:archive-guard` | 可以 archive / 有风险但可接受 / 暂不建议 archive | | | |
