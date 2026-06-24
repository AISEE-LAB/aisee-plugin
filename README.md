<p align="center">
  <img src="https://raw.githubusercontent.com/AISEE-LAB/aisee-plugin/main/assets/aisee-logo-wordmark.svg" alt="Aisee" width="560">
</p>

<p align="center">
  <strong>规范先行，交接更稳，知识复利。</strong>
</p>

<p align="center">
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/README.en.md">English</a> · 简体中文
</p>

<p align="center">
  <a href="https://aisee.wiki">网站</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin">GitHub</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/workflow.md">Workflow</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/best-practices.md">Best Practices</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/plugin-marketplace.md">Plugin Marketplace</a> ·
  <a href="https://pypi.org/project/aisee-plugin/">PyPI</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/aisee-plugin/"><img src="https://img.shields.io/pypi/v/aisee-plugin" alt="PyPI"></a>
  <a href="https://pypi.org/project/aisee-plugin/"><img src="https://img.shields.io/pypi/pyversions/aisee-plugin" alt="Python"></a>
  <a href="https://github.com/AISEE-LAB/aisee-plugin/actions/workflows/ci.yml"><img src="https://github.com/AISEE-LAB/aisee-plugin/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/AISEE-LAB/aisee-plugin/stargazers"><img src="https://img.shields.io/github/stars/AISEE-LAB/aisee-plugin?style=social" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

# Aisee Plugin

> Aisee Plugin is a Codex-oriented OpenSpec companion for baseline migration, change authoring, and engineering memory.

**Aisee** 是 **AI-Enhanced Software Engineering** 的缩写。

Aisee Plugin 是一个面向 OpenSpec 的 AI 软件工程 companion。它帮助团队接入 OpenSpec、为已有项目建立 baseline specs、把模糊意图整理成更清晰的 change 输入，并在实现前后提供项目记忆和团队知识 guardrails。

Aisee **不替代 OpenSpec**。OpenSpec 仍然是规范状态机和 baseline 事实源。Aisee 在 OpenSpec 周围补充结构化 skills、project memory、team knowledge 和少量只读上下文工具。

它尤其适合希望让 Codex 和其他 coding agent 在开源仓库中更稳定协作的维护者：

- 用可持久复用的需求与规范，替代只存在于聊天记录里的临时上下文；
- 用 OpenSpec baseline、active changes、项目记忆和团队知识 guardrails，为实现前后的判断提供稳定输入；
- 用 baseline 迁移、意图澄清和 change authoring，帮助 maintainer 和 contributor 更快进入可审查的 OpenSpec 变更；
- 用更轻的产品面降低维护成本，避免让 Aisee 变成第二套 workflow authority。

## OpenSpec Boundary

Aisee 不替代 OpenSpec，也不维护第二套 schema 状态机。Aisee 处理 OpenSpec 时只做接入、baseline 迁移、意图澄清、detailed authoring 和少量只读上下文辅助；project memory 和 team knowledge 始终只是 guidance / guardrails。

当 Aisee 处理 OpenSpec artifacts 时，它只做 parser / checker / projector；`openspec validate` / `openspec archive` 仍由 OpenSpec 负责。

## 为什么这对 Codex 很重要？

Codex 能写代码、审代码、修 bug，但在仓库没有显式需求、稳定上下文、审查规则和验证标准时，结果容易依赖短期 prompt 历史。

Aisee 把这些材料前置为可复用的 companion 能力：

- 让 baseline、change、project memory 和 team knowledge 的边界显式存在；
- 帮助维护者先固化已有系统行为，再进入新 change；
- 让 Codex 在 change authoring 和实现阶段读取同一套最小上下文边界；
- 为开源仓库提供更明确的 AI 协作约束，降低 maintainer 反复补充背景的成本。

## 为什么需要 Aisee？

AI coding assistant 很有用，但当需求、UI 说明、技术约束和实现证据长期停留在聊天记录里时，项目很容易上下文漂移。

