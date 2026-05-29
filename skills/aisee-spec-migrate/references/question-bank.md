# aisee:spec-migrate — 问题库

只问会影响 baseline spec 真实性、能力边界或写入位置的问题。

---

## 追问优先级

1. 迁移范围
2. OpenSpec 初始化状态
3. 能力边界
4. 当前行为证据
5. 代码 / 文档 / 测试冲突
6. Spec Owner 和确认责任

每轮最多 3 个问题。超过 3 轮仍不明确时写入 Open Questions。

---

## 迁移范围

- 这次要迁移整个项目，还是某个模块 / 目录？
- 是否已有 `openspec/specs/`，其中哪些 spec 是可信基线？
- 是否存在 active changes，不应被当成已上线行为？

## 能力边界

- 当前系统有哪些可独立修改的业务能力？
- 哪些能力属于全局约束：认证、安全、API 风格、测试、审计、可观测性？
- 哪些能力是跨模块协作，不应重复写在多个 spec 中？

## 当前行为证据

- 哪些测试、OpenAPI、路由或页面最能证明当前行为？
- 哪些 README / 产品文档已经过期？
- 是否有线上行为或运营规则没有写在代码里？

## 冲突和缺口

- 代码行为、测试和文档是否存在冲突？
- 是否有看似 bug 但被测试固定的当前行为？
- 哪些行为只能从命名推断，缺少可信证据？

## 写入策略

- 是否允许直接写入 `openspec/specs/`，还是先生成 migration index？
- 本次最多写入多少个 spec 文件？
- 每个能力的确认负责人是谁？

---

## 标签使用

缺少可信证据：

`[EVIDENCE-GAP] {行为} 缺少 high/medium 可信来源，暂不写入 baseline。`

代码、文档、测试冲突：

`[BEHAVIOR-CONFLICT] 代码：{code behavior}；文档：{doc behavior}；需要确认 baseline。`

当前行为疑似 bug：

`[CURRENT-BEHAVIOR] {behavior} 已被测试或代码固定；是否作为规范需要确认。`

需要负责人确认：

`[SPEC-OWNER-REQUIRED] {capability} 需要指定确认人。`

迁移范围过大：

`[MIGRATION-SCOPE] 范围过大；建议分批迁移 {batch suggestion}。`
