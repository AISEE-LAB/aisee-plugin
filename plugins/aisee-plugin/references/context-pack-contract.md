# Context Pack Contract

本文是 `aisee context pack` 核心输出结构的维护源。

相关细则：

- Target-specific 规则：[context-pack-targets.md](context-pack-targets.md)
- Gap 对象与门禁语义：[context-pack-gaps.md](context-pack-gaps.md)
- Source Map 解析规则：[source-map-contract.md](source-map-contract.md)
- ID 生命周期规则：[id-policy.md](id-policy.md)

`aisee context pack` 是 OpenSpec context companion。它默认调用时衔接 OpenSpec change、Aisee 补充信息和 CE evidence，不维护第二份内容事实源，也不替代 OpenSpec parser。

## Fact Sources

- OpenSpec artifacts / Markdown：内容事实源。
- `aisee/registry/id-registry.json`：历史兼容数据；当前主链路不把它当作正式事实源。
- `aisee/registry/sources.json`：change 外部 Aisee 产物来源登记事实源。
- `aisee/cache/context-index.json`：可删除、可重建缓存，不是事实源。

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

`source-map.md` 是 Aisee companion 路由表，允许结构化解析。除 `source-map.md` 外，OpenSpec artifacts 只承诺 metadata scan。

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
- `generated`：默认 `null`。只有显式启用生成摘要时才允许出现 AI 生成内容。
- `gaps`：缺口和断链，不是自动补齐结果。结构见 [context-pack-gaps.md](context-pack-gaps.md)。
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
    "artifacts": [],
    "apply_requires": ["tasks"],
    "archive_tracks": ["tasks.md", "source-map.md", "specs/**/*.md"]
  },
  "artifacts": {},
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
- `source_map` 作为 Aisee companion artifact，可包含 `upstream_sources`、`id_trace`、`artifact_applicability`、`implementation_paths`、`verification_evidence`、`out_of_scope` 和 parse issues。
- `sources` 只包含 `aisee/registry/sources.json` 和 `source-map.md` 明确引用的上游来源。
- `id_registry` 只报告历史兼容状态；缺失不是当前 authoring / lookup / traceability blocker。

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
  "implementation_references": {
    "declared_paths": [],
    "referenced_paths": [],
    "unmapped_reference_paths": []
  },
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

- `read_order` 只能来自当前 change、schema artifact DAG、`source-map.md`（如适用）和 project rules。
- `scope.in/out` 来自 proposal、当前 schema artifacts、source-map（如适用）和 apply tracks。
- `follow_up_candidates` 可记录实现中发现但未纳入当前 change 的问题。
- 对生成 `source-map.md` 的 schema，`code_paths` 和 `test_paths` 优先来自 `source-map.md` 的 `Affected Paths Index` 结构化声明。
- 对不生成 `source-map.md` 的 schema，实现参考只能来自当前 schema artifacts / apply tracks 的显式路径引用，并在 `implementation_references.source` 标记为 `schema-artifacts`。
- OpenSpec artifacts 和 source-map 文本中额外出现的路径只能进入 `implementation_references.referenced_paths`。
- `implementation_references.unmapped_reference_paths` 表示被 artifact 文本提到但未被当前 schema 的实现定位规则接纳的路径；`ce-work` 不得把这些路径加入 `allowed_paths`。
- 缺路径时写入 `gaps`，不要猜测。

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
