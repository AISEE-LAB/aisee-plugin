---
name: aisee:change-plan
description: 将已确认需求、轻量修复、技术调研或项目事实映射为可独立交付的 OpenSpec changes，并为每个 change 选择合适 schema。用于规划 change 边界、依赖顺序、并行关系、source-map seed 和 /opsx:new 命令；不重新做业务模块划分，不重新生成需求，不默认套用 app schema。
---

# aisee:change-plan — OpenSpec Change 边界规划

将已确认需求、轻量修复、技术调研或项目事实映射为边界清晰、可独立交付的 OpenSpec changes。每个输出 change 都应足够小，可以用 `/opsx:new` 创建，并在实现前按所选 schema 的 artifact 顺序补齐内容。

## 职责边界

本 skill 负责：

- 选择每个 change 的 schema。
- 在输出 `/opsx:new` 前做 schema availability preflight：优先读取 `aisee schemas list/check --json` 或项目内 `openspec/schemas/<schema>/schema.yaml` 状态。
- 规划 change 边界、依赖顺序和并行关系。
- 使用 Mermaid 语法块输出依赖顺序和并行关系，作为长期可读性 contract。
- 输出 source-map seed，仅当所选 schema 生成 `source-map.md`。
- 输出可复制的 `/opsx:new "<change>" --schema <schema>` 命令，并把它视为后续 author / implementation 的 schema metadata 合同。
- 保存 change plan 到 `aisee/docs/change-plan/`。

上游如果存在 `design-spec`、`design-assets`、`spec-migrate`、`reflect` 或 `hw:*` 输入，只能按需作为边界线索使用；它们不是默认新功能 happy path 的必经节点。

本 skill 不负责：

- 重新做业务模块划分或重新生成需求。
- 把 SRS 模块名、页面类型、技术层、schema artifact 或实施任务直接当作 change。
- 为上游对象分配额外编号状态。
- 生成或补齐任何 change artifact 正文。
- 默认套用 `aisee-app-spec-driven`。

## 输入

用户提供以下任意一种输入：

- 原始需求描述。
- ticket / issue 引用。
- 既有需求文档路径，包括 `aisee:srs` 输出的 SRS。
- 可选配套输入：`aisee:ui-content`、`aisee:design-spec`、`aisee:design-assets`、`aisee:architecture`。

可选参数：

- `--strategy vertical|risk|parallel`，默认 `vertical`。
- `--granularity fine|medium|coarse`，默认 `medium`。
- `--schema auto|<name>`，默认 `auto`。
- `--max-changes <N>`，默认 `8`。
- `--single-if-small`。

## Reference Loading

只按需读取 references，不要一次性展开全部文件：

- 先读 `references/input-boundary-rules.md`。
- schema 不明确时读 `references/schema-selection-rules.md`。
- 划分多个 changes 或依赖复杂时读 `references/change-boundary-algorithm.md`。
- 只有所选 schema 生成 `source-map.md` 时读 `references/source-map-rules.md`。
- 最终写文件前读 `references/output-template.md`。

## 阶段 1 — 读取项目上下文

静默收集输入和项目事实：

```bash
cat <input-file-path> 2>/dev/null || echo "File not found"
cat openspec/config.yaml 2>/dev/null || echo "No config found"
openspec list --json 2>/dev/null || ls openspec/changes/ 2>/dev/null || echo "No existing changes found"
ls openspec/changes/archive/ 2>/dev/null | head -20
cat AGENTS.md 2>/dev/null | head -120
```

`AGENTS.md` 是主入口；`CLAUDE.md` 只作为旧项目兼容 fallback，不主动作为新项目上下文读取。

## 阶段 2 — 识别输入模式

识别输入来自 SRS、UI Content、Design、Architecture、ticket、issue、轻量修复还是调研材料。

使用输入中的稳定对象作为分析单元，但不要复制输入结构：

- SRS 使用 `FR / NFR / RULE / FLOW / STATE`。
- UI Content 使用 `PAGE / FLOW / STATE`。
- Design Spec / Design Assets 只提供设计策略、组件策略、tokens、screen patterns、参考图或 dev-visual-brief。
- Architecture 使用 `ARCH / DEC / CONSTRAINT / RISK`、技术事实、共享前置和阻塞标签。

SRS 模块名、页面类型、设计材料、架构层、技术层和 schema artifact 名都只是边界提示，不是 change 名称或最终边界。编号规则按 `references/source-map-rules.md` 执行：只引用已有 `doc-ref#编号`；`SPEC / API / DATA / TASK / TEST` 属于 change-author 阶段。

## 阶段 3 — 必要时澄清

最多问两个问题，只在以下情况提问：

- 需求横跨多个无关领域，边界不清。
- 范围内组件或能力确实不明确。
- 关键架构、设计或需求决策缺失，并影响是否可独立交付。

少于约 100 字且只描述一个用户可见功能的小需求，或 SRS 输入模式下 FR 范围已明确时，直接跳过澄清。

如果用户没有回答或表示“你决定”，用 `[ASSUMPTION]` 记录假设并继续。

## 阶段 4 — 规划 Changes

执行：

1. 用 `input-boundary-rules.md` 审查候选，拒绝输入章节、技术层、页面类型、schema artifact 和实施阶段伪 change。
2. 用 `schema-selection-rules.md` 选择 schema；默认 `auto`，不要默认套用 app schema。
3. 对每个候选 schema 做 availability preflight：
   - 已安装：继续输出 `/opsx:new "<change>" --schema <schema>`。
   - 未安装但 plugin source 可见：停止在 planning 输出，转交 `aisee-schema-pack`，建议 `node <skill-dir>/scripts/setup-schemas.js --schema <schema>`。
   - source 也不可见：输出 schema availability blocker，不进入 author/execute 路径。
4. 用 `change-boundary-algorithm.md` 划分可独立交付边界、依赖和并行关系。
5. 用 `source-map-rules.md` 生成 source-map seed；不生成 `source-map.md` 的 schema 写 N/A。
6. 用 `output-template.md` 输出完整 change plan。

## 保护规则

- 单个需求不得输出超过 8 个 changes；超过时说明它是 epic，需要单独规划。
- 不得创建只做 infrastructure 或 setup、没有用户可见结果的 change。
- 不得机械拆成 frontend / backend / database changes，除非它们确实可以独立交付。
- 小 bugfix、文案、样式、配置小改不得强行升级为 `aisee-app-spec-driven`。
- 轻量 schema 不要求 SRS / UI Content / Architecture，除非边界判断确实依赖这些文档。
- 不得为不生成 `source-map.md` 的 schema 输出伪 source-map seed。
- 无前置 planning docs 时，必须使用 intake 摘要路径，不得伪造 `docs/...#FR-001`。
- schema 写入只通过 `aisee-schema-pack` skill / `setup-schemas.js`。
- 调研 schema 的结论不得写成生产实现任务；调研后需要实现时，另起实现 change。

## 工作流衔接

```text
aisee:srs / ui-content / design-spec / architecture
  -> aisee:change-plan
  -> /opsx:new <change> --schema <selected-schema>
  -> aisee:change-author
  -> openspec validate
  -> aisee:implementation-bridge
  -> compound plan / work / review / test
  -> aisee:verify
  -> aisee:archive-guard
  -> openspec archive
```

多个 changes 同时进行时，后续命令必须显式指定 change 名。
