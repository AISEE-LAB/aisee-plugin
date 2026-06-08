---
name: aisee:change-author
description: 将 aisee:change-plan 的结果转成单个 OpenSpec change artifacts 初稿。用于已确认 change 的 author preflight，并按当前 schema 编排 proposal、source-map、specs、tasks、quick-fix、research、docsite、infra、security-audit、app 或 device 契约 artifacts。必须先运行 aisee change author-check；不拆 change 边界、不重新选择 schema、不写代码；仅当当前 schema 明确包含 design.md 时才按 schema 模板补齐 design artifact。
---

# aisee:change-author

`aisee:change-author` 是 OpenSpec change 产物编排器。它只处理单个已确认 change，把当前 schema 声明的 artifacts 补齐为可验证初稿。

## CLI preflight

调用 `aisee ...` 前先按 `references/cli-preflight.md` 确认 CLI 可用；缺失时停止并提示用户通过 PyPI / pipx 安装 CLI。

## 职责边界

负责：

- 读取 change-plan、当前 change 目录、所选 schema、schema templates 和直接相关上游事实。
- 运行并解释 `aisee change author-check <change> --json`。
- 按 `author-check.artifact_order` 和 schema `artifacts[].requires` 生成或补齐 artifacts。
- 当前 schema 生成 `source-map.md` 时，用它串联上游 ID、产出 ID、artifact 适用性、路径和验证证据。
- 当前 schema 不生成 `source-map.md` 时，不伪造 source-map；用该 schema 的主 artifact 承载缺口、方案、调研、文档或运维信息。
- 需要正式 ID 时，按 `author-check.ids.actions` 先 reserve、写入后 activate。
- 仅当 schema 明确包含 `design.md` 时，按该 schema 的官方模板补齐 design artifact。

不负责：

- 拆 change 边界、重新选择 schema、升级轻量 schema 或一次处理多个 changes。
- 为 schema 未声明的 artifact 创建文件。
- 写代码、生成实现方案、让 `ce-plan` 生成长期任务清单。
- 为不生成 `source-map.md` 的 schema 创建 source-map。

## 必须先运行的检查

开始 author 前必须运行：

```bash
aisee change author-check <change> --json
```

处理规则：

- `status=blocked`：停止 author，列出 `blockers`；不要创建或修改 artifacts。
- `schema.valid=false`：停止 author；不得自造 schema 未声明的 artifact 或模板。
- `missing_artifacts` 非空：只按 `artifact_order` 和 schema templates 补齐缺失项；不重排 schema。
- `ids.actions.reserve` 非空：先运行对应 `aisee id reserve`，再写入正式 ID。
- `ids.actions.activate` 非空：写入 artifact 后运行 `aisee id activate`。
- `ids.registry.missing / inactive` 非空：先修复 registry 或替换引用；不要把断链 ID 写入新的 artifact。
- `next_actions` 是执行提示，不是新的事实源；所有结论必须回写到 OpenSpec artifacts。

如 CLI 不可用，允许继续草稿，但必须使用临时 ID 并显式标注 `[ID-RESERVATION-REQUIRED]`。具体 fallback 见 `references/authoring-rules.md`。

## 输入门禁

开始 author 前必须确认：

- 当前只处理一个 OpenSpec change。
- change 已由 `aisee:change-plan` 或用户明确确认边界、schema 和依赖。
- 能读取 `openspec/changes/<change>/`，或用户明确要求只输出补丁 / 草稿。
- `aisee change author-check <change> --json` 已完成，且没有 blocker。
- 能读取当前 schema 的 `schema.yaml` 和所有 `templates/`。
- 已收集与所选 schema 直接相关的上游输入：Change Plan、Issue / 用户输入；只有 app/device schema 需要读取对应 SRS、UI Content、Architecture 或设备上下文。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。
- 既有系统或二次开发场景下，已读取相关 existing specs、代码事实、路由/API/模型/测试。

CHECKPOINT: 写入或修改任何 artifact 前，必须输出当前 change、schema、artifact order、待写文件、ID reserve/activate 动作、已有 artifact 合并策略和 blocker/gap 摘要，等待用户确认。未确认时只能输出 author 草稿、patch 预览或缺口报告，不直接写入 change 目录。

