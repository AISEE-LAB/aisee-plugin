---
name: aisee:archive-guard
description: OpenSpec archive 前的轻量门禁。用于判断当前 change 是否已经满足归档条件：author-check/gaps/context pack 无 blocker、openspec validate 通过、aisee:verify 无阻断项、tasks 完成、spec/source-map/contracts 同步、CE P0/P1 review 处理、verification 记录满足 domain/schema 要求。它不重新做深度验证、不重新跑完整测试、不替代 openspec archive。
---

# aisee:archive-guard

`aisee:archive-guard` 是 archive 前的放行判断，不是深度验证器。

## 职责

- 读取已有 validate、verify、review、test、verification 结果。
- 运行或读取 `aisee change author-check <change> --json`、`aisee gaps --change <change> --json`、`aisee change archive-check <change> --json`、`aisee context pack --change <change> --for aisee-verify --json`。
- 判断是否可以执行 `openspec archive <change>`。
- 输出可以 archive / 暂不建议 archive / 有风险但可接受。

## 不负责

- 重新规划 change。
- 重新做代码 review。
- 重新跑完整测试。
- 修改 change artifacts。
- 修改 baseline specs。
- 替代 `openspec archive`。

## 归档前检查

- `aisee change author-check <change> --json` 无 blocker，且 `missing_artifacts` 已处理。
- `aisee change archive-check <change> --json` 无 blocker，或所有 risk 已有接受理由。
- `aisee gaps --change <change> --json` 为 clear，或 risk 已有接受理由。
- `aisee context pack --change <change> --for aisee-verify --json` 可生成，且无 archive 阻断项。
- `openspec validate <change>` 已通过，或失败项已有明确处理结论。
- `aisee:verify` 无未处理 blocker。
- `tasks.md` 的实现任务和验证任务已完成或明确标注 N/A / accepted risk。
- `source-map.md` 的 ID、代码路径、测试路径和验证证据没有断链。
- `specs/**` 与实现后的行为一致，没有未处理 spec drift。
- app schema 的 `change-context.md`、`ui-contract.md`、`service-contract.md`、`data-model.md` 或 device schema 的 `design.md` / contracts 已同步最终实现事实。
- CE P0/P1 review 结果已修复或记录接受理由。
- 测试、人工验证、截图、日志或设备验证证据已记录在 `tasks.md` 或 schema 指定位置。

## 判定规则

- 有任一 blocker：`暂不建议 archive`。
- 只有 risk，且每项都有接受理由、owner 和后续处理方式：`有风险但可接受`。
- validate、verify、tasks、source-map、review/test evidence 全部闭合：`可以 archive`。
- 如果缺少 verify 报告或 validate 未运行，不得给出 `可以 archive`，最多给出 `暂不建议 archive` 或 `有风险但可接受`。

## 推荐命令顺序

```bash
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee change archive-check <change> --json
aisee context pack --change <change> --for aisee-verify --json
openspec validate <change>
```

确认无 blocker 后才建议：

```bash
openspec archive <change>
```

## 输出

```md
# Archive Guard

## Decision

可以 archive / 暂不建议 archive / 有风险但可接受

## Evidence

- Author check:
- Gaps:
- Context pack:
- OpenSpec validate:
- Verify report:
- Review / test evidence:

## Blocking Items

## Accepted Risks

## Baseline Impact

- 是否需要回写 baseline specs:
- 归档后需确认的 spec 路径:

## Next Command

`openspec archive <change>`
```
