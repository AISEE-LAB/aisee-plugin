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

需要长期保留的结论必须回写到当前 OpenSpec change、baseline specs、schema apply tracks 或 source-map 等正式事实源。

## 1.1 默认走 Core Workflow，扩展能力按需触发

默认新功能 happy path 只应先走 core workflow。`design-*`、`svg-assets`、`image-object`、`spec-migrate`、`reflect`、`knowledge-curate` 和 `hw:*` 都是按需扩展，不要把它们平铺成每次迭代都必须经过的固定步骤。

## 2. 不要让前置文档替代 change artifacts

SRS、UI Content、Design Spec、Architecture 的作用是帮助规划当前版本 / 迭代的 changes。

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

## 3.1 小而低风险工作可以走轻路径

当工作同时满足“小范围、边界明确、低风险”时：

- 可以跳过 SRS / UI Content / Architecture 等重前置文档；
- 直接进入 `quick-fix`、`quick-research` 或其它合适轻量 schema；
- 仍然要保证当前 change artifacts、verify 和 archive gate 闭合。

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

## 6. source-map 负责路由，不负责解释全部业务

`source-map.md` 应记录：

- 上游来源或用户输入摘要；
- 当前 change 产出的文档内编号；
- artifact 适用性；
- 代码路径；
- 测试路径；
- evidence 路径；
- contract Required 状态。

不要在 source-map 中重写完整需求、页面流程、接口细节或数据库模型。详细内容应留在 specs、contracts 或对应 artifact 中。

## 7. 编号稳定，内容可演进

文档内编号用来减少重复命名，并让 source-map 和 context pack 能做轻量解析。

推荐：

- 文档内编号使用 `FR-001`、`PAGE-001`、`API-001`。
- 跨文档来源放进 `source-map.md`，只保留对实现和验证有用的路由信息。
- 临时 `TYPE-NEW-001` 只能短期存在，不能进入 archive。
- 删除或替换编号时保留迁移说明。
- 不把标题、文件名或自然语言描述当作稳定标识。

`source-map.md` 和 context pack 的可重建扫描视图只提供上下文入口；长期规范事实仍回写 OpenSpec artifacts 和 baseline specs。

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

## 9. 任务创建和执行先复用已有 workflow

创建任务、进入实现、提出审查角色或推荐下一步前，先检查已有 workflow 和 skill：

- 无明确 change 时，先回到需求澄清、change-plan 或当前 change 本身。
- 有明确 change 时，优先读取目标 context pack，例如 `aisee context pack --change <change> --for ce-work --json`。
- `ce-work` context pack 的 `reusable_workflow_candidates` 只是路由提示，不是事实源。
- `ce-work` context pack 的 blocker / risk / gap 默认也是 advisory projection；不要把它自动当成 OpenSpec 或人工审批的替代裁决。
- `requires_ce_plan=true` 时才按需使用 `ce-plan` 细化执行顺序；结论必须回写当前 schema apply tracks，只有 source-map schema 才回写 `source-map.md`。
- `requires_ce_plan=false` 且 paths/tasks 清楚时，优先 `aisee:implementation-bridge -> ce-work`。
- 不创建与 CE 重叠的执行、代码审查或测试 agent。

接口、UI、硬件、固件、安全和验证差异应作为 schema-aware check lenses。需要 Aisee reviewer 时，只使用 `aisee-change-architect`、`aisee-spec-reviewer`、`aisee-implementation-reviewer` 这三个只读一致性审查 role。

## 10. Implementation Brief 只做交接索引

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

## 11. Review 和 test evidence 必须可追溯

实现完成后至少要能回答：

- 跑了哪些测试？
- 哪些人工检查通过？
- 哪些 review 发现已处理？
- 哪些风险被正式接受？
- evidence 写在哪里？

公开 CLI、HTTP endpoint、API/service contract、schema、parser、路径读取、安全或隐私相关变更，建议走 Tier 2 code review。没有审查代理时，可以做本地重点自审，但必须记录限制。

## 12. Archive guard 不是形式步骤

不要把 `openspec archive` 当作“开发结束后随手执行”的命令。

archive 前应满足：

- `openspec validate <change>` 通过。
- `aisee:verify` 无 blocker。
- apply tracks 已关闭。
- Required=yes contracts 已闭合。
- review/test/manual evidence 足够。
- accepted risk 有 owner、理由、影响范围和后续处理方式。

`aisee:archive-guard` 给出“暂不建议 archive”时，应先修 blocker，而不是强行归档。

## 13. 跨仓库契约只读共享

前后端分离时，推荐 contract provider 暴露只读上下文：

```bash
直接读取当前项目内的 OpenSpec artifacts 或 `aisee context pack` 输出
```

最佳实践：

- provider 拥有 contract source。
- consumer 只读取 provider 明确提供的 OpenSpec artifacts、契约附件或 context pack 摘要。
- 用人工确认的路径和摘录控制上下文大小。
- 不暴露源码、密钥、环境变量或全仓库搜索结果。

## 14. Project memory 只提供当前项目 guidance

Project memory 用于当前仓库长期有效、但不属于 OpenSpec baseline 的 guidance。

推荐：

- 用 `aisee memory inspect --json` 发现状态和命令入口。
- 用 `aisee memory search --query "<task>" --json` 按任务检索少量 active metadata。
- 需要正文时显式传 `--include-body`，不要默认读完整正文。
- 只有用户明确要求长期记住时，才用 `aisee memory add ... --json` 写入。
- 用 `aisee memory update-index --json` 重建 `index.md` 和 cache。

避免：

- 直接递归读取整个 `aisee/memory/` 或 `.memory/` 树作为 AI 上下文。
- 把 project memory 写进 OpenSpec artifacts，或把它当 baseline 事实源。
- 让 hooks 自动写 memory。
- 把 `aisee/cache/memory-index.json` 当事实源。
- 将当前项目 memory 复制到团队知识库；跨项目复用应先走 `aisee:knowledge-curate`。

## 15. Team knowledge 只提供 guardrails

团队知识库用于跨项目复用工程经验，但不能成为第二套规范事实源。

推荐：

- 使用独立 `aisee-team-knowledge` 仓库存放经审查的 cards 和 packs。
- 业务项目只在 `aisee/knowledge.yaml` pin repo/path/ref/packs。
- 通过 `aisee knowledge query` 获取少量 matches。
- 让 CLI 先读 pack manifest 和 card frontmatter，再按需读取命中摘要。
- 只在用户明确触发时运行 `aisee:reflect` 或 `aisee:knowledge-curate`。
- 写入 team knowledge repo、创建分支、提交或 PR 前必须获得用户明确授权。

避免：

- 直接扫描 `knowledge/cards/**/*.md` 作为 AI 上下文。
- 把 `docs/solutions/`、memory 或 reflect 文档整库复制到业务项目。
- 把 evidence 当成 card 硬必填字段。
- 让向量索引、cache 或 AI 摘要成为事实源。
- 在 archive、verify 后自动写入 team knowledge。

## 16. 不要把 Aisee 做成另一个 OpenSpec

Aisee 应解决 OpenSpec 不负责的部分：

- 前置澄清；
- schema-aware 规划；
- 文档内编号约束和 source-map 路由；
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

## 17. 从真实项目 dogfood，而不是无限补抽象

主链路可用后，优先用真实或样例项目验证：

```text
init -> srs -> ui-content -> architecture -> change-plan
-> change-author -> implementation-bridge -> implementation
-> verify -> archive-guard -> archive
```

每轮 dogfood 只修真实暴露的问题。不要因为“可能未来需要”提前设计大型抽象。
