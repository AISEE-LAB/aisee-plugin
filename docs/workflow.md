# Aisee Workflow

本文描述 Aisee 与 OpenSpec 配合时的推荐软件开发流程。它参考 OpenSpec 的核心节奏：先提出 change，再补齐 artifacts，通过 validate，完成实现和验证，最后 archive 进入 baseline。

## 核心原则

- OpenSpec 是规范状态机和 baseline 事实源。
- Aisee 负责需求澄清、上下文整理、schema-aware 交接和门禁。
- Aisee CLI 输出 JSON context view，不创建第二份规范事实源。
- 实现、review、test 可以由 Compound Engineering 或其他 coding agent 承接。
- `openspec archive <change>` 是已验证 change 合入 baseline 的最终动作。

## 0. 项目初始化

适用于新项目或准备接入 OpenSpec 的已有项目。

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
aisee schemas install --all --json
aisee doctor --json
```

推荐同时使用 `aisee:init` 审计或生成：

- `AGENTS.md`
- `openspec/project.md`
- `aisee/registry/`
- `aisee/memory/`
- 必要 hooks

如果是已有项目，先不要直接写新 change。优先使用 `aisee:spec-migrate` 反向整理 baseline specs，再进入新需求开发。

## 1. 前置澄清

目标是把聊天里的想法转成可审查输入，而不是直接进入实现。

推荐顺序：

```text
aisee:srs
  -> aisee:ui-content（有 UI 时）
  -> aisee:design-spec / aisee:design-assets（有视觉设计需要时）
  -> aisee:architecture
```

产出定位：

| 产物 | 作用 | 注意 |
| --- | --- | --- |
| SRS | 澄清业务目标、范围、功能需求、非功能需求和验收标准 | 不写实现任务 |
| UI Content | 描述页面内容、状态、操作、权限可见性和前端数据需求 | 不写组件库、配色、排版 |
| Design Spec / Assets | 描述或生成视觉规范、参考图、素材和风格输入 | 不重复页面内容 |
| Architecture | 记录技术事实、架构边界、平台约束、共享约定和风险 | 不替代 change artifact |

这些前置文档是 change planning 的输入，不是 OpenSpec baseline。

## 2. Change 规划

用 `aisee:change-plan` 把已确认输入拆成可独立交付的 OpenSpec changes。

```text
aisee:change-plan
  -> change list
  -> dependency order
  -> schema recommendation
  -> source-map seed
