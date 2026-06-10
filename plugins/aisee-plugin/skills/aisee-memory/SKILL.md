---
name: aisee:memory
description: 引导项目记忆 CLI 的受控使用。用于用户询问项目记忆、aisee memory、记住这个、以后本项目都、查询本项目长期偏好或要求写入/更新 `aisee/memory/` 时触发。它负责使用 `aisee memory inspect/list/search/add/update-index`；会话复盘和候选生成仍优先交给 `aisee:reflect`。
---

# aisee:memory

引导 agent 低门槛使用项目本地长期记忆，避免手工全树扫描或把记忆误当 OpenSpec 事实。

## 职责

- 使用 `aisee memory inspect --json` 发现项目记忆状态、路径、类型和限制。
- 使用 `aisee memory search --query "<task>" --json` 检索少量任务相关记忆。
- 需要正文时显式使用 `--include-body`，只读取 bounded excerpt。
- 用户明确要求写入长期项目记忆时，通过 `aisee memory add` 写入 canonical `aisee/memory/`。
- 需要重建索引时运行 `aisee memory update-index --json`。
- 对“总结这次经验 / 生成候选 / 复盘”先转交 `aisee:reflect`，确认提升后再写 memory。

## 不负责

- 不自动写入记忆；写入必须来自用户明确意图。
- 不把项目记忆当 OpenSpec specs、tasks、contracts、source-map 或 baseline 的替代品。
- 不写全局用户记忆、home 目录记忆、跨项目记忆或 agent 私有存储。
- 不维护团队知识库；跨项目可复用知识仍交给 `aisee:knowledge-curate` 和 `aisee:knowledge`。
- 不让 `aisee/cache/memory-index.json` 成为事实源；它只是可删除、可重建 cache。

## Workflow

按用户目标选择模式；需要命令细节时读取 `references/workflow.md`。

| 用户目标 | 处理方式 |
|---|---|
| “检查项目记忆是否可用” | 运行 `aisee memory inspect --json`。 |
| “查一下本项目偏好/约定” | 运行 `aisee memory search --query "<task>" --json`；必要时按 `--type` 缩小范围。 |
| “实现时带项目记忆” | 显式使用 `aisee context pack --change <change> --for ce-work --project-memory --json`。 |
| “记住这个 / 以后本项目都...” | 先确认长期性和类型，再运行 `aisee memory add ... --json`。 |
| “复盘并沉淀候选” | 交给 `aisee:reflect` 生成候选；确认提升后再用 `aisee memory add`。 |
| “索引不一致 / 重建 memory index” | 运行 `aisee memory update-index --json`。 |

## Guardrails

- 读命令默认不返回正文；不要手工读取整个 `aisee/memory/` 树来替代 `search`。
- 写入前说明将写入 canonical `aisee/memory/<type>/`、会更新 `aisee/memory/index.md` 和 cache。
- `arch` 记录架构决策，`pref` 记录稳定偏好，`ctx` 记录有时效的上下文快照，`stack` 记录工具链/版本/环境约束。
- 如果 memory 与 OpenSpec、source-map 或 tasks 冲突，以 OpenSpec 相关产物为准，并提示用户是否更新 memory。
- 最终回复说明运行过的命令、命中条目数、写入路径和未验证风险。
