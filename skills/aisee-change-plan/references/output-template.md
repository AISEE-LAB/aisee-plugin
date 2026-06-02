# aisee:change-plan — Output Template

输出必须保存到 `docs/change-plan/`，并向用户返回保存路径和 `/opsx:new` 命令。

## 输出顺序

1. 摘要
2. 依赖图
3. Change 详情
4. 全部命令
5. 整体理由

## 摘要

```text
N 个 changes · M 个 phases · 预计总计 X 周 · Y 个可并行
```

任何估计为 XL（>14 天）的 change 都要标记风险。

## 依赖图

简单依赖链使用 ASCII：

```text
Phase 1（顺序执行）:
  [change-name-1] -> [change-name-2]

Phase 2（Phase 1 后可并行）:
  [change-name-3]
  [change-name-4]
```

复杂依赖追加表格：

| Change | 依赖 | 可并行 |
|---|---|---|
| change-name-3 | change-name-2 | change-name-4 |

## Change 详情模板

```text
─────────────────────────────────────────────────
change N/total

Name:         change-name-kebab-case
Title:        可读标题
Schema:       aisee-app-spec-driven | quick-fix | quick-research | aisee-device-spec-driven | aisee-docsite-driven | infra-change | security-audit | spec-driven | opsx-collab-pr-loop
Complexity:   S | M | L

Description:
  用一句话说明该 change 交付什么。

Schema rationale:
  - 为什么选择该 schema。
  - 如果不是 aisee-app-spec-driven，说明为什么不需要 SRS / UI Content / Architecture 追踪。
  - Required upstream docs: SRS / UI Content / Design Spec / Design Assets / Architecture / Issue / PR / none

In Scope:
  - 具体范围 1 (<scope>:FR-001)
  - 具体范围 2 (<scope>:PAGE-001 / N/A)

Out of Scope:
  - 明确排除事项 1
  - 明确排除事项 2

Source-map seed:
  - If schema does not generate source-map.md: N/A — schema does not generate source-map.md
  - If schema generates source-map.md:
      Upstream:
        FR:          <scope>:FR-001, <scope>:FR-002
        NFR/RULE:    <scope>:NFR-001, <scope>:RULE-001 (or "N/A")
        PAGE/FLOW:   <scope>:PAGE-001, <scope>:FLOW-001 (or "N/A")
        DESIGN:      Design Spec / Design Assets / dev-visual-brief refs (or "N/A")
        ARCH/DEC:    <scope>:ARCH-001, <scope>:DEC-001 (or "N/A")
        CONSTRAINT:  <scope>:CONSTRAINT-001 (or "N/A")
        RISK:        <scope>:RISK-001 (or "N/A")
      Change impact:
        Existing / Changed / New / Deprecated / Unknown objects and N/A reasons
      APP schema fields:
        SPEC: TBD in change-author
        API:  TBD in service-contract
        DATA: TBD in data-model
        TASK: TBD in tasks
        TEST: TBD in tasks / verification evidence
      DEVICE schema fields:
        HW:  expected HW IDs or "TBD in hardware-contract"
        FW:  expected FW IDs or "TBD in firmware-contract"
        RT:  expected RT IDs or "TBD in runtime-contract"
        VER: expected VER IDs or "TBD in verification-contract"
      Artifact applicability:
        - change-context.md: yes/no — 原因
        - ui-contract.md: yes/no — 原因
        - data-model.md: yes/no — 原因
        - service-contract.md: yes/no — 原因
        - hardware-contract.md: yes/no — 原因
        - firmware-contract.md: yes/no — 原因
        - runtime-contract.md: yes/no — 原因
        - verification-contract.md: yes/no — 原因

Depends on:    change-name（或 none）
Parallel with: change-name, change-name（或 none）

Change rationale:
  说明为什么这是自然边界，以及它为什么可以独立交付。

Command:
  /opsx:new "change-name-kebab-case" --schema <selected-schema>
─────────────────────────────────────────────────
```

## 全部命令

```bash
# Phase 1
/opsx:new "change-name-1" --schema <selected-schema>

# Phase 2 — 可并行运行
/opsx:new "change-name-2" --schema <selected-schema>
/opsx:new "change-name-3" --schema <selected-schema>
```

## 整体理由

用 2-4 句话说明：

- 为什么选择这些边界。
- 主要顺序约束是什么。
- 需求中最不确定的部分是什么。
- Phase 2 中记录的 `[ASSUMPTION]`。

Assumption 格式：

```text
[ASSUMPTION] {假设内容} — 影响 {change 列表} — 开始实现前请确认。
```

## 保存输出

保存到：

```text
docs/change-plan/<YYYY-MM-DD>-<requirement-slug>.md
```

保存后输出：

```text
Change plan 已保存：docs/change-plan/{filename}.md
{N} 个 changes · {M} 个 phases · {Y} 个可并行
```

然后提示先运行 Phase 1 的 `/opsx:new` 命令，再使用 `aisee:change-author`（必要时配合 `/opsx:continue`）按 schema 补齐 artifacts。
