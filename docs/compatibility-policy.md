# Compatibility Policy

本文定义 Aisee Plugin 的公开契约分层和变更规则。目标不是冻结所有实现细节，而是明确哪些内容会影响用户项目、agent runtime、OpenSpec change 和下游自动化。

`0.x` 阶段允许较快演进，但公开契约变更必须被记录、测试并在 release notes 中说明。

## 契约分层

| 层级 | 含义 | 示例 | 变更要求 |
| --- | --- | --- | --- |
| Public Contract | 用户或自动化会依赖的公开接口 | CLI 命令、JSON 输出语义、schema artifact DAG、context pack 字段、plugin manifest / marketplace listing | 必须测试；破坏性变更必须升级版本并写入 changelog |
| Experimental Contract | 可试用但未承诺稳定的能力 | team knowledge 远程安装、promote-batch、可选 MCP、硬件主工作流整合 | 必须标注 experimental；允许调整，但要避免伪装成稳定能力 |
| Internal Detail | 可随实现变化的内部细节 | parser helper、缓存文件内容、临时索引、内部评分权重、测试 fixture 结构 | 不承诺兼容；不得作为用户事实源 |

## Public Contracts

### CLI JSON

以下属于公开契约：

- 命令是否存在；
- `--json` 输出是否是合法 JSON；
- `status`、`issues`、`summary`、`meta.command`、`meta.writes` 等跨命令基础语义；
- 已文档化字段的含义；
- 只读命令不得写入项目文件；
- 写入命令必须在 `meta.writes` 或命令文档中可识别。

允许的向后兼容变更：

- 新增字段；
- 新增 enum 值，但必须让旧消费者能忽略；
- 新增 warning / risk issue；
- 新增命令。

破坏性变更：

- 删除或重命名已文档化字段；
- 改变字段含义；
- 把只读命令变成写入命令；
- 改变退出码或 JSON 错误结构，使现有自动化无法判断失败；
- 默认读取过大上下文或泄露源码、密钥、环境变量。

### Schema Packs

以下属于公开契约：

- `schema.yaml` 名称和版本；
- artifact `id`、`generates`、`template`、`requires`；
- apply/archive tracks；
- 模板文件名和 artifact 适用性规则；
- `aisee-app-spec-driven` 的按需 contract 策略；
- `aisee-device-spec-driven` 作为硬件/嵌入式专用扩展的定位。

允许的向后兼容变更：

- 新增可选 artifact；
- 放宽模板要求；
- 增加说明性字段；
- 增加 N/A 规则；
- 新增 schema。

破坏性变更：

- 删除 artifact；
- 重命名 artifact 或模板文件；
- 改变 artifact DAG 导致既有 changes 无法验证；
- 将按需 artifact 改成默认强制；
- 让 Aisee schema 与 OpenSpec baseline 事实源产生平行事实源。

### Context Pack

字段级契约以以下文件为准：

- [references/context-pack-contract.md](../plugins/aisee-plugin/references/context-pack-contract.md)
- [references/context-pack-targets.md](../plugins/aisee-plugin/references/context-pack-targets.md)

规则：

- `facts.parsed` 表示从文件解析出的事实；
- `facts.derived` 表示 CLI 派生视图；
- `knowledge.matches` 是可选 guardrails，不得污染 `facts.parsed` 或 `facts.derived`；
- `project_memory.matches` 只在显式 `--project-memory` 时出现，不得污染 `facts.parsed` 或 `facts.derived`；
- `--for <target>` 只限定可选注入层的检索边界，不再承诺 execution / verify / review 的 target-specific 投影；
- context pack 可以变大，但默认输出必须保持可控；
- 新 target 必须说明消费方、读取顺序和缺失字段处理方式。

### Plugin Content

以下属于公开契约：

- GitHub 仓库中的 `plugins/aisee-plugin/.codex-plugin/plugin.json`、`plugins/aisee-plugin/skills/`、`plugins/aisee-plugin/references/` 和 schema pack 目录保持可被 Codex marketplace plugin 加载；
- `plugins/aisee-plugin/references/skill-taxonomy.md` 中 setup / core / optional / knowledge / hardware 分层，以及 core 9 skill 集合；
- `aisee plugin inspect --json` 在 PyPI / pipx 安装中返回稳定状态和 setup hint；
- PyPI / pipx 通道只承诺 CLI 能力；skills、references、schema packs、team knowledge templates 和 plugin metadata 通过 marketplace plugin 或外部仓库分发。

破坏性变更包括重命名插件、移除 Codex manifest、破坏 marketplace plugin root 布局，或改变 core workflow skill 集合。

