# Aisee CLI Preflight

依赖 Aisee CLI 的 skill 在调用 `aisee ...` 命令前必须先确认 CLI 可用：

```bash
aisee --version
```

如果命令不可用，停止当前 CLI-dependent 流程，并提示用户安装或升级：

```bash
pipx install aisee-plugin
```

如果需要 Aisee plugin content、schema packs、references 或 team knowledge templates，同时提示用户通过 Codex marketplace 安装插件内容：

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

边界：

- Marketplace installation 不会安装 `aisee` CLI。
- PyPI / pipx installation 不会安装 bundled skills、schema packs、references 或 team knowledge templates。
- CLI 只能提示 Codex marketplace setup，不写 Codex config、cache 或 plugin state。