Aisee 的目标是让这些上下文显式化：

- 在实现前澄清业务需求或补齐已有系统 baseline；
- 把已有项目接入、baseline 迁移、change planning 和 change authoring 明确分层；
- 创建和补齐 OpenSpec changes，并优先围绕项目当前 schema 或官方 `spec-driven` 工作；
- 保持 OpenSpec 作为唯一持久规范事实源；
- 用 skill/template 约束文档内编号，减少临时发明和重复命名；
- 检查 artifacts、tasks、source-map、测试和 review evidence 是否闭环。

## 产品定位

Aisee 当前主推四类能力：

- OpenSpec 基础接入：`aisee openspec ensure`、`aisee:init`
- 已有项目 baseline 迁移：`aisee:spec-migrate`
- 意图理解与 change 输入：`aisee:srs`、`aisee:change-plan`、`aisee:change-author`
- 工程 guidance：`aisee:memory`、`aisee:knowledge`、`aisee:knowledge-curate`

## 工作流定位

```text
用户意图
  ↓
Aisee skills
  接入 OpenSpec、迁移 baseline、澄清需求、规划和细化 change
  ↓
spec-migrate / srs / change-plan / change-author
  为 baseline 或新 change 提供输入
  ↓
OpenSpec
  管理 active changes、baseline specs、validate、apply 和 archive
  ↓
Aisee CLI
  读取 OpenSpec/Aisee metadata，并提供项目记忆、团队知识与辅助检查能力
  ↓
Compound Engineering 或其它 coding agent
  消费 OpenSpec artifacts 与 memory/knowledge guidance
```

核心边界：

```text
OpenSpec = 规范状态机和 baseline 事实源
Aisee = OpenSpec companion、memory/knowledge guidance 与少量上下文辅助
Aisee CLI = 接入、检索与只读工具，不是第二份事实源
Compound Engineering = 可选的执行 / 审查 / 测试消费方
```

## Skill 分层

`plugins/aisee-plugin/.codex-plugin/plugin.json` 继续通过 `skills: "./skills/"` 暴露全部公开 skill，但当前主推路径只围绕 OpenSpec companion 核心与 memory/knowledge 展开。完整分类合同见 [Skill Taxonomy](plugins/aisee-plugin/references/skill-taxonomy.md)。

项目接入 / 治理：

- `aisee:init`

OpenSpec companion 主推能力：

- `aisee:spec-migrate`
- `aisee:srs`
- `aisee:change-plan`
- `aisee:change-author`

memory / knowledge：

- `aisee:reflect`
- `aisee:memory`
- `aisee:knowledge`
- `aisee:knowledge-curate`

legacy / transitional：

- `aisee:design-spec`
- `aisee:design-assets`
- `aisee:svg-assets`
- `aisee:image-object`
- `aisee-schema-pack`
- `aisee:implementation-bridge`
- `aisee:verify`
- `aisee:archive-guard`
- `hw:*`

## 功能特性

- **已有项目 baseline 迁移**：`aisee:spec-migrate` 反向整理现有系统当前行为，帮助已有项目先建立 OpenSpec baseline specs。
- **结构化需求澄清**：`aisee:srs` 通过对话澄清业务需求，并生成 change planning 所需需求输入。
- **OpenSpec change planning**：`aisee:change-plan` 将已确认输入映射为可独立交付的 OpenSpec changes。
- **Detailed change authoring**：`aisee:change-author` 细化 OpenSpec change 内容，强化 proposal、specs、design、tasks 的可实现性。
- **轻量 schema 兼容**：`aisee:implementation-bridge` 可直接消费 OpenSpec 官方 `spec-driven` 及其它轻量 schema；不会因为缺少 Aisee 专属增强字段而拒绝生成 bridge 上下文。
- **项目记忆**：`aisee memory` 受控检索和写入当前仓库长期 guidance，不替代 OpenSpec 事实源。
- **团队知识 Guardrails**：`aisee knowledge` 基于 pack/card 协议按需检索少量已审查工程经验，不把知识库变成第二份规范事实源。
- **受控记忆与知识检索**：`aisee memory` 与 `aisee knowledge` 直接提供项目记忆和团队 guardrails 查询，不升级为 workflow authority。
- **过渡中的 legacy 能力**：UI/architecture/schema-pack/verify 等旧能力仍公开存在，但不再属于当前主推路径。

