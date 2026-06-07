# Aisee Plugin

[English](README.en.md) | 简体中文

**Aisee** 是 **AI-Enhanced Software Engineering** 的缩写。

Aisee Plugin 是一个面向 OpenSpec 工作流的 AI 软件工程插件。它帮助团队把模糊想法整理成可审查的需求、UI 内容规格、技术架构上下文、schema-aware OpenSpec changes、实现交接 brief、验证检查和归档门禁。

Aisee **不替代 OpenSpec**。OpenSpec 仍然是规范状态机和 baseline 事实源。Aisee 在 OpenSpec 周围补充结构化 skills、schema packs、JSON context tooling、稳定 ID 追踪和工程交接规则。

> 当前状态：early alpha。仓库可用于本地实验和插件开发，但公开发布、安装自动化和版本化发行仍在完善中。

## 为什么需要 Aisee？

AI coding assistant 很有用，但当需求、UI 说明、技术约束和实现证据长期停留在聊天记录里时，项目很容易上下文漂移。

Aisee 的目标是让这些上下文显式化：

- 在实现前澄清业务需求；
- 分离需求、UI 内容、技术架构和 change planning；
- 以 schema-aware 的方式创建和补齐 OpenSpec changes；
- 保持 OpenSpec 作为唯一持久规范事实源；
- 为实现、验证和审查生成机器可读的 context pack；
- 追踪需求、页面、契约、任务、代码和证据 ID；
- 检查 artifacts、tasks、source-map、测试和 review evidence 是否闭环。

## 工作流定位

```text
用户意图
  ↓
Aisee skills
  澄清需求、UI 内容、架构和 change 边界
  ↓
OpenSpec
  管理 active changes、baseline specs、validate、apply 和 archive
  ↓
Aisee CLI
  读取 OpenSpec/Aisee metadata，输出 JSON context packs
  ↓
Compound Engineering 或其它 coding agent
  实现、审查、测试并产出 evidence
  ↓
Aisee verify / archive guard
  检查当前 change 是否可以进入归档
```

核心边界：

```text
OpenSpec = 规范状态机和 baseline 事实源
Aisee = 规划、上下文、schema、追踪和工作流 guardrails
Aisee CLI = JSON context bus，不是第二份事实源
Compound Engineering = 可选的执行 / 审查 / 测试消费方
```

## 功能特性

- **结构化需求澄清**：`aisee:srs` 通过对话澄清业务需求，并生成规划级 SRS。
- **UI 内容规格**：`aisee:ui-content` 将已确认需求转换为页面内容、状态、流程、权限可见性和平台差异，不写视觉设计。
- **技术架构上下文**：`aisee:architecture` 记录技术事实、约束、可复用能力、全局工程约定和 artifact hints。
- **Schema-aware change planning**：`aisee:change-plan` 将已确认输入映射为可独立交付的 OpenSpec changes。
- **OpenSpec schema pack**：提供 app、device、docsite、infra、security、quick-fix、quick-research、collaboration 等 schema。
- **Context packs**：`aisee context pack` 为实现、验证和 review 生成 JSON 上下文。
- **契约上下文服务**：`aisee contract` 以 manifest-first、section 级读取方式暴露服务契约，支持前后端跨仓库协作。
- **团队知识 Guardrails**：`aisee knowledge` 基于 pack/card 协议按需检索少量已审查工程经验，不把知识库变成第二份规范事实源。
- **ID registry 与 traceability**：`aisee id`、`aisee get`、`aisee trace` 连接上游文档、OpenSpec artifacts、tasks、代码路径、测试和 evidence。
- **验证与归档门禁**：`aisee:verify` 和 `aisee:archive-guard` 在 archive 前诊断缺口和风险。
- **Harness 设计**：通过 CLI contract tests 和规范化 skill eval cases 保持工作流稳定。

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

公开发布前，可直接从源码安装：

