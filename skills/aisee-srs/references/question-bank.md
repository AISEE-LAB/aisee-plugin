# aisee:srs — Question Bank

Reference file for Phase 2 discovery dialogue. Read this at the start of Phase 2.

---

## Round Progression

```
Round 1: 业务目标与用户       — 建立问题、用户、成功标准和范围边界
Round 2: 核心能力与业务流程   — 建立主流程、MVP、非目标和验收方向
Round 3: 业务对象、规则、权限 — 填充数据概念、状态、权限和业务规则
Round 4 (standard/deep): 异常、约束、基线影响、外部协作 — 补全边界条件
Round 4+ (deep or user raises new topics): 针对性追问
```

For `--depth shallow`: stop after Round 2 and proceed to the Confirmation Gate, but only if scope, core users, main flow, MVP, non-goals, and acceptance direction are clear enough for a draft SRS.

---

## Over-limit Warning (Round 8+)

After Round 8, if the user has not yet confirmed requirements are complete, display:

> ⚠️ **提示**：我们已经进行了 8 轮探讨。建议在下一轮结束后确认需求范围，避免过度发散。如果核心问题还未覆盖，请直接告诉我重点是什么。

---

## Question Bank by Theme

Select questions based on what remains unclear after each user response. Do **not** ask all of them.

### 业务目标与用户（Round 1）

- 这个需求要解决的核心业务问题是什么？为什么现在要做？
- 目标用户 / 角色是谁？他们各自的核心诉求是什么？
- 业务成功的判断标准是什么？上线后怎样算“解决了问题”？
- 这是全新能力，还是替换、增强、兼容或移除现有能力？
- 需求属于哪个业务范围？明确不覆盖哪些范围？

### 核心能力与业务流程（Round 2）

- 用户的核心操作流程是什么？（主流程）
- 有哪些触发条件？（用户主动操作 / 系统事件 / 定时任务）
- 操作完成的判断标准是什么？（Definition of Done）
- MVP 范围是什么？哪些功能是未来迭代的？
- 对每个核心能力，用户输入是什么、系统产出什么、失败时用户期望什么？
- 哪些能力必须同一期交付，哪些可以拆到后续 change？

### 业务对象与状态（Round 3）

- 涉及哪些核心数据实体？它们之间的关系是什么？
- 数据有哪些状态？状态之间如何流转？
- 哪些状态变化会影响用户可见行为、通知、权限或后续操作？
- 哪些业务对象需要保留历史、审计、归档或撤销？

### 业务规则与权限（Round 3）

- 有哪些必须遵守的业务规则、频率限制、唯一性规则或金额/数量限制？
- 谁可以查看、创建、编辑、删除、审批或导出数据？
- 权限是按角色、组织、数据归属、状态，还是其他规则决定？
- 无权限、超出范围或规则冲突时，用户应看到什么结果？

### 现有基线影响（Round 4，baseline-aware 模式使用）

> 只问业务行为和兼容边界，不问接口、数据库或代码实现。

- 这个需求是新增能力，还是修改 / 替换 / 移除现有能力？
- 现有用户流程、角色权限、状态流转或术语中，哪些必须保持兼容？
- 哪些历史行为会被改变？用户可观察到的差异是什么？
- 是否已有 OpenSpec baseline spec、历史 SRS、迁移文档或 active change 需要引用？
- 是否存在旧数据、旧入口、旧链接、旧配置或旧设备行为需要保留一段时间？
- 如果新旧规则冲突，哪个行为是正式目标，哪个需要标记为待确认？

### 边界与集成（Round 4）

- 与哪些外部系统或服务有业务交互？交互目的是什么？
- 是否有认证/授权需求？使用现有机制还是新建？
- 是否有文件上传、导入导出等 I/O 需求？
- 外部协作失败、超时、重复提交、部分成功时，业务上应该如何处理？

### 界面入口与任务路径（Round 3/4，仅在页面占比较高的需求中使用）

> 只询问理解功能边界所需的问题，不展开视觉设计或页面布局。

- 用户从哪里进入这个功能？完成后通常去哪里？
- 是否存在必须串联的页面/步骤，还是每个操作可独立完成？
- 哪些页面内容属于业务必须展示，哪些只是后续设计阶段可决定？

### 异常与约束（Round 3）

- 如果操作失败，用户看到什么？系统做什么？
- 有哪些输入校验规则？
- 有性能、并发、数据量方面的已知约束吗？
- 有哪些业务边界 case：重复提交、过期、撤销、取消、冲突、部分成功、长时间处理中？

### 非功能（Round 3）

- 对响应时间有要求吗？
- 需要考虑国际化、无障碍访问吗？
- 有合规、审计日志、数据留存方面的要求吗？

### 后续交接判断（确认门禁前使用）

- 这个需求是否需要 UI Content？如果需要，是因为多页面、多端、复杂交互、权限可见性，还是状态反馈复杂？
- 这个需求是否需要 Tech Context？如果需要，是因为既有系统改造、技术栈未明确、复用能力未知、外部系统、异步任务、数据迁移或权限复杂？
- 传给 `aisee:change-plan` 时，哪些 FR 可能必须放在同一 change，哪些可以独立拆分？
- 哪些问题必须在 change authoring 前确认，哪些可以作为 Open Questions 进入后续阶段？

---

## Assumption Handling

If the user gives an incomplete answer and the missing info is not blocking, record an assumption and move forward:

> `[ASSUMPTION] 已假设 {内容} — 影响需求 {FR-xxx} — 请在确认前核实。`

Block progress only when the scope could diverge by more than 30% depending on the answer.
