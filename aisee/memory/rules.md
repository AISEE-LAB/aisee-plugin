# Memory Rules

> 项目本地记忆规则。
> 始终先读 `aisee/memory/index.md`，再只加载当前任务相关条目。

## 目录结构

```text
aisee/memory/
  index.md
  rules.md
  arch/
  pref/
  ctx/
  stack/
```

## 写入规则

1. 需要长期保留的项目约定、发布策略、架构决策和反复使用的工作流，应写入 `aisee/memory/`。
2. 会话总结、候选经验和未确认想法先放在 `aisee/docs/reflect/`，确认后再提升到 memory。
3. 写入 memory 文件后，必须同步更新 `aisee/memory/index.md`。
4. 不要把 OpenSpec change、baseline specs、contracts、tasks 或 source-map 复制进 memory。
5. Memory 是项目约定索引，不是第二份规范事实源。

## 文件类型

| 目录 | 用途 |
|---|---|
| `arch/` | 长期架构和流程决策 |
| `pref/` | 用户偏好和团队偏好 |
| `ctx/` | 有时效性的上下文快照 |
| `stack/` | 技术栈版本、配置和已知问题 |