```bash
git clone <repository-url>
cd aisee-plugin
python -m pip install -e .
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

Python 包会同时携带 Aisee skills、schema pack、references 和 agent plugin metadata。可以先检查包内插件资源：

```bash
aisee plugin inspect --json
```

导出一个可被 agent runtime 加载的插件目录：

```bash
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
```

当前支持的 target：

```text
codex
claude
cursor
```

导出后的目录包含：

```text
aisee-plugin-bundle/
  .codex-plugin/plugin.json
  skills/
  references/
```

如果你的 agent runtime 支持加载本地插件，可以指向导出的目录或对应的 plugin metadata 文件。

源码仓库也包含多个 agent runtime 的插件元数据：

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
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

该命令使用保守默认值桥接 OpenSpec 初始化：

```text
openspec init . --tools none --profile core
openspec config profile core
```

然后安装本插件提供的 schemas：

```bash
aisee schemas install --all --json
```

再次检查项目状态：

```bash
aisee doctor --json
aisee flow inspect --json
```

## 文档

- [Aisee Workflow](docs/workflow.md)：端到端说明如何从初始化、需求澄清、change authoring、实现交接、验证到 archive。
- [Aisee Best Practices](docs/best-practices.md)：使用 Aisee 与 OpenSpec 时的事实源、schema、contract、context pack、review 和 archive 约定。
- [Aisee Team Knowledge Architecture](docs/architecture/aisee-team-knowledge.md)：说明 team knowledge 的 guardrail retrieval 定位、card/pack 边界和读取模型。
- [Aisee / OpenSpec / Compound Engineering 融合方案](docs/architecture/aisee-openspec-compound-integration.md)：高层职责边界和历史决策快照。
- [OpenSpec 多 Schema 最佳实践](docs/architecture/openspec-multi-schema-best-practices.md)：多 schema 共存、冲突和管理规则。
- [Release And Version Governance](docs/release.md)：版本号单一事实源、发布检查和 tag 规则。

## 典型流程

```text
1. aisee:srs
2. aisee:ui-content
3. aisee:architecture
4. aisee:change-plan
5. /opsx:new "<change>" --schema <schema>
6. aisee:change-author
7. openspec validate <change>
8. aisee:implementation-bridge
9. implementation / review / test
10. aisee:verify
11. aisee:archive-guard
12. openspec archive <change>
```

对于已有项目，可使用 `aisee:spec-migrate` 从代码、测试、文档、路由和已验证行为中整理 OpenSpec baseline specs。

## 主要 Skills

| Skill | 作用 |
| --- | --- |
| `aisee:flow` | 检查当前工作流阶段并推荐下一步。 |
| `aisee:init` | 初始化或审计 `AGENTS.md`、`openspec/project.md`、Aisee docs、memory 和 Codex hooks。 |
| `aisee:srs` | 澄清软件需求并生成规划级 SRS。 |
| `aisee:ui-content` | 生成页面、元素、状态、流程、权限和平台差异等 UI 内容规格。 |
| `aisee:architecture` | 捕获软件架构上下文、技术约束、可复用能力和 artifact hints。 |
| `aisee:change-plan` | 规划独立 OpenSpec changes 并选择 schema。 |
| `aisee-schema-pack` | 安装和维护 OpenSpec schema packs。 |
| `aisee:implementation-bridge` | 生成单个 change 的实现交接 brief 和 context pack 摘要。 |
| `aisee:verify` | 诊断 artifact、task、source-map、ID 和 evidence 缺口。 |
| `aisee:archive-guard` | 在 `openspec archive` 前给出最终归档建议。 |
| `aisee:spec-migrate` | 为已有项目整理 OpenSpec baseline specs。 |
| `aisee:design-spec` | 生成设计规范，不重复 UI 内容规格。 |
| `aisee:design-assets` | 生成或提取视觉参考和设计素材。 |
| `aisee:svg-assets` | 生成、矢量化、优化和校验 SVG assets。 |
| `aisee:image-object` | 对象级图片分割、mask、去背景和导出工作流。 |
| `aisee:reflect` | 沉淀可复用项目经验和工作流改进。 |
| `aisee:knowledge-curate` | 批量审查项目内 reusable knowledge candidates，产出可人工提交到 team knowledge 的 card drafts。 |

硬件相关 skills 已保留，但仍在整合到 Aisee 主工作流中：

```text
hw-init
hw-srs
hw-architecture
hw-change-plan
```

## Schema Packs

Schema pack 源位置：

```text
skills/aisee-schema-pack/assets/schema-pack/
```

当前包含：

| Schema | 适用场景 |
| --- | --- |
| `aisee-app-spec-driven` | App / 软件变更，包含 source-map、contracts、specs 和 tasks。 |
| `aisee-device-spec-driven` | 设备、固件、runtime、生产和验证相关变更。 |
| `aisee-docsite-driven` | 文档站变更。 |
| `infra-change` | 基础设施变更。 |
| `security-audit` | 安全审计工作流。 |
| `quick-fix` | 小型、边界清晰的修复。 |
| `quick-research` | 技术调研和建议。 |
| `opsx-collab-pr-loop` | 协作和 PR loop 工作流。 |

安装单个 schema：

```bash
aisee schemas install --schema aisee-app-spec-driven --json
```

安装全部 schemas：

```bash
aisee schemas install --all --json
```

检查 schema pack：

```bash
aisee schemas check --json --fail-on-blocker
```

## CLI Reference

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
aisee plugin inspect --json
aisee plugin path --target codex --json
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
aisee schemas list --json
aisee schemas check --json
aisee schemas install --all --json
aisee sources list --json
aisee sources check --json
aisee index --json
aisee flow inspect --json
aisee flow inspect --change <change> --json
aisee change inspect <change> --json
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
aisee context pack --change <change> --for aisee-verify --json
aisee knowledge inspect --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee knowledge index --json
aisee contract manifest --json
aisee contract summary --change <change> --json
aisee contract get --change <change> --artifact service-contract --section 能力契约 --json
aisee contract serve --host 127.0.0.1 --port 8765
aisee change verify-check <change> --json
aisee change archive-check <change> --json
aisee id check --json
aisee id reserve --scope <scope> --type <type> --count 3 --json
aisee get <id> --json
aisee trace <id> --json
```

