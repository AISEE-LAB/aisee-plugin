---
name: aisee:verify
description: 验证当前 OpenSpec change 的文档、ID、source-map、tasks、contracts、CE review/test 结果和实现状态是否一致。用于实现前后检查缺口、断链、drift、schema artifact 完整性和验证证据。它输出问题清单和修复建议，不负责 archive 放行审批。
---

# aisee:verify

`aisee:verify` 是当前 change 的一致性诊断器，不是 archive 放行器。

## 职责

- 运行或建议运行 `openspec validate`。
- 检查 schema artifact DAG。
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

必须以当前 change 为入口。优先使用 context pack，字段契约见 `references/context-pack-contract.md`：

```bash
aisee context pack --change <change> --for aisee-verify --json
```

同时建议读取 / 运行：

```bash
openspec validate <change>
aisee gaps --change <change> --json
```

如果 CLI 不可用，仍然只从当前 change artifacts、schema、`source-map.md` 指向的路径和已有 review/test evidence 读取；不要自由扩大全项目范围。

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

## Severity

- `BLOCKER`：不能进入 archive-guard，必须先修。
- `RISK`：可以继续，但 archive-guard 需要看到接受理由或补充证据。
- `INFO`：提示项，不阻断。

## 输出

```md
# Aisee Verify Report

## Result

pass / fail / pass-with-risk

## Findings

### BLOCKER
### RISK
### INFO

## Required Fixes

## Evidence Reviewed

## Suggested Next Step
```