```

拆分原则：

- 一个 change 对应一个可验证的用户价值或工程结果。
- 不把输入材料章节、技术层、页面类型、schema artifact 当成 change。
- 大 change 可以有依赖顺序，但不要让单个 change 承担整套产品。
- 低风险小修复可以使用 `quick-fix`，不强制走 app schema。
- 前后端共享接口、事件、数据模型或 SDK 时，优先规划一个前置 contract change。

## 3. Change 创建与 Authoring

创建 change 后，用 `aisee:change-author` 按 schema artifact DAG 补齐文档。

典型命令：

```bash
/opsx:new "<change>" --schema aisee-app-spec-driven
aisee change author-check <change> --json
openspec validate <change>
```

app schema 的常见 artifacts：

```text
proposal.md
source-map.md
specs/**/*.md
tasks.md
change-context.md        # 按需
ui-contract.md           # 按需
service-contract.md      # 按需
data-model.md            # 按需
```

`source-map.md` 决定按需 artifacts 是否 Required：

- Required=yes：必须展开对应 artifact。
- Required=no：必须写清楚 N/A 原因。
- 不要为了“完整”强行生成与当前 change 无关的 contract。

## 4. 实现交接

进入实现前，先确认 change 已 authored 且无 blocker。

```bash
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee context pack --change <change> --for ce-work --json
```

如果项目配置了 team knowledge，可以在公开接口、schema、路径读取、安全、跨仓库契约等高风险实现前额外读取少量 guardrails：

```bash
aisee knowledge query --from-change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
```

Knowledge matches 只作为提醒，不改变当前 change 的规范事实源，也不应复制进长期 artifacts。

然后使用 `aisee:implementation-bridge` 输出 Implementation Brief。Brief 只做执行索引：

- 当前 change 和 schema。
- 必读 artifacts。
- 允许修改的代码路径和测试路径。
- apply tracks 回写位置。
- 验证命令和 evidence 位置。
- 是否建议 Tier 2 code review。

如果 change 很大，不回到 change-plan 重新拆分。可以在当前 change 内生成 `brief-index.md` 和多个 `brief-part-NN.md` 分批执行。

## 5. 实现、Review 与 Test

实现阶段由 coding agent 或人工开发承接。无论使用什么工具，都应遵循：

- 只实现当前 change 范围。
- 如果发现 spec/contract/code 不一致，先回写当前 OpenSpec change，再继续实现。
- 完成后更新 `tasks.md` 或当前 schema 的 apply tracks。
- 测试、人工验证、预览、监控或 review 结果必须作为 evidence 记录。

当 change 触及公开 CLI、HTTP endpoint、API/service contract、schema、parser、路径读取、安全或隐私表面时，建议执行 Tier 2 code review。

只读 Aisee reviewer role 的触发时机：

| Reviewer | 触发时机 | 用途 |
| --- | --- | --- |
| `aisee-change-architect` | `aisee:change-plan` 后、`aisee:change-author` 前按需触发；仅用于边界复杂、跨模块、跨 schema、依赖不清或粒度不确定的 change | 审查 change 边界、依赖、粒度和可独立交付性 |
| `aisee-spec-reviewer` | `aisee:change-author` 后、`aisee:implementation-bridge` / `ce-work` 前建议触发 | 审查 artifacts、contracts、source-map、tasks 是否完整、一致、可验证 |
| `aisee-implementation-reviewer` | `ce-work` 完成后、`aisee:verify` / `aisee:archive-guard` 前建议触发 | 比对实现、tasks、spec/source-map 和 evidence 是否一致 |

这些 reviewer 只输出结构化审查结论，不改代码、不跑测试、不提交 PR，也不替代 `ce-doc-review`、`ce-code-review`、`ce-test-*` 或 `ce-work`。接口、UI、硬件、固件、安全和验证差异应作为 schema-aware check lenses，而不是新增独立全能 agent。

## 6. Verify

实现后运行：

```bash
openspec validate <change>
aisee change verify-check <change> --json
aisee context pack --change <change> --for aisee-verify --json
```

再使用 `aisee:verify` 输出 schema-aware 报告，重点检查：

- schema artifacts 是否存在。
- Required=yes contracts 是否闭合。
- source-map、ID、代码路径、测试路径和 evidence 是否一致。
- `tasks.md` 或 apply tracks 是否真实完成。
- OpenSpec validate 是否通过。
- review/test/manual evidence 是否足够。
- 是否仍需要 Tier 2 review。

verify 不是 archive 审批，它只输出问题和风险。

## 7. Archive Guard

archive 前运行：

```bash
aisee change archive-check <change> --json
```

然后使用 `aisee:archive-guard` 判断：

- `openspec validate <change>` 是否通过。
- `aisee:verify` 是否无 blocker。
- apply tracks 是否关闭。
- review/test/manual evidence 是否满足当前 schema。
- accepted risk 是否有 owner、理由、影响范围和后续处理方式。

只有 archive guard 给出“可以 archive”时，才执行：

```bash
openspec archive <change>
```

## 8. 跨仓库接口协作

前后端分离或多仓库协作时，推荐由后端仓库、BFF 仓库或独立契约仓库维护契约事实。

契约提供方：

```bash
aisee contract manifest --json
aisee contract summary --change <change> --json
aisee contract serve --host 127.0.0.1 --port 8765
```

契约消费方：

```bash
curl http://127.0.0.1:8765/manifest
curl http://127.0.0.1:8765/changes/<change>/summary
curl "http://127.0.0.1:8765/changes/<change>/contracts/service-contract/sections/<section>?max_chars=4000"
```

`aisee contract serve` 是只读上下文服务，不是 mock backend，不是 API gateway，也不是第二份接口事实源。

## 9. Team Knowledge 复用

当一个项目沉淀出可复用经验时，先由用户明确触发 `aisee:reflect` 生成项目内 candidate，再按需运行 `aisee:knowledge-curate` 做批量审查、去敏、泛化和去重。

推荐路径：

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> batch review report / card drafts
  -> 用户确认后再写入 team knowledge repo
```

边界：

- 不在 archive 或 verify 后自动写入 team knowledge。
- 不把 `docs/solutions/`、memory 或 reflect 文档整库复制到其他项目。
- 不让 AI 直接扫描 team knowledge 仓库正文；使用 `aisee knowledge query`。
- 写入 team repo、创建分支、提交、合并或 PR 前必须再次获得用户明确授权。

## 快速路径

| 场景 | 推荐路径 |
| --- | --- |
| 新功能 | SRS -> UI/Architecture -> change-plan -> change-author -> implementation-bridge -> verify -> archive-guard |
| 小修复 | `quick-fix` schema -> author-check -> implementation-bridge -> verify -> archive-guard |
| 技术调研 | `quick-research` schema -> findings/recommendation -> validate -> archive-guard |
| 文档站变更 | `aisee-docsite-driven` schema -> doc-change/tasks -> build/link evidence -> archive-guard |
| 已有项目接入 | `aisee:init` -> `aisee:spec-migrate` -> baseline specs -> 新 change |

## 何时停止

遇到以下情况不要继续实现：

- 需求范围仍不清楚。
- 当前 change 无法映射到可验证 outcome。
- schema artifacts 缺失或互相矛盾。
- Required=yes contract 缺失。
- 实现路径没有被当前 change 或 context pack 指向。
- OpenSpec validate 失败且没有明确修复方向。

这时应回到对应 artifact 修补，而不是让实现阶段临时猜测。
