# Release And Version Governance

本文定义 Aisee Plugin 的版本号、发布检查和 release 交接规则，避免 Python 包、CLI 和多运行时 plugin metadata 版本漂移。

## 单一版本事实源

版本号的唯一事实源是：

```text
pyproject.toml [project].version
```

以下文件不得手动改成不同版本，必须通过脚本同步或由测试检查：

```text
src/aisee_cli/__init__.py
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
src/aisee_plugin_assets/plugin-metadata/codex/plugin.json
src/aisee_plugin_assets/plugin-metadata/claude/plugin.json
src/aisee_plugin_assets/plugin-metadata/cursor/plugin.json
```

## 版本号规则

Aisee 使用 SemVer：

| 类型 | 触发条件 |
|---|---|
| `MAJOR` | 破坏 CLI JSON contract、schema pack contract、skill 输入/输出边界或插件 metadata contract |
| `MINOR` | 新增 CLI 命令、skill、schema、向后兼容字段或新的可选工作流 |
| `PATCH` | bugfix、文档、测试、内部实现修复和不改变 contract 的小调整 |

`0.x` 阶段仍允许较快演进，但每次发布必须保持所有版本文件一致。

公开契约分层和破坏性变更判断见 [Compatibility Policy](compatibility-policy.md)。

## 本地检查

检查版本一致性：

```bash
python scripts/check_versions.py
```

从 `pyproject.toml` 同步版本到 CLI 和 plugin metadata：

```bash
python scripts/sync_versions.py
```

同步 package assets：

```bash
python scripts/sync_package_assets.py
```

## 发布前检查清单

如本地没有 `build` 或 `twine` 模块，先安装：

```bash
python -m pip install build twine
```

```bash
python scripts/sync_versions.py
python scripts/sync_package_assets.py
python scripts/check_versions.py
pytest -q
python scripts/smoke_release.py
```

## 构建与发布命令

构建发布包：

```bash
rm -rf dist
python -m build
python -m twine check dist/*
```

发布到 PyPI：

```bash
python -m twine upload dist/*
```

发布后使用干净环境验证：

```bash
python -m pipx install aisee-plugin
aisee --version
aisee doctor --json
aisee plugin inspect --json
aisee plugin export --target codex --dest /tmp/aisee-plugin-bundle --force --json
aisee schemas list --json
```

本地 Public Beta 候选验证应先跑：

```bash
python scripts/smoke_release.py
python scripts/smoke_release.py --with-pipx
```

`--with-pipx` 使用临时 `PIPX_HOME`、`PIPX_BIN_DIR` 和 `PIPX_MAN_DIR`，不会把候选包安装到用户默认 pipx 环境。若本机没有 `pipx`，该检查会明确失败；默认 smoke 不强制依赖 pipx。

发布前还需要人工确认：

- `README.md` 和 `README.en.md` 的安装、CLI 和 Roadmap 是否仍准确。
- `docs/workflow.md` 和 `docs/best-practices.md` 是否覆盖新增公开能力。
- `docs/compatibility-policy.md` 是否覆盖新增或破坏的公开契约。
- `docs/schema-packs.md` 是否覆盖新增或调整的 schema。
- `docs/plugin-marketplace.md` 是否覆盖 plugin manifest、marketplace listing 或 runtime export 变化。
- 新增 skill 是否同步到 `src/aisee_plugin_assets/`。
- 新增 CLI JSON 字段是否有 contract tests。
- 破坏性或用户可见变更是否写入 `CHANGELOG.md`。
- 需要长期保留的发布决策是否写入 `aisee/memory/`。

## Git Tag 规则

正式发布使用：

```bash
git tag v<version>
```

示例：

```bash
git tag v0.1.0
```

不要在版本不一致或测试未通过时打 tag。

## Roadmap 进入条件

正式 PyPI 发布前必须完成：

- 正式 PyPI 发布路径验证通过，并在干净环境中完成 `pipx install aisee-plugin` smoke test。
- README 安装说明从 pre-release guidance 更新为 public install guidance。
- 临时 account-scoped token 已撤销，发布认证切换为 project-scoped token 或 Trusted Publishing。

1.0 前必须完成：

- 冻结 1.0 兼容边界，明确破坏 CLI JSON、schema packs、context pack、skill contract 和 plugin export 的版本升级规则。
- 明确 Public Contract、Experimental Contract 和 Internal Detail 的升级、弃用和迁移规则。
