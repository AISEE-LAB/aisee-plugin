# Context Pack Contract

`aisee context pack` 是 OpenSpec context companion。它默认调用时衔接 OpenSpec change、Aisee 补充信息和 CE evidence，不维护第二份内容事实源，也不替代 OpenSpec parser。

事实源：

- OpenSpec artifacts / Markdown：内容事实源。
- `.aisee/id-registry.json`：ID 分配和生命周期事实源。
- `.aisee/sources.json`：change 外部 Aisee 产物来源登记事实源。
- `.aisee/cache/context-index.json`：可删除、可重建缓存，不是事实源。

默认输出只包含：

- `parsed`：从 Aisee 自有补充文件、OpenSpec metadata scan 和可用 OpenSpec CLI 输出解析。
- `derived`：根据 source-map、ID registry、文件关系和校验规则推导。

AI 生成摘要必须显式启用，并在 JSON 中标记为 `generated`。

## OpenSpec Boundary

Aisee CLI 不解析 OpenSpec 已负责的规范语义：

- 不替代 `openspec validate`。
- 不判断 OpenSpec spec delta、baseline merge、artifact schema 合法性。
- 不把 proposal/spec/tasks/design/contracts 的自由文本解释为业务事实。
- 不把 artifact template 发展成 Aisee 的第二套 DSL。

Aisee CLI 对 OpenSpec artifacts 只做 metadata scan：

- artifact 路径、存在性、hash。
- heading、line、ID 引用、路径引用。
- checkbox 任务状态。
- 与 `source-map.md`、ID registry、review/test evidence 的链接。

当 OpenSpec CLI 提供结构化输出时，context pack 应优先消费 OpenSpec 输出；当没有结构化输出时，只返回 metadata scan 和 gaps，不用 Aisee 自己模拟 OpenSpec parser。

## Command

```bash
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for aisee-verify --json
aisee context pack --change <change> --for ce-doc-review --json
aisee context pack --change <change> --for ce-code-review --json
```

`--change` 是必需入口。context pack 不应从全项目自由搜索后推导范围。

## Top-level Envelope

所有 target 共用以下顶层结构：

```json
{
  "schema_version": "1.0",
  "target": "ce-work",
  "change": {
    "id": "add-auth-login",
    "path": "openspec/changes/add-auth-login",
    "schema": "aisee-app-spec-driven",
    "status": "authored"
  },
  "facts": {
    "parsed": {},
    "derived": {}
  },
  "generated": null,
  "gaps": [],
  "guardrails": [],
  "evidence": {},
  "meta": {}
}
```

Field rules:

- `schema_version`：context pack 契约版本，不等同于 OpenSpec schema 版本。
- `target`：只能是明确目标，如 `ce-work`、`aisee-verify`、`ce-doc-review`、`ce-code-review`。
- `change`：当前 change 是唯一入口。
- `facts.parsed`：只放从 Aisee 补充文件、OpenSpec metadata scan 或 OpenSpec CLI 输出得到的事实。
- `facts.derived`：只放由 `source-map.md`、ID registry、文件关系和轻量校验规则推导出的事实。
- `generated`：默认 `null`。只有显式 `--with-summary` 才允许出现 AI 生成摘要。
- `gaps`：缺口和断链，不是自动补齐结果。
- `guardrails`：执行限制和禁止越界项。
- `evidence`：validate、review、test、verification 的记录入口。
- `meta`：命令、时间、工具版本、解析置信度和错误。

## Parsed Facts

`facts.parsed` 至少包含：

```json
{
  "project_rules": {
    "primary": "AGENTS.md",
    "legacy_fallback": "CLAUDE.md"
  },
  "schema": {
    "name": "aisee-app-spec-driven",
    "version": 2,
    "artifacts": [
      {
        "id": "tasks",
        "path": "openspec/changes/add-auth-login/tasks.md",
        "required": true,
        "status": "present"
      }
    ],
    "apply_requires": ["tasks"],
    "archive_tracks": ["tasks.md", "source-map.md", "specs/**/*.md"]
  },
  "artifacts": {
    "proposal": {},
    "source_map": {},
    "specs": [],
    "contracts": {},
    "tasks": {}
  },
  "sources": [],
  "id_registry": {
    "available": true,
    "checked": true
  }
}
```