## 环境要求

- Python 3.10+
- Git
- Node.js 和 OpenSpec CLI

OpenSpec 需要单独安装：

```bash
npm install -g @fission-ai/openspec@latest
```

Compound Engineering 是可选依赖。Aisee 可以通过 `aisee doctor --json` 检查关键 Compound skills 是否可用。

## 安装

推荐使用 `pipx` 安装 CLI：

```bash
pipx install aisee-plugin
```

也可以使用 `pip`：

```bash
python -m pip install aisee-plugin
```

开发或本地修改时可以从源码安装：

```bash
git clone https://github.com/AISEE-LAB/aisee-plugin
cd aisee-plugin
python -m pip install -e .
```

也可以先构建 wheel，再安装本地包：

```bash
python -m pip install build
python -m build
python -m pip install dist/aisee_plugin-*.whl
```

检查 CLI：

```bash
aisee --version
aisee doctor --json
```

也可以不安装，直接运行仓库内入口：

```bash
./bin/aisee doctor --json
```

## 插件使用

PyPI / pipx 只安装 `aisee` CLI。Aisee skills、references、schema packs、team knowledge templates 和 plugin metadata 通过 GitHub-backed Codex marketplace 分发。

在 Codex 中添加 marketplace 并安装插件：

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

检查 CLI 与插件内容状态：

```bash
aisee plugin inspect --json
aisee doctor --json
```

CLI 读取插件内容时默认只检查 Codex 安装位置。需要对接其它 agent runtime 时，可设置 `AISEE_AGENT_RUNTIME=claude|cursor|agents`；设置为 `none` 可关闭已安装插件内容发现。

插件内容、schema pack 和 team knowledge 模板通过 Codex marketplace 插件或外部仓库获取；team knowledge onboarding 使用 `aisee knowledge init-repo` 和 `aisee knowledge configure`。

源码仓库也包含多个 agent runtime 的插件元数据：

```text
plugins/aisee-plugin/.codex-plugin/plugin.json
plugins/aisee-plugin/.claude-plugin/plugin.json
plugins/aisee-plugin/.cursor-plugin/plugin.json
```

Codex plugin metadata 会直接声明 skills 目录：

```json
{
  "skills": "./skills/"
}
```

## 快速开始