CLI 关键规则：

- JSON 输出只是上下文视图，不是事实源。
- `aisee/cache/context-index.json` 只是可删除、可重建的 cache。
- `aisee/cache/knowledge-index.json` 也是可删除、可重建的 cache；team knowledge 的持久来源是已 pin 的 pack/card 文件。
- `aisee/registry/id-registry.json`、`aisee/registry/sources.json`、OpenSpec artifacts 和 `source-map.md` 是持久追踪输入。
- `bootstrap --plan` 是只读计划，不做大而全初始化写入。
- `aisee openspec ensure` 只桥接 OpenSpec 初始化和 profile 设置，不替代 `aisee:init`。
- `aisee contract serve` 是只读契约上下文服务，不是 mock backend、API gateway 或第二份接口事实源；默认只监听 `127.0.0.1`，如需局域网访问必须显式传 `--host 0.0.0.0` 并承担暴露本地契约文档的风险。
- `aisee knowledge query` 只返回少量 guardrails；默认只读 pack manifest 和 card frontmatter，`--debug` 才包含命中 card 的正文摘要。

### 跨仓库接口契约读取

当前后端分离在不同仓库开发时，建议由后端仓库、BFF 仓库或独立契约仓库维护 `service-contract.md` 与可选的机器可读附件，例如 `contracts/openapi.yaml`、`contracts/events.yaml`、`contracts/webhooks.yaml` 或 `contracts/proto/*.proto`。

推荐流程：

