# aisee:srs — Question Bank

Reference file for Phase 2 discovery dialogue. Read this at the start of Phase 2.

---

## Round Progression

```
Round 1: 功能核心       — 建立主流程骨架
Round 2: 数据与状态 + 基线影响 + 边界与集成  — 填充需求边界
Round 3 (standard/deep): 异常与约束 + 非功能  — 补全边界条件
Round 4+ (deep or user raises new topics): 针对性追问
```

For `--depth shallow`: stop after Round 2 and proceed to the Confirmation Gate.

---

## Over-limit Warning (Round 8+)

After Round 8, if the user has not yet confirmed requirements are complete, display:

> ⚠️ **提示**：我们已经进行了 8 轮探讨。建议在下一轮结束后确认需求范围，避免过度发散。如果核心问题还未覆盖，请直接告诉我重点是什么。

---

## Question Bank by Theme

Select questions based on what remains unclear after each user response. Do **not** ask all of them.

### 功能核心（Round 1）

- 用户的核心操作流程是什么？（主流程）
- 有哪些触发条件？（用户主动操作 / 系统事件 / 定时任务）
- 操作完成的判断标准是什么？（Definition of Done）
- MVP 范围是什么？哪些功能是未来迭代的？

### 数据与状态（Round 2）

- 涉及哪些核心数据实体？它们之间的关系是什么？
- 数据有哪些状态？状态之间如何流转？
- 谁拥有数据的读/写权限？

### 现有基线影响（Round 2，baseline-aware 模式使用）

> 只问业务行为和兼容边界，不问接口、数据库或代码实现。

- 这个需求是新增能力，还是修改 / 替换 / 移除现有能力？
- 现有用户流程、角色权限、状态流转或术语中，哪些必须保持兼容？
- 哪些历史行为会被改变？用户可观察到的差异是什么？
- 是否已有 OpenSpec baseline spec、历史 SRS、迁移文档或 active change 需要引用？
- 是否存在旧数据、旧入口、旧链接、旧配置或旧设备行为需要保留一段时间？
- 如果新旧规则冲突，哪个行为是正式目标，哪个需要标记为待确认？

### 边界与集成（Round 2）

- 与哪些外部系统或服务有交互？（第三方 API、消息队列、数据库）
- 是否有认证/授权需求？使用现有机制还是新建？
- 是否有文件上传、导入导出等 I/O 需求？

### 界面入口与任务路径（Round 2/3，仅在页面占比较高的需求中使用）

> 只询问理解功能边界所需的问题，不展开视觉设计或页面布局。

- 用户从哪里进入这个功能？完成后通常去哪里？
- 是否存在必须串联的页面/步骤，还是每个操作可独立完成？
- 哪些页面内容属于业务必须展示，哪些只是后续设计阶段可决定？

### 异常与约束（Round 3）

- 如果操作失败，用户看到什么？系统做什么？
- 有哪些输入校验规则？
- 有性能、并发、数据量方面的已知约束吗？

### 非功能（Round 3）

- 对响应时间有要求吗？
- 需要考虑国际化、无障碍访问吗？
- 有合规、审计日志、数据留存方面的要求吗？

---

## Assumption Handling

If the user gives an incomplete answer and the missing info is not blocking, record an assumption and move forward:

> `[ASSUMPTION] 已假设 {内容} — 影响需求 {FR-xxx} — 请在确认前核实。`

Block progress only when the scope could diverge by more than 30% depending on the answer.
