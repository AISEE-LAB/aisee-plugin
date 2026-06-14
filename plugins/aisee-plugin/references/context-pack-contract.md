# Context Pack Contract

本文是 `aisee context pack` 核心输出结构的维护源。

相关细则：

- Target-specific 规则：[context-pack-targets.md](context-pack-targets.md)
- Source Map 解析规则：[source-map-contract.md](source-map-contract.md)
- 编号规则：[id-policy.md](id-policy.md)

`aisee context pack` 是 OpenSpec context companion。它默认调用时衔接当前 change 的 metadata scan 与可选的 memory / knowledge 注入，不维护第二份内容事实源，也不替代 OpenSpec parser。

## Fact Sources

- OpenSpec change artifacts / baseline specs：规范事实源。
- `source-map.md`：当前 change 的来源、适用性、候选路径和 evidence 路由。
- `tasks.md`：当前 change 的长期任务清单。
- review / test / verification evidence：实现后验证记录入口。
- planning docs frontmatter 和明确 source refs：版本或迭代输入索引，不是 baseline。

默认输出只包含：

- `parsed`：从 Aisee 自有补充文件、OpenSpec metadata scan 和可用 OpenSpec CLI 输出解析。
- `derived`：根据 source-map、文件关系、编号和轻量校验规则推导。
- 可选独立注入：`project_memory`、`knowledge`。

AI 生成摘要必须显式启用，并在 JSON 中标记为 `generated`。

## OpenSpec Boundary

Aisee CLI 不解析 OpenSpec 已负责的规范语义：

- 不替代 `openspec validate`。
- 不判断 OpenSpec spec delta、baseline merge、artifact schema 合法性。
- 不把 proposal/spec/tasks/design/contracts 的自由文本解释为业务事实。
- 不把 artifact template 发展成 Aisee 的第二套 DSL。

Aisee CLI 对 OpenSpec artifacts 只做 metadata scan：

- artifact 路径、存在性、hash。
- heading、line、编号、source ref 和路径引用。
- checkbox 任务状态。
- 与 `source-map.md`、review/test evidence 的链接。

`source-map.md` 是 Aisee companion 路由表，允许结构化解析。除 `source-map.md` 外，OpenSpec artifacts 只承诺 metadata scan。

当 OpenSpec CLI 提供结构化输出时，context pack 应优先消费 OpenSpec 输出；当没有结构化输出时，只返回 metadata scan 和 gaps，不用 Aisee 自己模拟 OpenSpec parser。

## Command

```bash
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --project-memory --json
aisee context pack --change <change> --for aisee-verify --json
aisee context pack --change <change> --for ce-doc-review --json
aisee context pack --change <change> --for ce-code-review --json
```

`--change` 是必需入口。context pack 不应从全项目自由搜索后推导范围。`--for <target>` 仅用于限定可选注入层的检索边界，不再要求生成 target-specific 的 execution / verify / review 投影。

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
  "project_memory": {},
  "meta": {}
}
```

Field rules:

- `schema_version`：context pack 契约版本，不等同于 OpenSpec schema 版本。
- `target`：只能是明确目标，如 `ce-work`、`aisee-verify`、`ce-doc-review`、`ce-code-review`。
- `change`：当前 change 是唯一入口。
- `facts.parsed`：只放从 Aisee 补充文件、OpenSpec metadata scan 或 OpenSpec CLI 输出得到的事实。
- `facts.derived`：只放由 `source-map.md`、文件关系、编号和轻量校验规则推导出的事实。
- `generated`：默认 `null`。只有显式启用生成摘要时才允许出现 AI 生成内容。
- `gaps`：缺口和断链，不是自动补齐结果，也不是路由裁决结果。结构见下文 `Gap Object`。
- `guardrails`：执行限制和禁止越界项。
- `evidence`：validate、review、test、verification 的记录入口。
- `project_memory`：只在显式 `--project-memory` 时出现；包含受控 memory matches，不得写入 `facts.parsed` 或 `facts.derived`。
- `meta`：命令、时间、工具版本、解析置信度和错误。

## Gap Object

所有 target 使用统一 gap 结构：

```json
{
  "code": "SOURCE_MAP_GAP",
  "severity": "blocker",
  "message": "tasks reference API-001 but source-map has no code path",
  "owner_artifact": "source-map.md",
  "related_refs": ["API-001"],
  "suggested_fix": "Update source-map.md with code and test paths before ce-work"
}
```

Rules:

- `code`：稳定机器可读 code。
- `severity`：只能是 `blocker`、`risk` 或 `info`。
- `message`：人类可读说明。
- `owner_artifact`：应修复或确认的 artifact / 文件。
- `related_refs`：可为空；需要定位来源或编号时使用 source ref 或短编号。
- `suggested_fix`：给出最小修复方向，不自动生成内容。

## Gap Severity And Common Codes

- `blocker`：不能进入下一阶段。
- `risk`：可以继续，但必须记录接受理由或验证要求。
- `info`：提示，不阻断。

Common codes:

- `MISSING_ARTIFACT`
- `SOURCE_MAP_GAP`
- `SOURCE_REF_GAP`
- `SOURCE_ROUTING_GAP`
- `TASK_GAP`
- `CONTRACT_GAP`
- `SPEC_DRIFT`
- `VALIDATE_FAILED`
- `REVIEW_BLOCKER`
- `TEST_EVIDENCE_MISSING`

`context pack` 自己不再消费这些 severity 去生成下一步路由。后续如何处理 blocker / risk / info，由 `implementation-bridge`、`aisee:verify`、`aisee:archive-guard` 或人工判断决定。

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
    "capabilities": ["source_map_traceability", "apply_execution", "contract_helper"],
    "artifacts": [],
    "apply_requires": ["tasks"],
    "apply_tracks": "tasks.md",
    "archive_tracks": ["tasks.md", "source-map.md"],
    "issues": []
  },
  "artifacts": {},
  "source_map": {},
  "sources": [],
  "source_reference_index": {}
}
```

Rules:

- `project_rules.primary` 优先为 `AGENTS.md`。
- `CLAUDE.md` 只能作为 legacy fallback。
- `schema.artifacts` 来自当前 change schema 或 OpenSpec CLI 输出，不得硬编码 app/device artifact。
- `schema.capabilities`、artifact `requiredness` 和 `na_requires_reason` 来自当前 schema 声明；skill 不得自行补默认 app 语义。
- `artifacts` 只承诺 metadata scan 和原文入口；不要把 contract 内容解析成业务语义。
- `source_map` 作为 Aisee companion artifact，可包含 `upstream_sources`、`source_context`、`artifact_applicability`、`implementation_paths`、`verification_evidence`、`out_of_scope` 和 parse issues。
- `sources` 只包含 `source-map.md` 明确引用的文档路径摘要，用于提示 read order，不是 registry。
- `source_reference_index` 是调用时生成的内部扫描视图，用于报告缺失 source ref 和临时编号风险；不是持久事实源。

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
    "upstream_refs": [],
    "mode": "empty",
    "produced_local_ids": [],
    "resolved_source_refs": [],
    "unresolved_source_refs": [],
    "numbering_links": []
  },
  "artifact_applicability": [],
  "code_paths": [],
  "test_paths": [],
  "implementation_references": {
    "declared_paths": [],
    "referenced_paths": [],
    "unmapped_reference_paths": []
  },
  "artifact_order": [],
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
- `artifact_order` 表示当前 schema artifacts 的稳定 author / 展示顺序；优先遵循 `artifacts[].requires`，同层级默认保持 schema 声明顺序，`apply_track` artifact 置后。
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
