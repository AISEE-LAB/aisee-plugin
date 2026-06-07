# Version Governance

**日期：** 2026-06-07
**类型：** arch

## 摘要

Aisee Plugin 的版本号必须以 `pyproject.toml [project].version` 为唯一事实源。CLI `__version__`、runtime plugin metadata 和 packaged plugin metadata 不允许手动漂移。

## 详情

版本治理规则：

- 唯一事实源：`pyproject.toml [project].version`。
- 同步脚本：`python scripts/sync_versions.py`。
- 检查脚本：`python scripts/check_versions.py`。
- CI/本地测试：`tests/test_version_consistency.py`。
- 发布说明：`docs/release.md`。

版本号分布文件：

```text
src/aisee_cli/__init__.py
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
src/aisee_plugin_assets/plugin-metadata/codex/plugin.json
src/aisee_plugin_assets/plugin-metadata/claude/plugin.json
src/aisee_plugin_assets/plugin-metadata/cursor/plugin.json
```

发布前必须运行：

```bash
python scripts/sync_versions.py
python scripts/sync_package_assets.py
python scripts/check_versions.py
pytest -q
```

## 引用

- `pyproject.toml`
- `scripts/check_versions.py`
- `scripts/sync_versions.py`
- `tests/test_version_consistency.py`
- `docs/release.md`
