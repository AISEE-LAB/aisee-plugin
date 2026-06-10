# aisee:change-plan — Source-map Seed 规则

只有所选 schema 生成 `source-map.md` 时，planned change 才必须包含 source-map seed。seed 不是最终 artifact 内容，只是后续 `source-map.md` 和 schema artifacts 的初始上下文路由线索。

不生成 `source-map.md` 的轻量 schema（如 `quick-fix`、`quick-research`、`infra-change`、`aisee-docsite-driven`）不需要 source-map seed；在 change-plan 中写 `Source-map seed: N/A — schema does not generate source-map.md`。

## 通用规则

- source-map seed 只记录上游来源、文档引用和候选 artifact 路由。已有 planning docs 使用 `doc-ref#编号`；没有前置文档时，在“上游来源”记录精简摘要和外部引用，不伪造 `FR-001`。
- FR / NFR / RULE 只有在存在 SRS 时才引用 `doc-ref#编号`；无 SRS 时写 `N/A — no SRS planning doc`，并在“上游来源”记录摘要。
- FLOW / STATE 只有在存在 SRS 或 UI Content 时才引用 `doc-ref#编号`；无前置文档时写 `N/A`，不要为了凑表强造 ref。
- PAGE / FLOW / STATE 必须来自 UI Content；没有 UI 时写 `N/A`，不要硬造页面。
- Architecture 相关来源只引用 `ARCH / DEC / CONSTRAINT / RISK` 的文档引用或编号，不复制整段架构说明。
- `aisee:change-plan` 不分配上游 ID，不临时发明正式 full ID。
- SPEC / API / DATA / TASK / TEST 是 change-author 阶段产出，seed 中写 `TBD in <artifact>` 或 local ID placeholder。
- artifact 适用性要写 yes/no 和原因，不能只写 yes/no。
- 用户输入 / issue / ticket 只保留 1-5 句摘要、外部引用和承接 artifact；不要复制原始长提示词、聊天记录或任务清单正文。
- 不要在 seed 中写最终 API endpoint、数据库字段、引脚表、寄存器表或实现任务。

## App / Software Schema Seed

适用于 `aisee-app-spec-driven`：

| 字段 | 填写规则 |
|------|----------|
| FR / NFR / RULE | 有 SRS 时写 `doc-ref#编号`；无 SRS 时写 `N/A — no SRS planning doc`，并在“上游来源”记录摘要 |
| PAGE / FLOW / STATE | UI Content 中的 `doc-ref#编号`；无 UI 时写 `N/A`，不要伪造页面/流程 |
| DESIGN | Design Spec / Design Assets / dev-visual-brief 引用，或 `N/A` |
| ARCH / DEC / CONSTRAINT / RISK | Architecture 中的 `doc-ref#编号`，或 `N/A` |
| SPEC | `TBD in change-author` |
| API | `TBD in service-contract` |
| DATA | `TBD in data-model` |
| TASK / TEST | `TBD in tasks` |

必须判断以下 artifact 是否适用：

- `change-context.md`
- `ui-contract.md`
- `data-model.md`
- `service-contract.md`

其中 `proposal.md`、`source-map.md`、`specs/**/*.md` 和 `tasks.md` 是 app 最小闭环，不通过 Required=no 跳过。`change-context.md`、`ui-contract.md`、`data-model.md` 和 `service-contract.md` 是按需 artifact / 契约，只有 Required=yes 时才需要在 change-author 阶段展开；Required=no 必须写具体原因。

当没有前置 planning docs 时，seed 在“上游来源”记录：

- 来源类型：`user-input` / `issue` / `ticket` / `pr` / `change-plan`
- 外部 Ref：外部链接、issue 编号或 `N/A`
- 摘要：1-5 句经过整理的输入摘要
- 承接 artifact：当前 change 预计承接它的 artifact，如 `specs/auth.md`、`tasks.md`

对于既有系统或二次开发，seed 应提示本 change 涉及对象是 `Existing / Changed / New / Deprecated / Unknown`。Existing 只引用来源，不要求后续 artifact 重写完整规格。

## Device Schema Seed

适用于 `aisee-device-spec-driven`：

| 字段 | 填写规则 |
|------|----------|
| FR | SRS / proposal 中的 FR ID |
| HW | 预期硬件能力 ID，或 `TBD in hardware-contract` |
| FW | 预期固件能力 ID，或 `TBD in firmware-contract` |
| RT | 预期运行时能力 ID，或 `TBD in runtime-contract` |
| VER | 预期验证能力 ID，或 `TBD in verification-contract` |

必须判断以下 artifact 是否适用：

- `hardware-contract.md`
- `firmware-contract.md`
- `runtime-contract.md`
- `verification-contract.md`

## Hybrid Schema Seed

混合系统需要同时判断软件侧和设备侧 seed。不要为了简化而把云端、App、设备、固件全部塞进同一个 change；除非它们构成一个小而完整、可独立验证的纵向切片。