在需要使用 OpenSpec 的项目内运行：

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee plugin inspect --json
```

如果项目还没有初始化 OpenSpec：

```bash
aisee openspec ensure --json
```

该命令会按当前 agent runtime 自动选择 OpenSpec tools（Codex 默认是 `codex`；无法识别时回退到 `none`），并默认启用 Aisee 需要的 expanded workflow，确保 OpenSpec 的项目内 instructions / skills 已安装或已刷新：

```text
write ~/.config/openspec/config.json   # profile=custom, delivery=both, workflows=expanded set
openspec init . --tools <detected-runtime-or-none> --profile custom
openspec update .
```

如果只想要 OpenSpec 的精简 `core` workflow，可显式传入：

```bash
aisee openspec ensure --profile core --json
```

如果只想创建 OpenSpec 目录而不安装 OpenSpec 提供的 agent skills / instructions，可显式传入：

```bash
aisee openspec ensure --tools none --json
```

Schema packs 来自 marketplace-installed plugin。`aisee schemas list/check` 只报告项目已安装 schema 状态或开发期源码 schema 状态；不会由 CLI 自动安装 schema。

再次检查项目状态：

```bash
aisee doctor --json
```

## 文档

- [文档站](https://aisee.wiki)：Aisee 使用指南、工作流和发布说明入口。
- [Aisee Workflow](docs/workflow.md)：说明当前主推的 OpenSpec companion 路径，以及 existing-project baseline 迁移入口。
- [Aisee Best Practices](docs/best-practices.md)：使用 Aisee 与 OpenSpec 时的事实源、保留能力、复用优先和 memory/knowledge 约定。
- [Compatibility Policy](docs/compatibility-policy.md)：说明 CLI JSON、保留 skill 面和 plugin content 的兼容边界。
- [Plugin Marketplace](docs/plugin-marketplace.md)：说明插件 manifest、marketplace listing、PyPI/pipx 和 Codex 安装路径的分工。
- [Team Knowledge Guardrails](docs/team-knowledge.md)：说明团队共享知识的实验性状态、使用方式和稳定前缺口。
- [Aisee Team Knowledge Architecture](docs/architecture/aisee-team-knowledge.md)：说明 team knowledge 的 guardrail retrieval 定位、card/pack 边界、CLI 初始化和读取模型。
- [Schema Packs](docs/schema-packs.md)：记录历史 schema pack 设计；当前产品面不再主推 repo 自带 schema。
- [Aisee / OpenSpec / Compound Engineering 融合方案](docs/architecture/aisee-openspec-compound-integration.md)：高层职责边界和历史决策快照。
- [OpenSpec 多 Schema 最佳实践](docs/architecture/openspec-multi-schema-best-practices.md)：多 schema 共存、冲突和管理规则。
- [CHANGELOG.md](CHANGELOG.md)：版本历史、发布说明和已发布版本的用户可见变更。

## 典型流程

```text
1. 已有项目 / 二开：`aisee:init` -> `aisee:spec-migrate`（按需）
2. 新需求：`aisee:srs`（按需）
3. `aisee:change-plan`
4. `/opsx:new "<change>" --schema <project-schema-or-spec-driven>`
5. `aisee:change-author`
6. `openspec validate <change>`
7. implementation / review / test
8. `openspec archive <change>`

对小范围、边界明确、低风险工作，也可以直接走：

```text
quick-fix / quick-research / 其它轻量 schema
  -> change-author
  -> implementation / review / test（完成当前批次前先回写 `tasks.md` / apply tracks）
  -> archive
```
```

实现前后可按需触发只读 Aisee reviewer lens：`aisee-change-architect`、`aisee-spec-reviewer`、`aisee-implementation-reviewer`。触发时机和边界见 [Aisee Workflow](docs/workflow.md)，复用优先规则见 [Aisee Best Practices](docs/best-practices.md)。

对于已有项目或基于现有系统做二次开发的场景，可先使用 `aisee:spec-migrate` 从代码、测试、文档、路由和已验证行为中整理 OpenSpec baseline specs，再进入新 change。

## 主要 Skills

| Skill | 作用 |
| --- | --- |
| `aisee:init` | 初始化或审计 `AGENTS.md`、`openspec/project.md`、Aisee docs、memory 和 Codex hooks。 |
| `aisee:spec-migrate` | 为已有项目或二开场景整理 OpenSpec baseline specs。 |
| `aisee:srs` | 澄清软件需求并生成 change planning 所需需求输入。 |
| `aisee:change-plan` | 规划独立 OpenSpec changes，并为 `/opsx:new` 提供范围和 schema 建议。 |
| `aisee:change-author` | 细化当前 OpenSpec change 内容，强化 proposal/specs/design/tasks 的可实现性。 |
| `aisee:memory` | 引导项目记忆 CLI 的 inspect/search/add/update-index 使用。 |
| `aisee:knowledge` | 引导团队知识 CLI 的初始化、配置、同步、检索和 promote 流程。 |
| `aisee:knowledge-curate` | 批量审查项目内 reusable knowledge candidates，产出可人工提交到 team knowledge 的 card drafts。 |
| `aisee:reflect` | 沉淀可复用项目经验和 memory / knowledge 候选。 |
| `legacy / transitional skills` | `aisee-schema-pack`、`aisee:implementation-bridge`、`aisee:verify`、`aisee:archive-guard` 及各类 design/hardware skills 仍公开存在，但不再属于当前主推路径。 |

## CLI Reference

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
aisee plugin inspect --json
aisee memory inspect --json
aisee memory list --json
aisee memory search --query "<task>" --json
aisee memory add --type pref --title "<title>" --summary "<summary>" --body "<body>" --json
aisee memory update-index --json
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
aisee knowledge check --team-path .aisee/team-knowledge --json
aisee knowledge install --json
aisee knowledge update --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee knowledge index --json
aisee knowledge index --team-path .aisee/team-knowledge --json
aisee knowledge promote-batch --curation <path> --team-path .aisee/team-knowledge --pack web-app --json
```

