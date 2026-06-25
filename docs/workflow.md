# Aisee Workflow

本文描述 Aisee 与 OpenSpec 配合时的推荐软件开发流程。它参考 OpenSpec 的核心节奏：先提出 change，再补齐 artifacts，通过 validate，完成实现和验证，最后 archive 进入 baseline。

## 核心原则

- OpenSpec 是规范状态机和 baseline 事实源。
- Aisee 当前主推 OpenSpec 接入、baseline 迁移、意图澄清、change authoring 和 knowledge/memory 增强。
- Aisee CLI 输出 JSON context view，不创建第二份规范事实源。
- 实现、review、test 可以由 Compound Engineering 或其他 coding agent 承接。
- `openspec archive <change>` 是已验证 change 合入 baseline 的最终动作。
- planning docs 只服务当前版本 / 迭代输入，不替代 baseline facts。
- 普通 planning docs 使用统一 YAML frontmatter 合同做身份、状态和来源索引；OpenSpec change 和 baseline 仍是规范事实源。
- 文档内正式写法使用稳定编号；跨文档来源由 `source-map.md` 记录。

## 0. 项目初始化

适用于新项目或准备接入 OpenSpec 的已有项目。

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

如果是已有项目，或基于现有系统做二次开发，先不要直接写新 change。优先使用 `aisee:spec-migrate` 反向整理 baseline specs，再进入新需求开发。

## 默认主路径与按需扩展

`aisee:init` 属于项目入口接入 / 治理能力，不是默认新功能迭代 happy path 的必经节点。当前主推的新需求 / 新 change 路径只围绕 `aisee:srs`、`aisee:change-plan`、`aisee:change-author` 展开；已有项目接入或二开前补 baseline 时，再按需进入 `aisee:spec-migrate`。

以下能力按条件触发，不是每次都要走：

- `aisee:spec-migrate`：只用于已有项目 / brownfield 场景建立 baseline spec，不是每次迭代必经步骤。
- `aisee:memory`：只用于项目记忆的受控检索、写入和索引维护。
- `aisee:reflect` / `aisee:knowledge-curate`：只用于复盘、项目记忆候选和团队知识沉淀。
- 其它 legacy / transitional skills：当前仍公开存在，但不属于当前主推产品路径。

## 1. 前置澄清

目标是把聊天里的想法转成可审查输入，而不是直接进入实现。

推荐顺序：

```text
aisee:srs
  -> aisee:change-plan
  -> /opsx:new
  -> aisee:change-author
```

产出定位：

| 产物 | 作用 | 注意 |
| --- | --- | --- |
| SRS | 澄清业务目标、范围、功能需求、非功能需求和验收标准 | 不写实现任务 |
| Change Plan | 把已确认输入映射为一个或多个 OpenSpec changes | 不直接写 change artifact 正文 |
| Change Author | 按当前 schema 模板详细补齐当前 change 的各项文档，并在模板基础上补强边界、风险、验证和实施顺序 | 不写实现代码 |

这些前置文档是当前版本 / 迭代的 planning docs，是 change planning 的输入，不是 OpenSpec baseline。

## 2. Change 规划

用 `aisee:change-plan` 把已确认输入拆成可独立交付的 OpenSpec changes。一个版本 / 迭代可以拆成 one or more changes。

```text
aisee:change-plan
  -> change list
  -> dependency order
  -> schema recommendation
  -> /opsx:new 输入
```

拆分原则：

- 一个 change 对应一个可验证的用户价值或工程结果。
- 不把输入材料章节、技术层、页面类型、schema artifact 当成 change。
- 大 change 可以有依赖顺序，但不要让单个 change 承担整套产品。
- 低风险小修复可以使用 `quick-fix`，不强制走 app schema。
- 小范围、边界明确、低风险工作可以跳过重前置文档，直接进入合适的轻量 schema。
- 前后端共享接口、事件、数据模型或 SDK 时，优先规划一个前置 contract change。

## 3. Change 创建与 Authoring

创建 change 后，用 `aisee:change-author` 按当前 schema 模板详细补齐文档。先保留模板结构，再补强当前 change 最容易导致实现、评审或验证出错的信息。

典型命令：

```bash
/opsx:new "<change>" --schema <project-schema-or-spec-driven>
openspec validate <change>
```

常见的按需文档示例：

- `service-contract.md`
- `data-model.md`

当前规则：

