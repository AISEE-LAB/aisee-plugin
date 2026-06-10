# Aisee、OpenSpec 与 Compound Engineering 集成

## 维护边界

本文记录当前生效的高层职责边界和主流程。旧 full ID lifecycle、独立 lookup / trace 命令、跨项目制品读取和本地 context 服务都不再属于当前方案。

细节以以下事实源为准：

- [aisee-cli-context-and-id-registry.md](/Users/fengliang/PycharmProjects/aisee-plugin/docs/architecture/aisee-cli-context-and-id-registry.md)
- `plugins/aisee-plugin/skills/*/SKILL.md`
- `plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/`
- `src/aisee_cli/`

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

- Aisee 不替代 OpenSpec state machine。
- Compound 不替代 OpenSpec 规范事实源。
- OpenSpec 不负责 AI 友好的上下文切片。
- Aisee CLI 只按当前 schema contract 做解析、检查和投影。

## 2. 当前正式流程

### 前置 planning docs

这些文档是版本 / 迭代输入，不是 baseline 事实源：

- `aisee:srs`
- `aisee:ui-content`
- `aisee:design-spec`
- `aisee:design-assets`
- `aisee:architecture`

编号规则由对应 skill 约束，例如 `FR-001`、`PAGE-001`、`ARCH-001`。编号用于写作一致性，不形成独立 CLI 生命周期。

### Change 规划

`aisee:change-plan` 负责：

- 将一次迭代拆成 one or more OpenSpec changes。
- 选择 schema。
- 为需要 `source-map.md` 的 schema 输出来源和路径 seed。

它不负责生成 change artifacts，也不机械分配全局 ID。

### Change authoring

`aisee:change-author` 负责：

- 读取 schema。
- 按 DAG 生成 proposal / source-map / specs / contracts / tasks。
- 把上游输入压缩到当前 change artifacts。

当前规则：

- 文档内编号由 skill/template 约束。
- 跨文档来源和候选影响路径由 `source-map.md` 记录。
- 不要求旧 ID lifecycle 或独立 lookup / trace 流程。

### Implementation

进入实现前使用：

- `aisee context pack --for ce-work`
- `aisee:implementation-bridge`

再进入：

- `ce-work`
- `ce-code-review`
- `ce-test-*`

### Verify / archive

使用：

- `aisee:verify`
- `aisee:archive-guard`
- `openspec validate`
- `openspec archive`

archive 后，baseline specs 成为当前规范事实源。

## 3. Source Map 与 Context Pack

`source-map.md` 是当前 change 的上下文路由中心。它连接：

- upstream planning docs 或 intake 摘要
- current change 文档内编号
- artifact applicability
- implementation paths
- verification evidence
- cross-repo contract ownership

`aisee context pack` 把这些最小事实切给：

- `ce-work`
- `aisee-verify`
- `ce-doc-review`
- `ce-code-review`

它不创建新的长期事实源。

## 4. 结论

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

- Aisee 负责规划和上下文。
- OpenSpec 负责规范状态机。
- Compound Engineering 负责工程执行。
