# Context Pack Targets

本文是 `aisee context pack --for <target>` 的 target-specific 规则维护源。核心 envelope 和通用字段见 [context-pack-contract.md](context-pack-contract.md)。

## ce-work Pack

`--for ce-work` 面向实现阶段，只输出当前 change 的可执行上下文。

Required additions:

```json
{
  "facts": {
    "derived": {
      "execution": {
        "start_from": [],
        "suggested_order": [],
        "allowed_paths": [],
        "unmapped_reference_paths": [],
        "forbidden_scope": [],
        "requires_ce_plan": false,
        "ce_plan_reason": null,
        "reusable_workflow_candidates": [
          {
            "name": "aisee:implementation-bridge",
            "kind": "aisee-skill",
            "status": "recommended",
            "reason": "preflight author-check, gaps, context pack, scope guardrails, and review recommendation before CE execution"
          }
        ]
      }
    }
  },
  "guardrails": [
    "follow current schema apply tracks",
    "do not create a parallel durable plan",
    "report out-of-scope findings as follow-up candidates"
  ]
}
```

Rules:

- 对生成 `source-map.md` 的 schema，`allowed_paths` 只来自 `source-map.md` 的 `Affected Paths Index`；缺表时输出 risk，不做隐式 fallback。
- artifact 文本提到但未在 source-map 声明的路径只能作为 `unmapped_reference_paths` 和 gap 输出。
- 对不生成 `source-map.md` 的 schema，`allowed_paths` 来自当前 schema artifacts / apply tracks 的显式路径引用；缺路径时要求补当前 schema artifact，而不是创建假 source-map。
- 如果当前 schema apply tracks 太粗、路径缺失或 contract 冲突，`requires_ce_plan` 可以为 `true`，但 `ce-plan` 结论必须回写当前 schema apply tracks；仅 source-map schema 需要回写 `source-map.md`。
- `reusable_workflow_candidates` 是路由提示，不是事实源；item 必须包含 `name`、`kind`、`status`、`reason`。
- `kind` 只能表达能力来源，例如 `aisee-skill` 或 `compound-skill`；不能表达事实源。
- `status` 使用 `required`、`recommended`、`available`、`missing`：Aisee 修补 gate 用 `required/recommended`，CE skill 可用性用 `available/missing`。
- 有 blocker gap 时，候选只应要求回到 `aisee:change-author` 修补 artifacts/traceability，不应继续推荐 `ce-plan` 或 `ce-work`。
- 无 blocker 且 `requires_ce_plan=true` 时，候选包含 `aisee:implementation-bridge` 和 `ce-plan`，并用 `ce_plan_reason` 说明为什么只做执行细化。
- 无 blocker 且 `requires_ce_plan=false` 时，候选包含 `aisee:implementation-bridge` 和 `ce-work`。
- 不包含完整 SRS / UI Content / Architecture 正文，只包含当前 change 追踪到的 ID、路径和必要摘录。
- 未纳入当前 change 的问题可以放入 `follow_up_candidates`，不能进入 `suggested_order`。

## aisee-verify Pack

`--for aisee-verify` 面向一致性诊断，范围比 `ce-work` 更宽，但仍以当前 change 为入口。

Required additions:

```json
{
  "facts": {
    "derived": {
      "checks": {
        "schema_artifacts": [],
        "traceability": [],
        "tasks": [],
        "contracts": [],
        "implementation": [],
        "review_and_tests": []
      },
      "drift_candidates": []
    }
  },
  "evidence": {
    "openspec_validate": null,
    "ce_doc_review": [],
    "ce_code_review": [],
    "tests": [],
    "manual_verification": [],
    "details": {
      "openspec_validate": null,
      "reviews": [],
      "tests": [],
      "manual_verification": [],
      "accepted_risks": []
    }
  }
}
```

Rules:

- `aisee-verify` 可以检查实现后代码/test evidence 是否偏离 specs/contracts。
- 发现未被当前 change 纳入范围的问题，应输出为 gap 或 follow-up，不直接扩大当前 change。
- `aisee-verify` 不做 archive 放行审批；archive 结论属于 `aisee:archive-guard`。
- `evidence.details` 是对 review/test/validate 文件的轻量解析结果，保留原始路径数组以兼容旧消费者。
- review finding 中未关闭的 P0/P1 必须进入 verify/archive 门禁；`accepted risk` 或“接受风险”可作为关闭依据，但不能替代 owner 文档修复。
- `openspec_validate` 或 test evidence 显示 failed 时必须输出 blocker；unknown 状态至少输出 risk。

## ce-doc-review Pack

`--for ce-doc-review` 面向文档审核阶段，重点检查 schema artifacts、traceability、tasks、contracts 和 open questions。

Rules:

- 只审当前 change 的文档，不重新做 SRS 或 change 边界规划。
- 必须暴露 schema artifact DAG、缺失 artifact、ID trace、source-map gaps 和 open questions。
- 不应生成实现任务之外的长期计划；有效结论应回写当前 OpenSpec artifacts。

## ce-code-review Pack

`--for ce-code-review` 面向实现后代码审查，重点检查 implementation、tests、source-map / schema-artifacts 和 task_state。

Rules:

- 只把当前 change 声明或推导允许的代码/测试路径作为 review 范围入口。
- `unmapped_reference_paths` 只能作为风险提示，不自动进入审查范围。
- 必须携带 verify/test/review evidence 入口，方便审查实现和证据是否一致。