如果缺少阻塞输入，输出 `[CHANGE-AUTHOR-BLOCKED]` 并列出缺口。非阻塞缺口必须写入当前 schema 的追踪 artifact，不要静默补齐。无 source-map schema 的缺口落点见 `references/authoring-rules.md`。

## 读取顺序

1. 读取 `author-check` JSON，确认 schema、artifact DAG、missing artifacts、ID actions 和 blockers。
2. 读取当前 schema 的 `schema.yaml`，再按需读取每个 artifact 的 `instruction` 和 `template`。
3. 读取当前 change 已有 artifacts，增量补齐，不覆盖用户内容。
4. 读取与当前 schema 直接相关的上游事实。
5. 如 schema 生成 `source-map.md`，先写或补 source-map 的来源、ID 路由、artifact 适用性和缺口。
6. 按 artifact DAG 生成 proposal、specs、contracts、tasks 或轻量 schema artifacts。
7. 写入后运行或要求运行 `aisee change author-check <change> --json`、`aisee id check --json` 和 `aisee gaps --change <change> --json`。

详细 artifact 编写边界、app schema v2 顺序、N/A 规则、ID preflight 命令和无 source-map schema 落点见：

```text
references/authoring-rules.md
```

## Author 子阶段

```text
author-check -> blocker / schema / ID preflight
proposal.md -> change scope from confirmed change-plan
source-map.md -> only when schema generates it; upstream IDs + produced IDs + artifact applicability
specs/**/*.md -> only when schema generates it; observable behavior and acceptance
change-context.md -> app architecture context author, only when Required=yes
design.md -> only when schema generates design.md, author directly from schema template
ui-contract.md / service-contract.md / data-model.md -> app domain author, only when Required=yes
hardware-contract.md / firmware-contract.md / runtime-contract.md / verification-contract.md -> device domain author, when schema generates them
quick-fix artifacts -> problem.md / solution.md / tasks.md
research artifacts -> question.md / findings.md / recommendation.md or loop/* artifacts
security-audit artifacts -> threat-model.md / design.md, only when selected schema generates them
docsite / infra artifacts -> only when selected schema generates them
tasks.md -> single durable implementation and verification checklist
final check -> aisee change author-check + aisee gaps
```

## 核心规则

- 以 `author-check.artifact_order` 和当前 schema 的 `artifacts[].requires` 为唯一生成顺序来源。
- 生成每个 artifact 前，读取它的 schema `instruction` 和 `template`。
- 不要因为某个模板常见就创建 schema 未声明的 artifact。
- 对生成 `source-map.md` 的 schema，先在 source-map 写 artifact 适用性；Required=no 且有原因时不展开完整模板。
- 对不生成 `source-map.md` 的 schema，按 schema 模板写对应 artifact，不套 app artifact 假设。
- 正式 ID 必须来自 `aisee/registry/id-registry.json`；新增 ID 先 reserve，写入后 activate。
- CLI 或 registry 不可用时，只能写 `{{scope}}:<TYPE>-NEW-001` 临时占位符，并标注 `[ID-RESERVATION-REQUIRED]`。
- app schema 的 `tasks.md` 只记录实现顺序、任务状态和验证证据，不承载需求、契约、ID 注册、来源追踪或归档判断。
- 轻量 schema 的任务追踪到该 schema 的 problem / solution / findings / doc-change / impact / rollback 等前置 artifact。

发现 schema DAG 循环、模板缺失、requires 指向不存在 artifact 时，停止并输出 `[SCHEMA-INVALID]`；优先引用 `author-check.schema.issues`。

## 写入与输出

如果用户要求直接写文件：

- 只写当前 change 目录内 schema 声明的 artifacts。
- 已存在 artifact 时先读取并增量补齐，避免覆盖用户内容。
- 不要删除用户已有内容，除非它与 schema 明确冲突且用户确认。

输出摘要必须包含：

- 生成 / 更新了哪些 artifacts。
- 哪些 artifacts 是 N/A 及原因。
- 当前 schema 是否生成 `source-map.md`；若不生成，说明没有创建 source-map。
- 是否存在临时 ID 或 `[ID-RESERVATION-REQUIRED]`。
- 需要用户确认的 blocker。
- 最后一次 `aisee change author-check <change> --json` 和 `aisee gaps --change <change> --json` 的状态。
- 建议下一步：`openspec validate`，再进入 `aisee:implementation-bridge`。
