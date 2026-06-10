---
name: aisee:change-author
description: 将 aisee:change-plan 的结果转成单个 OpenSpec change artifacts 初稿。用于已确认 change 的 author preflight，并按当前 schema 编排 proposal、source-map、specs、tasks、quick-fix、research、docsite、infra、security-audit、app 或 device 契约 artifacts。不拆 change 边界、不重新选择 schema、不写代码；仅当当前 schema 明确包含 design.md 时才按 schema 模板补齐 design artifact。
---

# aisee:change-author

`aisee:change-author` 是 OpenSpec change 产物编排器。它只处理单个已确认 change，把当前 schema 声明的 artifacts 补齐为可验证初稿。

## 职责边界

负责：

- 读取 change-plan、当前 change 目录、所选 schema、schema templates 和直接相关上游事实。
- 读取当前 schema、change 目录和已存在 artifacts 做 author preflight；不要求用户手工执行常规命令。
- 按 schema `artifacts[].requires` 生成或补齐 artifacts。
- 当前 schema 生成 `source-map.md` 时，用它串联上游 anchor refs、产出 local ID、artifact 适用性、路径和验证证据。
- 当前 schema 不生成 `source-map.md` 时，不伪造 source-map；用该 schema 的主 artifact 承载缺口、方案、调研、文档或运维信息。
- 需要新增标识时，只写当前 change 内的 local ID；跨文档追踪统一回写到 anchor ref / alias anchor。
- 仅当 schema 明确包含 `design.md` 时，按该 schema 的官方模板补齐 design artifact。

不负责：

- 拆 change 边界、重新选择 schema、升级轻量 schema 或一次处理多个 changes。
- 为 schema 未声明的 artifact 创建文件。
- 写代码、生成实现方案、让 `ce-plan` 生成长期任务清单。
- 为不生成 `source-map.md` 的 schema 创建 source-map。

## 输入门禁

开始 author 前必须确认：

- 当前只处理一个 OpenSpec change。
- change 已由 `aisee:change-plan` 或用户明确确认边界、schema 和依赖。
- 能读取 `openspec/changes/<change>/`，或用户明确要求只输出补丁 / 草稿。
- 能读取当前 schema 的 `schema.yaml` 和所有 `templates/`。
- 当前 change metadata 已声明 schema，且项目内已安装该 schema；如只有 plugin source 可见但项目未安装，先转交 `aisee-schema-pack`。
- 已收集与所选 schema 直接相关的上游输入：Change Plan、Issue / 用户输入；只有 app/device schema 需要读取对应 SRS、UI Content、Architecture 或设备上下文。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。
- 既有系统或二次开发场景下，已读取相关 existing specs、代码事实、路由/API/模型/测试。

CHECKPOINT: 写入或修改任何 artifact 前，必须输出当前 change、schema、artifact order、待写文件、anchor/local ID 处理动作、已有 artifact 合并策略和 blocker/gap 摘要，等待用户确认。未确认时只能输出 author 草稿、patch 预览或缺口报告，不直接写入 change 目录。

如果缺少阻塞输入，输出 `[CHANGE-AUTHOR-BLOCKED]` 并列出缺口。非阻塞缺口必须写入当前 schema 的追踪 artifact，不要静默补齐。无 source-map schema 的缺口落点见 `references/authoring-rules.md`。

## 读取顺序

1. 读取当前 schema 的 `schema.yaml`，确认 artifact DAG、缺失项和 schema instruction。
2. 按需读取每个 artifact 的 `instruction` 和 `template`。
3. 读取当前 change 已有 artifacts，增量补齐，不覆盖用户内容。
4. 读取与当前 schema 直接相关的上游事实。
   - 有 SRS / UI Content / Architecture 时读取对应 planning docs 的 anchor refs。
   - 没有前置 planning docs 时，只读取 Change Plan、Issue、PR 或用户输入的 intake 摘要；不要伪造 `FR-001`。
5. 如 schema 生成 `source-map.md`，先写或补 source-map 的来源、anchor 路由、artifact 适用性和缺口。
6. 按 artifact DAG 生成 proposal、specs、contracts、tasks 或轻量 schema artifacts。
7. 写入后运行或要求运行 `aisee get <anchor-ref> --json`（按需），并再次检查当前 change 与 schema 是否一致。

详细 artifact 编写边界、app schema v2 顺序、N/A 规则、ID preflight 命令和无 source-map schema 落点见：

```text
references/authoring-rules.md
```

## Author 子阶段

```text
schema preflight -> blocker / schema / anchor preflight
proposal.md -> change scope from confirmed change-plan
source-map.md -> only when schema generates it; upstream anchors + produced local IDs + artifact applicability
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
final check -> schema / artifact consistency recheck
```

## 核心规则

- 以当前 schema 的 `artifacts[].requires` 为唯一生成顺序来源。
- 生成每个 artifact 前，读取它的 schema `instruction` 和 `template`。
- 不要因为某个模板常见就创建 schema 未声明的 artifact。
- 对生成 `source-map.md` 的 schema，先在 source-map 写 artifact 适用性；Required=no 且有原因时不展开完整模板。
- 对不生成 `source-map.md` 的 schema，按 schema 模板写对应 artifact，不套 app artifact 假设。
- 正式 authoring 只使用 local ID 与 anchor refs；不要再要求 `aisee id reserve/activate/check`。
- 对 intake 路径，`upstream_refs=[]` 是合法状态；只要 `intake_sources` 和当前 change 产出 local IDs 完整，就不要为了消除空值补假 anchor。
- CLI 或索引不可用时，只能写 `TYPE-NEW-001` 临时占位符，并标注 `[ID-FINALIZATION-REQUIRED]`。
- app schema 的 `tasks.md` 只记录实现顺序、任务状态和验证证据，不承载需求、契约、ID 注册、来源追踪或归档判断。
- 轻量 schema 的任务追踪到该 schema 的 problem / solution / findings / doc-change / impact / rollback 等前置 artifact。

发现 schema DAG 循环、模板缺失、requires 指向不存在 artifact 时，停止并输出 `[SCHEMA-INVALID]`。

## 写入与输出

如果用户要求直接写文件：

- 只写当前 change 目录内 schema 声明的 artifacts。
- 已存在 artifact 时先读取并增量补齐，避免覆盖用户内容。
- 不要删除用户已有内容，除非它与 schema 明确冲突且用户确认。

输出摘要必须包含：

- 生成 / 更新了哪些 artifacts。
- 哪些 artifacts 是 N/A 及原因。
- 当前 schema 是否生成 `source-map.md`；若不生成，说明没有创建 source-map。
- 是否存在临时 local ID 或 `[ID-FINALIZATION-REQUIRED]`。
- 需要用户确认的 blocker。
- 建议下一步：`openspec validate`，再进入 `aisee:implementation-bridge`。