```bash
# 在契约提供方仓库
aisee contract manifest --json
aisee contract summary --change <change> --json
aisee contract serve --host 127.0.0.1 --port 8765

# 在消费方仓库的 AI 上下文中，先读 manifest，再按需读取小 section
curl http://127.0.0.1:8765/manifest
curl http://127.0.0.1:8765/changes/<change>/summary
curl "http://127.0.0.1:8765/changes/<change>/contracts/service-contract/sections/<section>?max_chars=4000"
```

契约权威来源仍然是 OpenSpec/Aisee artifacts。HTTP 服务只在请求时读取当前文件并返回 JSON 视图，不持久化契约副本，不暴露源码、环境变量、密钥或全仓库搜索结果。

### 团队知识 Guardrails

团队知识用于跨项目复用工程经验，但不替代 OpenSpec、`source-map.md`、contracts、tasks 或 baseline specs。

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
aisee knowledge inspect --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
```

使用原则：

- 通过 CLI 查询，不让 AI 直接扫描 `knowledge/cards/**/*.md`。
- 只返回少量带边界的 matches，作为实现、review 或 verify 的提醒。
- 项目内 `aisee/docs/reflect/knowledge-candidates/` 仍是候选区，不自动进入 team knowledge。
- `aisee:knowledge-curate` 只生成审查报告和 card drafts；写入 team repo、创建分支、提交、合并或 PR 必须再次获得用户明确授权。

## 仓库结构

```text
.codex-plugin/       Codex plugin metadata
.claude-plugin/      Claude plugin metadata
.cursor-plugin/      Cursor plugin metadata
bin/                 本地 CLI 入口
src/aisee_cli/       Aisee Python CLI
src/aisee_plugin_assets/
                     打包进 wheel 的 skills、schemas、references 和 plugin metadata
skills/              Aisee skills 和 skill assets
references/          跨 skill contracts 和 references
docs/                用户 workflow、最佳实践、架构、计划和 review 文档
docs/architecture/   架构与历史决策文档
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

同步包内插件资源：

```bash
python scripts/sync_package_assets.py
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

## 设计原则

- OpenSpec 是 canonical specification source。
- 不在 Aisee docs、CLI cache 或聊天总结中创建平行事实源。
- Skill 保持单一职责：需求、UI 内容、架构、change planning、implementation bridge、verify、archive guard。
- 优先使用 schema-aware 检查，而不是硬编码 artifact 假设。
- `SKILL.md` 保持精简，长规则放到 references 或 architecture docs。
- 硬件和嵌入式流程作为专用扩展处理，不强行套入 app schema。

## 相关项目

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — 面向 AI coding assistants 的 spec-driven development 框架。
- [OpenSpec documentation](https://openspec.dev/) — OpenSpec 安装和工作流文档。
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — 面向 AI 工程执行、审查、测试、提交和团队知识沉淀的 agent workflow 插件。

## Roadmap

### Public Beta 前

- 稳定公开安装路径：PyPI/pipx、源码安装、plugin export 和 runtime loading。
- 完成版本治理：`pyproject.toml` 作为唯一版本事实源，脚本同步 CLI 与 plugin metadata，测试检查版本漂移。
- 继续将 skill eval cases 规范化到 `aisee.skill-eval.v1`。
- 增加完整生命周期 workflow dogfood 和 scenario fixtures。

### 1.0 前

- 补充 schema pack 文档、示例和可运行的样例 changes。
- 补齐 `LICENSE`、`CONTRIBUTING.md`、release notes 和发布说明。
- 定义 CLI JSON、schema packs 和 skill contracts 的兼容策略。
- 完成 package build、plugin export 和安装后 smoke tests。

### 后续

- 将硬件和嵌入式工作流整合进 Aisee 体系。
- 扩展跨仓库契约协作示例和 team knowledge 工作流。

## License

MIT。当前 license 声明位于插件 metadata 中。
