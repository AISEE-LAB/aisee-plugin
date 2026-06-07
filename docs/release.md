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

```bash
python scripts/sync_versions.py
python scripts/sync_package_assets.py
python scripts/check_versions.py
pytest -q
python -m build
aisee plugin export --target codex --dest /tmp/aisee-plugin-bundle --force --json
```

发布前还需要人工确认：

- `README.md` 和 `README.en.md` 的安装、CLI 和 Roadmap 是否仍准确。
- `docs/workflow.md` 和 `docs/best-practices.md` 是否覆盖新增公开能力。
- 新增 skill 是否同步到 `src/aisee_plugin_assets/`。
- 新增 CLI JSON 字段是否有 contract tests。
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

公开 beta 前必须完成：

- 安装路径稳定：PyPI/pipx、源码安装、plugin export、runtime loading。
- 版本治理稳定：单一版本事实源、同步脚本、检查脚本、测试覆盖。
- release checklist、changelog 和 tag 规则可执行。

1.0 前必须完成：

- `LICENSE`、`CONTRIBUTING.md` 和发布说明。
- CLI JSON、schema packs、skill contracts 的兼容策略。
- schema pack 文档、示例和完整 lifecycle dogfood fixtures。
