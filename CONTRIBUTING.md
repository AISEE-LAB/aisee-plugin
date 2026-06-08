# Contributing

感谢你改进 Aisee Plugin。贡献时请优先保持 OpenSpec、Aisee 和 Compound Engineering 的职责边界清晰。

## 开发环境

需要：

- Python 3.10+
- Git
- Node.js 和 OpenSpec CLI，只有涉及 OpenSpec 初始化或真实 change 验证时才必须安装

本地开发安装：

```bash
python -m pip install -e .
```

常用检查：

```bash
python -m pytest
python scripts/check_versions.py
python scripts/sync_package_assets.py
```

发布前 smoke test 见 [docs/release.md](docs/release.md)。

## 设计边界

- OpenSpec change 和 baseline specs 是规范事实源。
- Aisee skills 负责需求澄清、上下文组织、schema-aware planning、实现交接、验证和归档 guardrails。
- Aisee CLI 输出 JSON context view，不创建第二份规范事实源。
- `aisee/cache/*.json` 只能作为可删除、可重建的缓存。
- `tasks.md` 是唯一长期任务清单；计划结论必须回写 OpenSpec artifacts 或 Aisee registry。
- Team knowledge 只提供少量 guardrail retrieval，不替代当前项目的 specs、contracts 或 tasks。

## 修改 Skills

- 保持 `SKILL.md` 精简，只放触发条件、职责边界、核心流程和输出要求。
- 长规则、模板、审计说明和参考协议放入 `references/`、`docs/architecture/` 或 skill 自己的 assets。
- 不要把教程站正文、第三方长文或聊天记录原文直接放入仓库。
- 修改 `skills/` 后运行：

```bash
python scripts/sync_package_assets.py
python -m pytest tests/test_plugin_packaging.py tests/test_skill_eval_schema.py
```

## 修改 Schema Packs

Schema pack 源文件位于：

```text
skills/aisee-schema-pack/assets/schema-pack/
```

修改时需要保持：

- `schema.yaml` 的 artifact DAG 可解释；
- template 文件与 `generates`、`template` 字段一致；
- app schema 不强制生成不适用的 UI、service 或 data contract；
- device schema 作为硬件和嵌入式专用扩展保留，不混入 app 默认流程；
- 机器可读契约附件只做可追踪输入，不默认要求每个 change 生成。

相关说明见 [docs/schema-packs.md](docs/schema-packs.md)。

## 修改 CLI

CLI JSON 是公开接口面。修改时请同时考虑：

- 是否改变已有字段语义；
- 是否需要新增测试；
- 是否会把 OpenSpec artifact 之外的缓存误当事实源；
- 是否影响跨仓库 contract context 或 team knowledge retrieval。

建议至少运行：

```bash
python -m pytest tests/test_cli_context_bus.py tests/test_contract_context.py tests/test_contract_server.py
python -m pytest tests/test_knowledge_query.py tests/test_plugin_packaging.py
```

## 版本管理

版本号唯一事实源是：

```text
pyproject.toml [project].version
```

不要手动改出多个版本号。同步和检查：

```bash
python scripts/sync_versions.py
python scripts/check_versions.py
```

版本规则见 [docs/release.md](docs/release.md)。

## 提交规范

提交信息默认使用中文：

```text
<type>(<scope>): <中文主题>
```

示例：

```text
docs(readme): 补充 schema pack 文档入口
fix(cli): 修复 contract section 读取边界
```

提交前请检查工作区，只提交当前任务相关文件。

## Pull Request 建议

PR 描述建议包含：

- 变更动机；
- 主要文件；
- 是否影响 CLI JSON、schema pack、skill contract 或插件 metadata；
- 已运行的验证命令；
- 未覆盖风险。
