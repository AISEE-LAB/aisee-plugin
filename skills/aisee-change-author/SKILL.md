---
name: aisee:change-author
description: 将 aisee:change-plan 的结果转成 OpenSpec change artifacts 初稿。用于单个已确认 change 的 proposal、change-context、spec、tasks、source-map、ui/service/data contract 或 hardware/firmware/runtime/verification contract 编排。它不拆 change 边界、不写代码；仅当当前 schema 明确包含 design.md 时才调用 aisee:change-design。
---

# aisee:change-author

`aisee:change-author` 是 OpenSpec change 产物编排器。

## 职责

- 读取 change-plan、SRS、UI/device context、architecture 和项目事实。
- 识别当前 schema 需要哪些 artifacts。
- 生成 artifacts 前检查 `.aisee/id-registry.json` 和 `source-map.md` 的 ID 状态。
- 需要新增正式 ID 时，先通过 `aisee id reserve` 获取，不允许 AI 临时编正式编号。
- 为单个 OpenSpec change 创建或补齐 artifacts 初稿。
- 通过 ID 和 `source-map.md` 串联上游产物、spec、tasks、代码路径和验证。
- 对 `change-context.md` 承接 Architecture 的本 change 局部上下文。
- 仅当 schema 明确包含 `design.md` 时，调用或复用 `aisee:change-design` 规则。

## 不负责

- 拆 change 边界。
- 为多个 change 规划 schema。
- 写代码。
- 让 `ce-plan` 生成长期任务清单。

## Author 子阶段

```text
ID registry preflight -> aisee id check / reserve / activate
change-context.md -> app architecture context author
design.md -> only when schema generates design.md, use aisee:change-design
ui-contract.md / service-contract.md / data-model.md -> app domain author
hardware-contract.md / firmware-contract.md / runtime-contract.md / verification-contract.md -> device domain author
source-map.md -> ID trace + sources + OpenSpec artifacts
```

## ID 规则

- 正式 ID 必须来自 `.aisee/id-registry.json`，不得由 AI 直接发明。
- 新增 `FR / NFR / RULE / PAGE / FLOW / STATE / ARCH / DEC / CONSTRAINT / RISK / SPEC / API / DATA / TASK / TEST` 前，先使用 `aisee id reserve --scope <scope> --type <TYPE> --count <N> --json`。
- 写入 artifact 后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活。
- 交付前运行或要求运行 `aisee id check --json`。
- 如果 Aisee CLI 或 ID registry 不可用，只能写临时占位符，例如 `{{scope}}:API-NEW-001`，并在 `source-map.md` 标注 `[ID-RESERVATION-REQUIRED]`。不要声称占位符是正式 ID。