### Plugin Marketplace

以下属于公开契约：

- 插件名称 `aisee-plugin`；
- `plugins/aisee-plugin/.codex-plugin/plugin.json` 保持存在且可被 Codex plugin validator 接受；
- Codex manifest 的 `skills` 字段指向可加载 skills 目录；
- marketplace listing 示例使用 `policy.installation`、`policy.authentication` 和 `category`；
- PyPI / pipx 安装与 plugin marketplace 安装是两个通道，CLI 不能依赖 marketplace 才能运行。

破坏性变更包括重命名插件、移除 Codex manifest、改变 marketplace listing 的策略语义，或把 marketplace listing 变成 OpenSpec、schema 或 source-map 的事实源。

具体说明见 [Plugin Marketplace](plugin-marketplace.md)。

### Planning Docs And Root Resolution

以下属于公开契约：

- 普通 planning docs 的 frontmatter 合同和 `aisee doctor --json` / `aisee context pack --json` 的只读 diagnostics；
- `status`、`doc_type`、`source_refs`、`change_refs` 等 planning doc 索引字段的基本语义；
- `resolve_project_root` 以最近的 Aisee/OpenSpec project marker 优先，再 fallback 到 Git 顶层的语义；
- release smoke 对 PyPI / pipx CLI、marketplace setup hint、公开命令面和 root resolver fixture 的检查重点。

破坏性变更包括把 planning doc diagnostics 变成写入命令，或改变 root resolution 使 monorepo 子项目误读为仓库顶层。

### Project Memory

以下属于公开契约：

- `aisee memory inspect/list/search/add/update-index --json` 命令存在且输出合法 JSON；
- project memory 的 canonical 路径是 `aisee/memory/`，legacy `.memory/` 只作为 fallback 读取；
- `inspect/search/list` 默认只读，`add/update-index` 必须通过 `meta.writes` 标记写入；
- 默认检索只返回 bounded metadata，不返回完整正文；
- `aisee/cache/memory-index.json` 是可删除、可重建 cache，不是事实源；
- `aisee context pack --project-memory` 只把 matches 放入独立 `project_memory` 字段。

破坏性变更包括删除命令、默认注入完整正文、把 memory 混入 OpenSpec facts、或让 hooks 自动写 memory。

## Experimental Contracts

当前仍为 experimental：

- Team knowledge `init-repo` / `configure` onboarding、远程安装、自动同步、promote-batch、PR 自动化和 MCP 包装；
- 硬件和嵌入式主工作流整合；
- 可运行的完整 lifecycle dogfood fixtures；
- schema sample changes 的最终目录和格式；
- semantic rerank / vector index。

Experimental 能力可以变化，但文档必须清楚说明：

- 当前可用能力；
- 明确不支持的能力；
- 是否会写入项目或远程仓库；
- 是否需要用户再次授权。

## Internal Details

以下不能作为事实源或稳定 contract：

- `aisee/cache/knowledge-index.json`；
- `aisee/cache/memory-index.json`；
- parser 内部 helper；
- scoring 权重；
- 构建缓存；
- 测试 fixture 的内部组织；
- chat summary。

缓存必须可删除、可重建；事实源只能来自 OpenSpec artifacts、source-map、tasks、明确 pin 的 team knowledge card/pack。Project memory 是项目 guidance，不是 OpenSpec 事实源。

## 版本规则

`0.x` 阶段：

- 破坏 Public Contract：至少 `MINOR`，并在 changelog 说明迁移影响；
- 新增 Public Contract：`MINOR`；
- 向后兼容修复或文档更新：`PATCH`；
- Experimental Contract 调整：通常 `PATCH` 或 `MINOR`，但必须保持文档准确。

正式稳定版本后：

- 破坏 Public Contract：`MAJOR`；
- 新增向后兼容能力：`MINOR`；
- 修复、文档、测试：`PATCH`。

## 变更检查

涉及 Public Contract 的 PR 或提交必须至少考虑：

- 是否更新 README / workflow / best practices / release 文档；
- 是否更新 skill taxonomy reference；
- 是否更新 schema pack 文档；
- 是否更新 context pack reference；
- 是否新增或调整 CLI contract tests；
- 是否运行 `python scripts/check_versions.py`；
- 是否运行相关测试和 `python scripts/smoke_release.py`。

推荐最小检查：

```bash
python scripts/check_versions.py
python -m pytest tests/test_plugin_packaging.py tests/test_doctor_flow_schema.py tests/test_version_consistency.py -q
python -m pytest -q
git diff --check
```

发布前还应运行：

```bash
python scripts/smoke_release.py
```
