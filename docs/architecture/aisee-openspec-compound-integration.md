# Aisee、OpenSpec 与 Compound Engineering 集成

## 维护边界

本文只记录 **当前生效** 的高层职责边界和主流程，不保留旧 full ID / `aisee id` lifecycle 作为现行方案。

细节以以下事实源为准：

- [aisee-cli-context-and-id-registry.md](/Users/fengliang/PycharmProjects/aisee-plugin/docs/architecture/aisee-cli-context-and-id-registry.md)
- [plugins/aisee-plugin/references/id-policy.md](/Users/fengliang/PycharmProjects/aisee-plugin/plugins/aisee-plugin/references/id-policy.md)
- `plugins/aisee-plugin/skills/*/SKILL.md`
- `plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/`

## 1. 三层分工

```text
Aisee
= 需求澄清、planning docs、change 边界规划、artifact 编排、上下文整理

OpenSpec
= schema、change artifacts、validate、archive、baseline specs

Compound Engineering
= implementation、review、test、commit、PR、reflect
```

核心边界：

- Aisee 不替代 OpenSpec state machine
- Compound 不替代 OpenSpec 规范事实源
- OpenSpec 不负责 AI 友好的上下文切片和路由
- Aisee CLI core 只绑定当前 schema contract，不绑定 `aisee-app-spec-driven` 的 artifact 语义

## 1.1 Schema capability boundary

当前正式规则：

- schema 必须声明 `capabilities`、artifact `requiredness`、`na_requires_reason`、`apply.tracks` 和 `archive.tracks`。
- Aisee CLI 只按 schema contract 做解析、门禁和投影，不再根据 `service-contract.md`、`ui-contract.md` 或 `source-map.md` 这些 app 名称推断全局规则。
- app-specific check 只能在当前 schema 显式声明对应 capability 时触发；轻量 schema 不补伪 source-map 或 app contracts。
- OpenSpec CLI 仍是 validate / archive authority；Aisee 只消费证据并增加 schema-aware 风险。

## 2. 当前正式流程

### 2.1 前置 planning docs

前置文档是 planning inputs，不是 baseline 事实源：

- `aisee:srs`
- `aisee:ui-content`
- `aisee:design-spec`
- `aisee:design-assets`
- `aisee:architecture`

这些文档只负责：

- 版本 / 迭代级输入
- delta / brief / inventory / evidence
- frontmatter 身份、状态和来源索引

不负责长期替代 OpenSpec baseline。

### 2.2 change 规划

`aisee:change-plan` 负责：

- 规划 one iteration -> one or more changes
- 选择 schema
- 给需要 `source-map.md` 的 schema 输出 source-map seed

它不负责：

- 生成 change artifacts
- 分配 full ID
- 把输入章节机械拆成 changes

### 2.3 change authoring

`aisee:change-author` 负责：

- 读取 schema
- 按 DAG 生成 proposal / source-map / specs / contracts / tasks
- 把上游 planning anchors 提升为当前 change artifacts

当前正式规则：

- 文档内使用 local ID
- 跨文档使用 anchor ref
- 不再要求 `aisee id reserve/activate/deprecate`

### 2.4 implementation

进入实现前使用：

- `aisee context pack --for ce-work`
- `aisee:implementation-bridge`

再进入：

- `ce-work`
- `ce-code-review`
- `ce-test-*`

### 2.5 verify / archive

使用：

- `aisee:verify`
- `aisee:archive-guard`
- `openspec validate`
- `openspec archive`

archive 后：

- baseline specs 成为当前规范事实源

## 3. 当前正式标识模型

正式模型只有两层：

- local ID
- anchor ref

示例：

```text
FR-001
PAGE-001
docs/requirements/auth-srs.md#FR-001
srs:auth-login#FR-001
```

以下不再是正式规则：

- `scope:TYPE-001`
- `aisee id reserve / activate / deprecate`
- `<!-- aisee:id ... -->`

如果历史仓库里仍有这些内容，只作为兼容诊断处理。

## 4. Source Map 与 Context Pack

`source-map.md` 是当前 change 的路由中心。

它连接：

- planning docs anchors
- current change local IDs
- artifact applicability
- implementation paths
- verification evidence
- cross-repo contract ownership

`aisee context pack` 则把这些最小事实切给：

- `ce-work`
- `aisee-verify`
- `ce-doc-review`
- `ce-code-review`

它不创建新的长期事实源。

## 5. 跨仓库协作

跨仓库消费者通过：

不再提供跨项目制品获取命令或本地只读服务；当前项目上下文通过 OpenSpec artifacts、`aisee context pack` 和 knowledge 检索提供。

读取 provider 明确暴露的片段。

规则：

1. manifest-first
2. anchor-aware
3. 不允许全仓库任意搜索
4. 只读

## 6. 当前迁移策略

如果仓库仍保留旧 full ID 文档：

1. 正文改为 local ID
2. `source-map.md` 改为 `Ref/Refs`
3. `sources.json` 增加 alias
4. `aisee get/trace` 改用 anchor ref
5. 旧 full ID 只保留短期兼容诊断，逐步清理

## 7. 结论

当前集成策略可以概括为：

```text
planning docs
-> change-plan
-> OpenSpec change artifacts
-> context pack / CE execution
-> verify / archive
-> baseline specs
```

其中：

- Aisee 负责规划和上下文
- OpenSpec 负责规范状态机
- Compound Engineering 负责工程执行
