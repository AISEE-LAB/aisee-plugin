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
.agents/plugins/marketplace.json
plugins/aisee-plugin/.codex-plugin/plugin.json
plugins/aisee-plugin/.claude-plugin/plugin.json
plugins/aisee-plugin/.cursor-plugin/plugin.json
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

从 `pyproject.toml` 同步版本到 CLI、marketplace listing 和 plugin metadata：

```bash
python scripts/sync_versions.py
```

`scripts/sync_package_assets.py` 仅保留为兼容入口。PyPI package 是 CLI-only，不再 mirror skills、references、schema packs、team knowledge templates 或 plugin metadata。

## 发布前检查清单

如本地没有 `build` 或 `twine` 模块，先安装：

```bash
python -m pip install build twine
```

```bash
python scripts/sync_versions.py
python scripts/check_versions.py
pytest -q
python scripts/smoke_release.py
```

## GitHub Actions 自动发布

`.github/workflows/publish-pypi.yml` 在 `main` 分支收到 push 或手动触发时运行：

- 先读取 `pyproject.toml` 中的版本号；
- 如果该版本已经存在于 PyPI，则跳过发布；
- 如果该版本不存在，则运行版本检查、测试、`scripts/smoke_release.py`、`twine check`，再发布到 PyPI。

`scripts/smoke_release.py` 会重新构建 dist、安装 wheel 到干净 venv，并检查 wheel / sdist 不包含完整 `skills/`、`references/`、schema pack trees、team knowledge templates 或 plugin metadata 副本。

当前 smoke 还必须证明：

- `aisee plugin inspect --json` 在 installed wheel 中返回 `mode=cli-only`；
- `aisee doctor --json` 仍输出 Codex marketplace setup hint；
- `aisee plugin export ...` 返回 argparse `invalid choice`，且不会创建目标目录；
- `aisee schemas list --json` 在 wheel-only 环境不报告 packaged schema source。

该 workflow 默认使用 PyPI Trusted Publishing，不在仓库中保存 PyPI token。PyPI 项目需要配置 trusted publisher：

```text
Owner: AISEE-LAB
Repository: aisee-plugin
Workflow: publish-pypi.yml
Environment: pypi
```

如果改用 GitHub secret token，应单独调整 workflow，不要同时保留无用的长期 PyPI token。

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
aisee schemas list --json
aisee schemas check --json
```

发布后的 CLI-only smoke 需要确认：

- `aisee doctor --json` 输出 `codex_marketplace` 检查结果；
- `aisee plugin inspect --json` 输出 CLI-only 状态和 Codex marketplace setup hint；
- wheel 中不包含完整 `skills/`、`references/`、schema pack trees、team knowledge templates 或 plugin metadata 副本。

Codex marketplace 真实安装 smoke 会写 Codex 本地配置，不放入默认 PyPI 发布 workflow。发布负责人可在已授权的本机环境中额外执行：

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

然后确认 Codex 能发现 Aisee skills，并运行 `aisee doctor --json` 查看 `codex_marketplace.status`。

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
- `docs/plugin-marketplace.md` 是否覆盖 plugin manifest、marketplace listing 和 Codex 安装路径。
- `plugins/aisee-plugin/references/skill-taxonomy.md`、README 和 workflow 是否仍与 core 11 / 扩展 skill 分层一致。
- 新增 skill、reference、schema pack 或 team knowledge template 是否位于 repository plugin content 源内，并能通过 Codex marketplace 安装读取。
- 新增 CLI JSON 字段是否有 contract tests。
- 破坏性或用户可见变更是否写入 `CHANGELOG.md`。
- 需要长期保留的发布决策是否写入 `aisee/memory/`。

与 root resolver 相关的公开行为变更前，还应确认 fixture / monorepo 场景测试仍通过，例如 `tests/test_doctor_flow_schema.py` 中从 Git 仓库子项目目录运行 `doctor` / `flow inspect` 不会错误解析到仓库顶层。

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

## 后续发布要求

- 发布路径验证通过，并在干净环境中完成 `pipx install aisee-plugin` smoke test。
- 推荐使用 project-scoped token 或 Trusted Publishing，避免长期使用 account-scoped token。

持续兼容治理必须维护：

- 明确 CLI JSON、schema packs、context pack、skill contract 和 marketplace plugin content 的兼容边界与版本升级规则。
- 明确 Public Contract、Experimental Contract 和 Internal Detail 的升级、弃用和迁移规则。