Rules:

- `project_rules.primary` 优先为 `AGENTS.md`。
- `CLAUDE.md` 只能作为 legacy fallback。
- `schema.artifacts` 来自当前 change schema 或 OpenSpec CLI 输出，不得硬编码 app/device artifact。
- `artifacts` 只承诺 metadata scan 和原文入口；不要把 contract 内容解析成业务语义。
- `sources` 只包含 `.aisee/sources.json` 和 `source-map.md` 明确引用的上游来源。
- `id_registry` 只报告当前状态，不分配新 ID。

## Derived Facts

`facts.derived` 至少包含：

```json
{
  "read_order": [],
  "scope": {
    "in": [],
    "out": [],
    "follow_up_candidates": []
  },
  "traceability": {
    "upstream_ids": [],
    "produced_ids": [],
    "id_links": []
  },
  "artifact_applicability": [],
  "code_paths": [],
  "test_paths": [],
  "task_state": {
    "total": 0,
    "done": 0,
    "open": 0,
    "blocked": 0
  },
  "verification_requirements": [],
  "open_questions": []
}
```

Rules:

- `read_order` 只能来自当前 change、schema artifact DAG、`source-map.md` 和 project rules。
- `scope.in/out` 来自 proposal、source-map 和 tasks。
- `follow_up_candidates` 可记录实现中发现但未纳入当前 change 的问题。
- `code_paths` 和 `test_paths` 必须来自 `source-map.md`、tasks、contracts 或明确的 implementation evidence；不得自由全项目搜索后加入。
- 缺路径时写入 `gaps`，不要猜测。

## Gap Object

所有 target 使用统一 gap 结构：

```json
{
  "code": "SOURCE_MAP_GAP",
  "severity": "blocker",
  "message": "tasks references auth:API-001 but source-map has no code path",
  "owner_artifact": "source-map.md",
  "related_ids": ["auth:API-001"],
  "suggested_fix": "Update source-map.md with code and test paths before ce-work"
}
```

Severity:

- `blocker`：不能进入下一阶段。
- `risk`：可以继续，但必须记录接受理由或验证要求。
- `info`：提示，不阻断。

Common codes:

- `MISSING_ARTIFACT`
- `SOURCE_MAP_GAP`
- `ID_REGISTRY_GAP`
- `TRACE_GAP`
- `TASK_GAP`
- `CONTRACT_GAP`
- `SPEC_DRIFT`
- `VALIDATE_FAILED`
- `REVIEW_BLOCKER`
- `TEST_EVIDENCE_MISSING`

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
        "forbidden_scope": [],
        "requires_ce_plan": false,
        "ce_plan_reason": null
      }
    }
  },
  "guardrails": [
    "follow tasks.md",
    "do not create a parallel durable plan",
    "report out-of-scope findings as follow-up candidates"
  ]
}
```

Rules:

- `allowed_paths` 来自 `source-map.md`、tasks 或 contracts。
- 如果 `tasks.md` 太粗、路径缺失或 contract 冲突，`requires_ce_plan` 可以为 `true`，但 `ce-plan` 结论必须回写 `tasks.md` / `source-map.md`。
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

## Generated Summary

默认禁止生成摘要。显式启用时：

```json
{
  "generated": {
    "summary": {
      "mode": "generated",
      "target": "ce-work",
      "text": "...",
      "source_fields": [
        "facts.parsed.artifacts",
        "facts.derived.traceability"
      ]
    }
  }
}
```

Generated content is never authoritative. If generated summary conflicts with `facts.parsed` or `facts.derived`, the facts win.
