# Plugin Marketplace

本文说明 Aisee plugin content、Codex marketplace 和 PyPI / pipx CLI 的职责边界。

## 结论

```text
GitHub / Codex marketplace
  -> 分发 Aisee skills / references / schema packs / team knowledge templates / plugin metadata

PyPI / pipx
  -> 安装 Aisee CLI
  -> 提供项目内 JSON context tooling、OpenSpec companion checks、registry、ID、knowledge query 等命令
```

Marketplace installation 不会安装 `aisee` CLI。PyPI / pipx installation 不会安装 bundled skills、schema packs、references 或 team knowledge templates。

## Codex 安装

在 Codex 中添加 GitHub marketplace 并安装插件：

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

CLI 只会提示这些命令，不会写 Codex config、cache 或 plugin state。

CLI 读取插件内容时默认只检查 Codex 安装位置；不会跨 agent runtime 扫描。需要指定其它运行时，可设置 `AISEE_AGENT_RUNTIME=claude|cursor|agents`；设置为 `none` 可关闭已安装插件内容发现。

## Manifest 与 Marketplace Listing

| 文件 | 职责 | 当前状态 |
| --- | --- | --- |
| `plugins/aisee-plugin/.codex-plugin/plugin.json` | 插件 manifest，描述插件名称、版本、skills 路径和 UI 展示信息 | 仓库已提供 |
| `.agents/plugins/marketplace.json` | Codex marketplace listing，指向 `plugins/aisee-plugin` plugin root | 仓库已提供 |

`plugins/aisee-plugin/.codex-plugin/plugin.json` 属于插件本体，声明：

```json
{
  "name": "aisee-plugin",
  "skills": "./skills/"
}
```

`.agents/plugins/marketplace.json` 属于 marketplace entry，source 指向仓库内的插件目录：

```json
{
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

## 与 PyPI / pipx 的关系

推荐关系：

- `pipx install aisee-plugin` 安装 CLI。
- Codex marketplace 安装 plugin content。
- `aisee doctor --json` 和旧内容分发命令可以提示 marketplace setup，但不执行安装。

不推荐：

- 让 CLI 写 Codex marketplace 或 plugin cache；
- 让 PyPI wheel 携带第二份 skills、references、schema packs 或 team knowledge templates；
- 让 marketplace listing 成为 OpenSpec、schema、source-map 或 team knowledge 的项目事实源；
- 为 Claude / Cursor 强行套 Codex marketplace 字段。

## 兼容承诺

以下属于 Aisee public contract：

- 插件名称 `aisee-plugin`；
- Codex manifest 的 `skills` 指向可加载 skills 目录；
- Codex marketplace 添加命令；
- CLI JSON 中 `status`、`issues`、`summary`、`meta` 和 setup hint 的基础语义；
- 公开旧命令在迁移期返回 stable deprecation/blocker，而不是静默写入旧 wheel assets。

以下仍不承诺稳定：

- Codex 内部 cache 路径；
- marketplace 展示顺序；
- Codex config 文件内部 schema；
- Claude / Cursor 的 marketplace-native 分发。

## 发布前检查

涉及插件市场兼容时，至少运行：

```bash
python /Users/fengliang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/aisee-plugin
python scripts/smoke_release.py
```

并人工确认：

- `plugins/aisee-plugin/.codex-plugin/plugin.json` 没有 unsupported fields；
- `.agents/plugins/marketplace.json` 指向 `./plugins/aisee-plugin` plugin root；
- `pipx install aisee-plugin` 只验证 CLI，不假设 wheel 内存在 plugin content。
