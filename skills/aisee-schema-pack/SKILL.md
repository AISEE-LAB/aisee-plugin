---
name: aisee-schema-pack
description: 提供、审计、创建并维护 OpenSpec schema pack。用于从 marketplace-installed plugin 的 schema pack 内容初始化项目 openspec/schemas/，校验 schema.yaml 和模板路径，检查 artifact requires DAG、apply tracks、config rules 覆盖、schema 命名冲突，并按任务类型推荐 aisee-app-spec-driven、aisee-device-spec-driven、aisee-docsite-driven、quick-fix、quick-research、security-audit、infra-change、opsx-collab-pr-loop 等 schemas。触发词包括 aisee-schema-pack、aisee-opsx-schema、初始化 schema、安装 schemas、检查 OpenSpec schema、schema pack、custom schema、openspec schema validate。
---

# aisee-schema-pack

> 旧名称：`aisee-opsx-schema`。若用户仍使用旧名，按本技能处理。

## CLI preflight

调用 `aisee ...` 前先按 `references/cli-preflight.md` 确认 CLI 可用；schema pack 内容来自 marketplace-installed plugin，不来自 PyPI wheel。

命名策略：本 skill 暂时保留 `aisee-schema-pack`，不改为 `aisee:schema-pack`。原因是它管理的是可安装的 schema 包和脚本资产，已被文档、CLI 和安装路径引用；重命名会影响发现、安装和旧项目兼容。若未来统一命名，应单独做迁移计划，而不是在 schema 内容优化中顺手改名。

## 目标

管理 OpenSpec schema 扩展层，而不是 AI 配置层。

- 从本技能自带 schema pack 内容初始化目标项目的 `openspec/schemas/`。
- 审计现有 custom schemas 是否符合 OpenSpec 结构和团队最佳实践。
- 根据任务类型推荐合适 schema。
- 创建或调整 schema 时，保持模板路径、依赖图和 apply 语义正确。

`aisee:init` 负责 `AGENTS.md`、hooks、memory、`openspec/project.md`。`CLAUDE.md` 只作为旧项目兼容入口，不作为新项目主规则文件。本技能只负责 schemas。

## 先决条件

操作前确认目标项目已初始化 OpenSpec：

```bash
test -f openspec/config.yaml && test -d openspec/changes
openspec --version
```

如果缺少 OpenSpec 目录，先让用户运行：

```bash
openspec init
```

不要手动替代 `openspec init`。

## Schema Pack

自带 schema pack 位于 `assets/schema-pack/`：

| Schema | 适用场景 |
|---|---|
| `aisee-app-spec-driven` | 新功能、普通功能迭代、全栈或前后端分层开发；需要绑定 SRS / UI Content / Architecture / Change Plan 并细化 UI、服务、数据契约 |
| `aisee-device-spec-driven` | 嵌入式、固件、板级 bring-up、Linux 设备程序、32 位 MCU、RTOS 或 bare-metal 开发；需要细化硬件、固件、运行时和验证合同 |
| `aisee-docsite-driven` | 文档站、知识库、教程、团队 Wiki、内容导航和信息架构维护；不强制 specs，但归档前必须回写文档站基线 |
| `quick-fix` | 小 bugfix、文案/样式/静态配置小改、已知根因的低风险修复或紧急 Hotfix |
| `quick-research` | 不需要代码实现的技术调研、可行性分析、技术选型 |
| `security-audit` | 认证、授权、隐私、加密、外部输入等安全相关变更 |
| `infra-change` | CI/CD、部署、云资源、网络、服务器配置 |
| `opsx-collab-pr-loop` | PR review、外部调研、多轮协作任务 |

常用命令：

```bash
aisee schemas list --json
aisee schemas check --json
node <skill-dir>/scripts/setup-schemas.js --list
node <skill-dir>/scripts/setup-schemas.js --all
node <skill-dir>/scripts/setup-schemas.js --schema aisee-docsite-driven
node <skill-dir>/scripts/setup-schemas.js --schema aisee-docsite-driven --init-baseline
node <skill-dir>/scripts/setup-schemas.js --schema quick-fix
node <skill-dir>/scripts/setup-schemas.js --schema security-audit --force
```

`<skill-dir>` 是当前 skill 所在目录，例如仓库内 `skills/aisee-schema-pack` 或用户本地安装目录。不要假设目标项目根目录下存在 `aisee-schema-pack/scripts/`。

安装规则：