CLI 关键规则：

- JSON 输出只是上下文视图，不是事实源。
- `aisee memory` 管理当前仓库项目记忆；`aisee/cache/memory-index.json` 是可删除、可重建 cache。
- `aisee/cache/knowledge-index.json` 也是可删除、可重建的 cache；team knowledge 的持久来源是已 pin 的 pack/card 文件。
- `aisee knowledge promote-batch` 只写本地 team knowledge worktree，不自动 commit、push 或创建 PR。
- `bootstrap --plan` 是只读计划，不做大而全初始化写入。
- `aisee openspec ensure` 负责项目目录内 OpenSpec instructions / skills 的安装或刷新，并顺带对齐全局 profile；它不替代 `aisee:init`。
- `aisee knowledge query` 只返回少量 guardrails；默认只读 pack manifest 和 card frontmatter，`--debug` 才包含命中 card 的正文摘要。

### 项目记忆

项目记忆用于当前仓库长期有效、但不属于 OpenSpec baseline 的工程 guidance，例如稳定偏好、架构决策摘要、有时效的上下文快照和技术栈约束。

常用命令：

```bash
aisee memory inspect --json
aisee memory search --query "commit style" --json
aisee memory search --query "test command" --type stack --include-body --json
aisee memory add --type pref --title "提交信息语言" --summary "本项目提交信息默认使用中文。" --body "本项目 commit message 默认使用中文，并遵循 AGENTS.md。" --source-ref AGENTS.md --priority high --json
aisee memory update-index --json
aisee memory search --query "当前实现任务" --json
```

使用原则：

- `aisee:memory` 负责引导这些 CLI 的日常使用；`aisee:reflect` 仍负责会话复盘和候选生成。
- 默认检索只返回少量 active metadata；需要正文时显式使用 `--include-body`。
- 新写入只进入 canonical `aisee/memory/`；legacy `.memory/` 只作为 fallback 读取。
- hooks 只读，只提示 `inspect/search` 和少量高优先级摘要，不能自动写 memory。
- 项目记忆是 guidance；若与 OpenSpec artifacts、`source-map.md` 或 `tasks.md` 冲突，以 OpenSpec 相关产物为准。

### 团队知识 Guardrails

团队知识是实验性功能，用于跨项目复用工程经验，但不替代 OpenSpec、`source-map.md`、contracts、tasks 或 baseline specs。

业务项目可以在 `aisee/knowledge.yaml` 中 pin 独立知识仓库、本地路径、ref 和 packs：

```yaml
repo: git@example.com:org/aisee-team-knowledge.git
path: .aisee/team-knowledge
ref: v0.1.0
packs:
  - web-app
retrieval:
  max_cards: 3
  include_project_candidates: true
```

常用命令：

```bash
aisee knowledge init-repo --dest ../aisee-team-knowledge --initial-pack web-app --json
aisee knowledge configure --path ../aisee-team-knowledge --enable-pack web-app --json
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
aisee knowledge install --json
aisee knowledge update --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee knowledge promote-batch --curation <path> --team-path ../aisee-team-knowledge --pack web-app --json
```