- 只写当前 schema 声明的文档，不补未声明文件。
- 模板是基础骨架，不是完成条件；每个文档都应补强边界、例外、风险、验证或实施衔接中的必要内容。
- Required=yes 的文档必须展开；Required=no 的文档必须写清楚 N/A 原因。
- 不要为了“完整”强行生成与当前 change 无关的 contract 或辅助文档。
- 如果某个 schema 仍声明 `source-map.md`，把它当成该 schema 的普通文档按模板补齐，不把它当成整个 authoring 阶段的中心。

## 4. 实现交接

进入实现前，先确认 change 已 authored。

```bash
openspec/changes/<change>/
```

如果项目有长期本地 guidance，例如提交偏好、测试命令、架构决策摘要或技术栈约束，可以显式检索项目记忆：

```bash
aisee memory search --query "<当前实现任务>" --json
```

Project memory matches 只作为 guidance，不改变当前 change 的规范事实源，也不应复制进 OpenSpec artifacts。

如果项目配置了 team knowledge，可以在公开接口、schema、路径读取、安全、跨仓库契约等高风险实现前额外读取少量 guardrails：

```bash
aisee knowledge query --from-change <change> --for ce-work --json
```

Knowledge matches 只作为提醒，不改变当前 change 的规范事实源，也不应复制进长期 artifacts。

进入实现前，直接读取当前 change、schema、相关 artifacts、`tasks.md`、必要 evidence 入口和项目记忆 / 团队知识 guidance；不再依赖额外 Aisee implementation handoff skill。

## 5. 实现、Review 与 Test

实现阶段由 coding agent 或人工开发承接。无论使用什么工具，都应遵循：

- 只实现当前 change 范围。
- 如果发现 spec/contract/code 不一致，先回写当前 OpenSpec change，再继续实现。
- 不要等到 verify 或 archive 前再补写；`ce-work` 完成当前批次前，就应先更新 `tasks.md` 或当前 schema 的 apply tracks。
- 测试、人工验证、预览、监控或 review 结果必须作为 evidence 记录。

当 change 触及公开 CLI、HTTP endpoint、API/service contract、schema、parser、路径读取、安全或隐私表面时，建议执行 Tier 2 code review。

只读 Aisee reviewer lens 的触发时机：

| Reviewer | 触发时机 | 用途 |
| --- | --- | --- |
| `aisee-change-architect` | `aisee:change-plan` 后、`aisee:change-author` 前按需触发；仅用于边界复杂、跨模块、跨 schema、依赖不清或粒度不确定的 change | 审查 change 边界、依赖、粒度和可独立交付性 |
| `aisee-spec-reviewer` | `aisee:change-author` 后、进入实现前建议触发 | 审查当前 schema 文档、N/A 理由、tasks 和验证口径是否完整、一致、可验证 |
| `aisee-implementation-reviewer` | `ce-work` 完成后建议触发 | 比对实现、当前 schema 文档、tasks 和 evidence 是否一致 |

这些 reviewer 只输出结构化审查结论，不改代码、不跑测试、不提交 PR，也不替代 `ce-doc-review`、`ce-code-review`、`ce-test-*` 或 `ce-work`。接口、UI、硬件、固件、安全和验证差异应作为 schema-aware check lenses，而不是新增独立全能 agent。

## 6. Verify

实现后运行：

```bash
openspec validate <change>
```

再直接读取当前 change artifacts、schema、`tasks.md`、`source-map.md`（若适用）和 evidence，输出人工或工具化一致性审查结论，重点检查：

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
| 新功能 | SRS -> change-plan -> change-author -> implementation / review / test -> archive |
| 小修复 | `quick-fix` schema -> change-author -> implementation / review / test -> archive |
| 技术调研 | `quick-research` schema -> findings/recommendation -> validate -> archive |
| 文档站变更 | `aisee-docsite-driven` schema -> doc-change/tasks -> build/link evidence -> archive |
| 已有项目接入 / 二开前补 baseline | `aisee:init` -> `aisee:spec-migrate` -> baseline specs -> 新 change |

## 何时停止

遇到以下情况不要继续实现：

- 需求范围仍不清楚。
- 当前 change 无法映射到可验证 outcome。
- schema artifacts 缺失或互相矛盾。
- Required=yes contract 缺失。
- 实现路径没有被当前 change、`tasks.md` 或 `source-map.md`（若适用）指向。
- OpenSpec validate 失败且没有明确修复方向。

这时应回到对应 artifact 修补，而不是让实现阶段临时猜测。