- 优先使用 `aisee schemas list/check --json` 获取机器可解析状态。`aisee schemas install` 是迁移期兼容命令，只返回 deprecation/blocker，不写入 schema pack。
- 需要写入 schema pack 时，使用本 skill 内 `scripts/setup-schemas.js` 或按确认后的文件清单从本 skill 的 `assets/schema-pack/<schema-name>/` 复制到项目 `openspec/schemas/<schema-name>/`。
- 写入 `openspec/schemas/<schema-name>/`。
- 已存在同名 schema 时默认跳过；`--force` 才覆盖。
- schema 可附带 `baseline-templates/`，使用 `--init-baseline` 初始化到项目 `openspec/` 下。
- baseline 已存在时默认跳过；`--force-baseline` 才覆盖。
- 安装后默认执行 `openspec schema validate <schema-name>`。
- 不修改 `openspec/config.yaml` 默认 schema，除非用户明确要求。

CHECKPOINT: 写入或覆盖 `openspec/schemas/**`、使用 `--force`、使用 `--init-baseline` 或 `--force-baseline` 写入 `openspec/project-docs.md` 等 baseline 文件、修改 `openspec/config.yaml` 默认 schema、创建/删除/重命名 schema 前，必须先列出目标路径、覆盖策略、baseline 影响、验证命令和回滚方式，等待用户确认。未确认时只输出审计报告或安装计划。

`aisee-docsite-driven` 附带 `baseline-templates/project-docs.md`，初始化后生成：

```text
openspec/project-docs.md
```

该文件是文档站长期基线，不属于单个 change artifact；每个 `aisee-docsite-driven` change 归档前必须回写它，或在 `doc-change.md` 写明无需回写原因。

## 推荐规则

- 新功能、普通功能迭代、全栈或前后端分层开发：优先使用 `aisee-app-spec-driven`。
- 嵌入式、固件、Linux 设备程序、驱动、RTOS、bare-metal、板级 bring-up：优先使用 `aisee-device-spec-driven`。
- 文档站、知识库、教程、Wiki、内容导航、阅读路径或信息架构维护：优先使用 `aisee-docsite-driven`。
- 小 bugfix、文案、样式、静态配置小改、已知根因的低风险修复或紧急 hotfix：使用 `quick-fix`。
- 需要新增业务能力、新 UI/API/DATA 契约、跨模块架构调整或上游 SRS/UI/Architecture 追踪时，不使用 `quick-fix`，改用 `aisee-app-spec-driven`。
- 无代码实现的调研：使用 `quick-research`。
- PR review 或多轮外部协作：使用 `opsx-collab-pr-loop`。
- 安全边界相关变更：使用 `security-audit`。
- 基础设施或发布变更：使用 `infra-change`。

如任务同时匹配多个 schema，优先选择风险控制更强的 schema。例如“紧急修复认证绕过”应选 `security-audit`，不是 `quick-fix`。

## 审计清单

读取目标 schema 的 `schema.yaml` 和 `templates/`，检查：

- 目录是否位于 `openspec/schemas/<name>/`。
- `schema.yaml` 是否包含 `name`、`version`、`description`、`artifacts`。
- artifact `id` 是否唯一。
- `template` 是否写成模板目录内文件名，如 `proposal.md`，不要写 `templates/proposal.md`。
- `requires` 是否只引用已存在 artifact，且无循环依赖。
- `generates` 是否符合 artifact 语义；spec delta 通常使用 `specs/**/*.md`。
- `apply.requires` 是否足以支持实现阶段。
- `apply.tracks` 是否指向实际需要打勾或维护的文件。
- artifact id 与 `openspec/config.yaml` 的 `rules` 是否匹配；不匹配时用 `instruction` 补齐团队约束。
- schema 名称是否避开官方内置 schema 名称，除非明确要覆盖。

更完整的多 schema 决策和冲突处理见 `references/multi-schema-best-practices.md`。

## 创建/修改规则

- 每个 schema 独立目录：`openspec/schemas/<schema-name>/schema.yaml` + `templates/`。
- 模板放在 `templates/`，但 `schema.yaml` 的 `template` 字段只写文件名。
- 项目级长期基线模板放在 `baseline-templates/`，不要放入 `templates/`。
- 依赖图从轻到重：proposal → source-map / specs → 按需 artifacts → tasks → apply。
- 只有会产生实现的 schema 才写 `apply`。
- 不要把 schema pack 内容写进 `aisee:init`。

修改后必须验证：

```bash
openspec schema validate <schema-name>
openspec templates --schema <schema-name>
```

如果是多 schema 项目，还要检查来源：

```bash
openspec schema which --all
```

## 输出格式

审计报告用中文：

```markdown
# OpenSpec Schema 审计报告

## 结论

## 问题

### [BLOCKER]
### [RISK]
### [IMPROVEMENT]

## 建议

## 已验证
```
