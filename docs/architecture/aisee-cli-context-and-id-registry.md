# Aisee CLI、上下文索引与编号规则

## 维护边界

本文描述当前生效的 Aisee CLI 上下文设计。

事实源以以下内容为准：

- `src/aisee_cli/`
- `plugins/aisee-plugin/skills/*/SKILL.md`
- `plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/`
- `tests/`

## 1. 目标

Aisee CLI 不是第二套规范系统。它只做四件事：

1. 检查环境、版本、插件资产和项目布局。
2. 解析 OpenSpec artifacts、`source-map.md`、tasks、evidence 和少量 planning doc metadata。
3. 生成面向实现、验证和 review 的 JSON context pack。
4. 管理团队知识仓库的只读检索、安装和批量提升辅助。

## 2. 编号模型

编号是 skill/template 的写作约束。

正式规则：

- 文档内编号使用 `FR-001`、`PAGE-001`、`ARCH-001`、`SPEC-001`、`TASK-001` 等格式。
- 无法确定最终编号时，使用 `TYPE-NEW-001` 并标注 `[NUMBERING-FINALIZATION-REQUIRED]`。
- 编号只用于减少重复命名、方便人工阅读和让 `source-map.md` / context pack 能做轻量解析。

## 3. 事实源分工

| 层 | 作用 | 是否事实源 |
|---|---|---|
| OpenSpec change artifacts / baseline specs | 规范事实、任务和归档依据 | 是 |
| planning docs | 版本 / 迭代输入，frontmatter 只做索引辅助 | 是，但不是 baseline |
| `source-map.md` | 当前 change 的来源、适用性、候选路径和 evidence 路由 | 是 |
| context pack 内部扫描视图 | 可重建的文档扫描视图 | 否 |

## 4. 命令职责

### `aisee context pack`

围绕当前 change 生成 schema-aware JSON：

- `facts.parsed`
- `facts.derived`
- `gaps`
- `guardrails`
- `evidence`

它依赖 `source-map.md`、当前 change artifacts、review / verification evidence 和 schema metadata。内部扫描只服务本次输出，不是持久事实源。

## 5. Source Map 规则

`source-map.md` 是当前 change 的上下文路由中心。

它记录：

- 上游来源或用户输入摘要
- 当前 change 产出的文档内编号
- artifact Required yes/no 和原因
- 候选代码 / 测试 / contract 路径
- 预期 evidence 入口
- 必要时记录 contract owner / provider / consumer / sync mode

它不记录：

- 具体实现步骤
- contract 字段细节
- 最终测试结论
- 长期 ID 生命周期

## 6. 结论

当前模型是：

```text
skills enforce numbering
OpenSpec owns specs/tasks/archive
source-map routes context
aisee CLI emits JSON views
Compound executes engineering work
```

编号保留为写作规则，CLI 不再把编号升级成独立产品面。
