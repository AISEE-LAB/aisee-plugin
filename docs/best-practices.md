# Aisee Best Practices

本文记录 Aisee 插件的推荐使用约定。目标是让团队用 OpenSpec 管理事实源，用 Aisee 管理上下文和交接，避免把流程做重或制造第二套规范系统。

## 1. 保持 OpenSpec 是唯一规范事实源

OpenSpec baseline 和 active changes 是长期规范事实源：

```text
openspec/specs/
openspec/changes/
```

Aisee 文档、CLI JSON、Implementation Brief、review report 和聊天总结都不是 baseline。它们只能作为：

- 规划输入；
- 上下文视图；
- 实现交接；
- 验证 evidence；
- 后续改进建议。

需要长期保留的结论必须回写到当前 OpenSpec change、baseline specs、schema apply tracks、source-map 或 registry。

## 2. 不要让前置文档替代 change artifacts

SRS、UI Content、Design Spec、Architecture 的作用是帮助规划 change。

推荐：

```text
SRS / UI Content / Architecture
  -> aisee:change-plan
  -> OpenSpec change artifacts
```

避免：

```text
SRS 写完后直接实现
UI Content 充当 ui-contract
Architecture 充当 change-context
聊天记录充当 tasks
```

change 内 artifacts 应只写当前 change 必需的内容，不复制整份前置文档。

## 3. 一个 change 只承担一个可验证结果

好的 change 应满足：

- 可以独立 validate。
- 可以独立实现和测试。
- 可以独立 archive。
- 失败时不会影响无关 change 的判断。

避免把以下内容当成 change 边界：

- 文档章节；
- 技术层；
- 页面类型；
- schema artifact；
- 任务阶段；
- “前端一部分 / 后端一部分”这种无法独立验收的切分。

如果多个仓库需要协作，优先用 contract change 或前置共享 change 管住接口。

## 4. 按风险选择 schema，不要所有事情都走重流程

推荐选择：

| 场景 | Schema |
| --- | --- |
| 新功能、跨模块软件变更 | `aisee-app-spec-driven` |
| 单点低风险修复 | `quick-fix` |
| 技术调研或方案建议 | `quick-research` |
| 文档站变更 | `aisee-docsite-driven` |
| 基础设施变更 | `infra-change` |
| 安全相关变更 | `security-audit` |

`aisee-app-spec-driven` 适合需要 specs、source-map、contracts 和 tasks 闭环的变更。不要为了形式完整让每个小修复都生成 UI、service、data contract。

## 5. Required=yes 才展开按需 contract

app schema 的按需 artifacts 包括：

```text
change-context.md
ui-contract.md
service-contract.md
data-model.md
```

推荐做法：

- 在 `source-map.md` 中写明 Required=yes/no。
- Required=yes 时展开对应 contract。
- Required=no 时写具体 N/A 原因。
- 不要把 Required=no 的 contract 空模板留在 change 中制造噪声。

这能减少重复内容，也能降低 AI 上下文负担。

## 6. source-map 负责追踪，不负责解释全部业务

`source-map.md` 应记录：

- 上游 ID；
- 产出 ID；
- artifact 适用性；
- 代码路径；
- 测试路径；
- evidence 路径；
- contract Required 状态。

不要在 source-map 中重写完整需求、页面流程、接口细节或数据库模型。详细内容应留在 specs、contracts 或对应 artifact 中。

## 7. ID 稳定，内容可演进

ID 用来连接需求、页面、接口、数据、任务、代码和 evidence。

推荐：

- 实现前预留或确认 ID。
- 临时 ID 只能短期存在，不能进入 archive。
- 删除或替换 ID 时保留迁移说明。
- 不把标题、文件名或自然语言描述当作稳定 ID。

ID registry 是追踪输入，不是需求正文。

## 8. Context pack 是读取入口，不是新文档

`aisee context pack` 适合给 AI 提供小而准的上下文：

```bash
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for aisee-verify --json
aisee context pack --change <change> --for ce-code-review --json
```

使用规则：

- 只消费当前目标需要的字段。
- 不把 context pack 输出复制进长期文档。
- 发现缺口时回写当前 change artifact 或 apply tracks。
- 不绕过当前 change 去全仓库搜索后扩大范围。

## 9. Implementation Brief 只做交接索引

Brief 应包含：

- 必读路径；
- 允许修改路径；
- 当前批次目标；
- 验证命令；
- evidence 写回位置；
- review gate 建议。

Brief 不应包含：

- proposal 全文；
- specs 全文；
- contract 全文；
- 长期任务清单；
- 新需求；
- 未经 OpenSpec artifact 承认的业务事实。

大 change 可以分批 Brief，但仍属于同一个 OpenSpec change。

## 10. Review 和 test evidence 必须可追溯

实现完成后至少要能回答：

- 跑了哪些测试？
- 哪些人工检查通过？
- 哪些 review 发现已处理？
- 哪些风险被正式接受？
- evidence 写在哪里？

公开 CLI、HTTP endpoint、API/service contract、schema、parser、路径读取、安全或隐私相关变更，建议走 Tier 2 code review。没有审查代理时，可以做本地重点自审，但必须记录限制。

## 11. Archive guard 不是形式步骤

不要把 `openspec archive` 当作“开发结束后随手执行”的命令。

archive 前应满足：

- `openspec validate <change>` 通过。
- `aisee:verify` 无 blocker。
- apply tracks 已关闭。
- Required=yes contracts 已闭合。
- review/test/manual evidence 足够。
- accepted risk 有 owner、理由、影响范围和后续处理方式。

`aisee:archive-guard` 给出“暂不建议 archive”时，应先修 blocker，而不是强行归档。

## 12. 跨仓库契约只读共享

前后端分离时，推荐 contract provider 暴露只读上下文：

```bash
aisee contract serve --host 127.0.0.1 --port 8765
```

最佳实践：

- provider 拥有 contract source。
- consumer 先读 manifest，再按需读 summary 或 section。
- 用 `max_chars` 控制上下文大小。
- 局域网访问必须显式开启 `--host 0.0.0.0`。
- 不用 contract service 暴露源码、密钥、环境变量或全仓库搜索结果。

## 13. 不要把 Aisee 做成另一个 OpenSpec

Aisee 应解决 OpenSpec 不负责的部分：

- 前置澄清；
- schema-aware 规划；
- ID 和 source-map 追踪；
- AI context pack；
- 实现交接；
- verify / archive guard。

不应新增：

- 平行 specs；
- 平行 tasks；
- 平行 contract store；
- 平行 archive；
- 独立于 OpenSpec 的状态机。

当某个能力已经由 OpenSpec 原生提供时，Aisee 只应做衔接、校验或上下文优化。

## 14. 从真实项目 dogfood，而不是无限补抽象

主链路可用后，优先用真实或样例项目验证：

```text
init -> srs -> ui-content -> architecture -> change-plan
-> change-author -> implementation-bridge -> implementation
-> verify -> archive-guard -> archive
```

每轮 dogfood 只修真实暴露的问题。不要因为“可能未来需要”提前设计大型抽象。
