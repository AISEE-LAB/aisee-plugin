# Aisee Workflow

本文描述 Aisee 与 OpenSpec 配合时的推荐软件开发流程。它参考 OpenSpec 的核心节奏：先提出 change，再补齐 artifacts，通过 validate，完成实现和验证，最后 archive 进入 baseline。

## 核心原则

- OpenSpec 是规范状态机和 baseline 事实源。
- Aisee 负责需求澄清、上下文整理、knowledge/memory 增强和 Compound 交接。
- Aisee CLI 输出 JSON context view，不创建第二份规范事实源。
- 实现、review、test 可以由 Compound Engineering 或其他 coding agent 承接。
- `openspec archive <change>` 是已验证 change 合入 baseline 的最终动作。
- planning docs 只服务当前版本 / 迭代输入，不替代 baseline facts。
- 普通 planning docs 使用统一 YAML frontmatter 合同做身份、状态和来源索引；OpenSpec change 和 baseline 仍是规范事实源。
- 文档内正式写法使用稳定编号；跨文档来源由 `source-map.md` 记录。

## 0. 项目初始化

适用于新项目或准备接入 OpenSpec 的已有项目。

如果刚进入项目且不确定从哪个 Aisee workflow 开始，先使用 `aisee:orient` 判断项目状态、用户意图和下一步路由。

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
aisee doctor --json
```

这里的边界是：`aisee openspec ensure` 负责把 OpenSpec 的 instructions / skills 写入当前项目目录，并顺带对齐全局 `openspec config profile`；不要把 `config profile` 本身理解成项目目录安装步骤。

推荐同时使用 `aisee:init` 审计或生成：

- `AGENTS.md`
- `openspec/project.md`
- `aisee/memory/`
- 必要 hooks

如果是已有项目，先不要直接写新 change。优先使用 `aisee:spec-migrate` 反向整理 baseline specs，再进入新需求开发。

## 默认主路径与按需扩展

`aisee:orient` 和 `aisee:init` 属于项目入口定位 / 接入 / 治理阶段能力，不是默认新功能迭代 happy path 的必经节点。默认新功能 happy path 只依赖核心迭代 workflow：`aisee:srs`、`aisee:ui-content`、`aisee:architecture`、`aisee:change-plan`、`aisee:change-author`、`aisee-schema-pack`、`aisee:implementation-bridge`。

以下能力按条件触发，不是每次都要走：

- `aisee:design-spec` / `aisee:design-assets`：只有存在视觉规范、参考图或素材需求时才进入。
- `aisee:svg-assets` / `aisee:image-object`：只有素材生产或图片处理工作时才进入。
- `aisee:spec-migrate`：只用于已有项目建立 baseline spec，不是每次迭代必经步骤。
- `aisee:memory`：只用于项目记忆的受控检索、写入和索引维护。
- `aisee:reflect` / `aisee:knowledge-curate`：只用于复盘、项目记忆候选和团队知识沉淀。
- `hw:*`：仅用于硬件、嵌入式或实验域，不影响 app 默认流程。

## 1. 前置澄清

目标是把聊天里的想法转成可审查输入，而不是直接进入实现。

推荐顺序：

```text
aisee:srs
  -> aisee:ui-content（有 UI 时）
  -> aisee:architecture
```

如果有视觉规范、参考图或素材需求，再按需进入 `aisee:design-spec` / `aisee:design-assets`；它们不是默认新功能主路径的必经节点。

产出定位：

| 产物 | 作用 | 注意 |
| --- | --- | --- |
| SRS | 澄清业务目标、范围、功能需求、非功能需求和验收标准 | 不写实现任务 |
| UI Content | 描述页面内容、状态、操作、权限可见性和前端数据需求 | 不写组件库、配色、排版 |
| Design Spec / Assets | 描述或生成视觉规范、参考图、素材和风格输入 | 不重复页面内容 |
| Architecture | 记录技术事实、架构边界、平台约束、共享约定和风险 | 不替代 change artifact |

这些前置文档是当前版本 / 迭代的 planning docs，是 change planning 的输入，不是 OpenSpec baseline。

## 2. Change 规划

用 `aisee:change-plan` 把已确认输入拆成可独立交付的 OpenSpec changes。一个版本 / 迭代可以拆成 one or more changes。

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
- 小范围、边界明确、低风险工作可以跳过 SRS / UI / Architecture 等重前置文档，直接进入合适的轻量 schema。
- 前后端共享接口、事件、数据模型或 SDK 时，优先规划一个前置 contract change。

## 3. Change 创建与 Authoring

创建 change 后，用 `aisee:change-author` 按 schema artifact DAG 补齐文档。

典型命令：

```bash
/opsx:new "<change>" --schema aisee-app-spec-driven
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
- Upstream Sources / Trace 表记录来源 `Ref` / `Refs`；当前 change 内新对象使用文档内编号。

