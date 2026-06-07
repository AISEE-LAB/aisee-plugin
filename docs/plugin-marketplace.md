# Plugin Marketplace

本文说明 Aisee 如何兼容 agent 插件市场规范，以及它与 PyPI / pipx 安装的边界。

## 结论

Aisee 当前采用双通道分发：

```text
PyPI / pipx
  -> 安装 Aisee CLI
  -> 携带默认 skills / references / schema packs / plugin metadata

Plugin marketplace
  -> 让 agent runtime 发现、安装或排序 Aisee 插件入口
  -> 描述展示信息、分类、安装策略和认证策略
```

Public Beta 前，skills 继续打入 Python wheel。插件市场是 runtime 分发和发现通道，不是 CLI 的基础依赖。

## Manifest 与 Marketplace Listing

需要区分两类文件：

| 文件 | 职责 | 当前状态 |
| --- | --- | --- |
| `.codex-plugin/plugin.json` | 插件 manifest，描述插件名称、版本、skills 路径和 UI 展示信息 | 仓库已提供 |
| `marketplace.json` | 市场 listing，描述插件来源、安装策略、认证策略和分类 | 当前不内置，文档提供示例 |

`.codex-plugin/plugin.json` 属于插件本体。Aisee 源码仓库和 `aisee plugin export --target codex` 都会提供这个文件。

`marketplace.json` 属于某个 marketplace root。它通常不应强行写入 Aisee 源码仓库，因为不同用户、团队或市场的 `source.path`、安装策略和展示顺序可能不同。

## 当前 Codex Manifest

源码仓库包含：

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
```

Codex manifest 声明：

```json
{
  "name": "aisee-plugin",
  "version": "0.1.0",
  "skills": "./skills/",
  "interface": {
    "displayName": "Aisee",
    "category": "Coding"
  }
}
```

运行时导出：

```bash
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
```

导出目录：

```text
aisee-plugin-bundle/
  .codex-plugin/plugin.json
  skills/
  references/
```

## Marketplace Listing 示例

个人或团队 marketplace 可以引用导出的插件目录，也可以引用按 marketplace 规范摆放的插件目录。

示例：

```json
{
  "name": "team",
  "interface": {
    "displayName": "Team Plugins"
  },
  "plugins": [
    {
      "name": "aisee-plugin",
      "source": {
        "source": "local",
        "path": "./plugins/aisee-plugin"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

如果使用非默认 marketplace 文件，需要先让 runtime 安装或识别该 marketplace。默认个人 marketplace 和团队 marketplace 的管理方式由 agent runtime 决定。

## 与 PyPI / pipx 的关系

推荐关系：

- `pipx install aisee-plugin` 安装 CLI 和默认资源。
- `aisee plugin export` 从已安装包导出 agent runtime 可加载的插件目录。
- marketplace listing 指向导出的插件目录或团队管理的插件目录。

不推荐：

- 让 CLI 运行依赖 marketplace；
- 从 wheel 中移除默认 skills；
- 让 marketplace listing 成为 schema pack 或 OpenSpec artifact 的事实源；
- 为 Claude / Cursor 强行套 Codex marketplace 字段。

## 兼容承诺

以下属于 Aisee public contract：

- 插件名称 `aisee-plugin`；
- Codex manifest 的 `skills` 指向可加载 skills 目录；
- `aisee plugin export --target codex|claude|cursor` 的 target 名称；
- 导出目录包含目标 runtime metadata、`skills/` 和 `references/`；
- marketplace 示例使用 `policy.installation`、`policy.authentication` 和 `category`。

以下仍不承诺稳定：

- 具体 marketplace 文件位置；
- marketplace 展示顺序；
- team marketplace 的 source path；
- 远程 marketplace 分发机制；
- 自动安装、自动更新或自动认证流程。

## 发布前检查

涉及插件市场兼容时，至少运行：

```bash
python /Users/fengliang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python scripts/smoke_release.py
```

并人工确认：

- `.codex-plugin/plugin.json` 没有 unsupported fields；
- `aisee plugin export --target codex` 的导出目录能被 runtime 识别；
- marketplace listing 示例没有被写成唯一安装方式。
