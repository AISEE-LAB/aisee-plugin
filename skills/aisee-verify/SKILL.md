---
name: aisee:verify
description: 验证当前 OpenSpec change 的文档、ID、source-map、tasks、contracts、CE review/test 结果和实现状态是否一致。用于实现前后运行 author-check、gaps、context pack 和 change inspect，检查缺口、断链、drift、schema artifact 完整性和验证证据。它输出问题清单和修复建议，不负责 archive 放行审批。
---

# aisee:verify

`aisee:verify` 是当前 change 的一致性诊断器，不是 archive 放行器。

## 职责

- 运行或建议运行 `openspec validate`。
- 运行 `aisee change author-check <change> --json`、`aisee gaps --change <change> --json`、`aisee context pack --change <change> --for aisee-verify --json`。
- 检查 schema artifact DAG 和 template / artifact 缺失。
- 检查 ID、`source-map.md`、spec、tasks、contracts 的一致性。
- 检查实现后是否出现 spec drift。
- 消费 `ce-doc-review`、`ce-code-review`、`ce-test-*` 结果。
- 输出问题清单和修复建议。

## 不负责

- 创建、拆分或重新规划 change。
- 替代 `ce-code-review` 或重新做完整代码审查。
- 替代测试工具或重新跑完整测试矩阵。
- 修改 artifacts、代码或 baseline specs。
- 判断是否可以执行 `openspec archive`；这是 `aisee:archive-guard` 的职责。

## 输入入口

必须以当前 change 为入口。按顺序运行：

```bash
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee change inspect <change> --json
aisee context pack --change <change> --for aisee-verify --json
```

同时建议运行：

```bash
openspec validate <change>
```

如果 CLI 不可用，仍然只从当前 change artifacts、schema、`source-map.md` 指向的路径和已有 review/test evidence 读取；不要自由扩大全项目范围。

## 输入处理规则

- `author-check.status=blocked`：直接输出 fail，引用 `author-check.blockers`，不要继续推断实现状态。
- `gaps.result.status=blocked`：直接输出 fail，要求回到对应 artifact 修复。
- `change inspect.ids.registry.missing / temporary / inactive` 非空：至少输出 RISK；inactive 或 removed ID 输出 BLOCKER。
- `context pack.facts.derived.checks` 是 verify 的结构化检查入口；不要把 verify 报告当成新事实源。
- `openspec validate` 未运行时，输出 RISK；运行失败且无接受理由时输出 BLOCKER。
- 已有 `ce-doc-review`、`ce-code-review`、`ce-test-*` 结果只作为 evidence；verify 不替代它们。

## 检查项

按以下维度输出 findings：

| 维度 | 检查内容 |
|---|---|
| Schema artifacts | schema 声明的 artifacts 是否存在；N/A artifact 是否写明原因 |
| ID / source-map | 上游 ID、产出 ID、owner artifact、代码路径、测试路径是否闭合 |
| Specs | specs 是否覆盖本 change 的 FR / NFR / RULE / FLOW / STATE |
| Contracts | contracts 是否覆盖 specs 和 source-map 中声明的 UI / service / data / device 约束 |
| Tasks | tasks 是否覆盖实现、验证、证据记录；状态是否真实 |
| Implementation drift | 代码或配置是否偏离 specs/contracts/source-map |
| Review / test evidence | CE P0/P1、测试失败、人工验证缺口是否处理或记录接受理由 |
| Archive readiness signals | 是否存在会阻止 archive-guard 的 blocker |

## Severity

- `BLOCKER`：不能进入 archive-guard，必须先修。
- `RISK`：可以继续，但 archive-guard 需要看到接受理由或补充证据。
- `INFO`：提示项，不阻断。

## 输出

```md
# Aisee Verify Report

## Result

pass / fail / pass-with-risk

## Inputs

- Author check:
- Gaps:
- Change inspect:
- Context pack:
- OpenSpec validate:

## Findings

### BLOCKER
### RISK
### INFO

## Required Fixes

## Evidence Reviewed

## Archive-Guard Readiness

- Ready for archive-guard: yes / no / with-risk
- Reasons:

## Suggested Next Step
```