## 4. 实现交接

进入实现前，先确认 change 已 authored。

```bash
aisee context pack --change <change> --for ce-work --json
```

如果项目有长期本地 guidance，例如提交偏好、测试命令、架构决策摘要或技术栈约束，可以显式检索项目记忆：

```bash
aisee memory search --query "<当前实现任务>" --json
aisee context pack --change <change> --for ce-work --project-memory --json
```

Project memory matches 只作为 guidance，不改变当前 change 的规范事实源，也不应复制进 OpenSpec artifacts。

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

只读 Aisee reviewer lens 的触发时机：

| Reviewer | 触发时机 | 用途 |
| --- | --- | --- |
| `aisee-change-architect` | `aisee:change-plan` 后、`aisee:change-author` 前按需触发；仅用于边界复杂、跨模块、跨 schema、依赖不清或粒度不确定的 change | 审查 change 边界、依赖、粒度和可独立交付性 |
| `aisee-spec-reviewer` | `aisee:change-author` 后、`aisee:implementation-bridge` / `ce-work` 前建议触发 | 审查 artifacts、contracts、source-map、tasks 是否完整、一致、可验证 |
| `aisee-implementation-reviewer` | `ce-work` 完成后建议触发 | 比对实现、tasks、spec/source-map 和 evidence 是否一致 |

这些 reviewer 只输出结构化审查结论，不改代码、不跑测试、不提交 PR，也不替代 `ce-doc-review`、`ce-code-review`、`ce-test-*` 或 `ce-work`。接口、UI、硬件、固件、安全和验证差异应作为 schema-aware check lenses，而不是新增独立全能 agent。

## 6. Verify

实现后运行：

```bash
openspec validate <change>
aisee context pack --change <change> --for aisee-verify --json
```

再使用 `aisee:verify` 或人工审查输出一致性报告，重点检查：

- schema artifacts 是否存在。
- Required=yes contracts 是否闭合。
- source-map、文档内编号、代码路径、测试路径和 evidence 是否一致。
- `tasks.md` 或 apply tracks 是否真实完成。
- OpenSpec validate 是否通过。
- review/test/manual evidence 是否足够。
- 是否仍需要 Tier 2 review。

确认 `openspec validate` 通过、apply tracks 关闭、review/test/manual evidence 齐全且 accepted risk 已说明后，执行：

```bash
openspec archive <change>
```

## 7. Project Memory 使用

项目记忆服务当前仓库长期 guidance，不服务跨项目复用，也不替代 OpenSpec。

推荐路径：

```bash
aisee memory inspect --json
aisee memory search --query "<task>" --json
aisee memory add --type pref --title "<title>" --summary "<summary>" --body "<body>" --json
aisee memory update-index --json
```

边界：

- 默认检索只返回少量 active metadata，不返回完整正文。
- 只有用户明确说“记住 / 以后本项目都 / 写入项目记忆”时才写入。
- 写入只进入 canonical `aisee/memory/`；legacy `.memory/` 只作为 fallback 读取。
- hooks 只读，不自动写 memory。
- 与 OpenSpec artifacts、`source-map.md` 或 `tasks.md` 冲突时，以 OpenSpec 相关产物为准。

## 8. Team Knowledge 复用

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
| 新功能 | SRS -> UI/Architecture -> change-plan -> change-author -> implementation-bridge -> implementation / review / test -> archive |
| 小修复 | `quick-fix` schema -> change-author -> implementation-bridge -> implementation / review / test -> archive |
| 技术调研 | `quick-research` schema -> findings/recommendation -> validate -> archive |
| 文档站变更 | `aisee-docsite-driven` schema -> doc-change/tasks -> build/link evidence -> archive |
| 不确定从哪开始 | `aisee:orient` -> 推荐下一步 skill / workflow |
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