使用原则：

- `aisee:knowledge` 负责引导这些 CLI 的日常使用，降低初始化、同步、检索和 promote 的门槛。
- `install`、`update` 和 `promote-batch` 是实验性能力；team knowledge 示例来自 marketplace plugin 或外部仓库。PR 自动化和 MCP 服务仍未稳定。
- 通过 CLI 查询，不让 AI 直接扫描 `knowledge/cards/**/*.md`。
- 只返回少量带边界的 matches，作为实现、review 或 verify 的提醒。
- 项目内 `aisee/docs/reflect/knowledge-candidates/` 仍是候选区，不自动进入 team knowledge。
- `aisee:knowledge-curate` 只生成审查报告和 card drafts；写入 team repo、创建分支、提交、合并或 PR 必须再次获得用户明确授权。

## 仓库结构

```text
.agents/plugins/marketplace.json
                     Codex marketplace listing
plugins/aisee-plugin/
  .codex-plugin/     Codex plugin metadata
  .claude-plugin/    Claude plugin metadata
  .cursor-plugin/    Cursor plugin metadata
  skills/            Aisee skills 和 skill assets
  references/        跨 skill contracts 和 references
bin/                 本地 CLI 入口
src/aisee_cli/       Aisee Python CLI
docs/                用户 workflow、最佳实践、架构和发布文档
docs/architecture/   架构文档
docs/plans/          开发计划
docs/reviews/        审计和 review 记录
scripts/             开发和发布辅助脚本
tests/               CLI 与 harness 测试
```

## 开发

运行测试：

```bash
python -m pytest
```

校验 skill eval JSON：

```bash
python -m pytest tests/test_skill_eval_schema.py
```

查看 CLI help：

```bash
python -m aisee_cli.__main__ --help
```

检查和同步版本号：

```bash
python scripts/check_versions.py
python scripts/sync_versions.py
```

构建 wheel：

```bash
python -m build
```

运行发布 smoke test：

```bash
python scripts/smoke_release.py
```

发布候选版本建议在本机具备 `pipx` 时运行隔离安装验证：

```bash
python scripts/smoke_release.py --with-pipx
```

## 设计原则

- OpenSpec 是 canonical specification source。
- 不在 Aisee docs、CLI cache 或聊天总结中创建平行事实源。
- Skill 保持单一职责：需求、UI 内容、架构、change planning、implementation bridge、verify、archive guard。
- 处理 OpenSpec change 时读取当前 schema 声明，不硬编码 app artifact 假设。
- `SKILL.md` 保持精简，长规则放到 references 或 architecture docs。
- 硬件和嵌入式流程作为专用扩展处理，不强行套入 app schema。

## 相关项目

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — 面向 AI coding assistants 的 spec-driven development 框架。
- [OpenSpec documentation](https://openspec.dev/) — OpenSpec 安装和工作流文档。
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — 面向 AI 工程执行、审查、测试、提交和团队知识沉淀的 agent workflow 插件。

## Roadmap

### 持续兼容治理

- 继续按 Compatibility Policy 维护 CLI JSON、project memory、team knowledge、marketplace plugin content 和 skill contracts；新增或破坏公开契约时同步补测试、迁移说明和 release notes。
- 用真实项目 dogfood 验证 memory 检索和 knowledge guardrails，不为了覆盖 schema 类型扩展抽象流程。

### 后续

- 补充更贴近 maintainer 场景的 Codex PR review / implementation brief 示例。
- 增加 sample OpenSpec change，帮助新仓库快速理解 Aisee 的交付形态。
- 扩展示例化的 verify / archive gate 文档，降低 OSS 维护者的试用门槛。
- 完善 project memory 的冲突提示、过期策略和低上下文注入规则。
- 收敛 team knowledge 的远程同步、promote workflow、生命周期管理和可选 MCP 包装。

## License

MIT。详见 [LICENSE](LICENSE)。
