# aisee:srs — Writing Rules

Read this file before generating any SRS document.

## Requirement Quality Checklist

Apply to each FR before writing it:

- [ ] Describes what the system does, not how (no implementation decisions)
- [ ] Testable: a QA engineer can write a test case from it
- [ ] No framework choices, API endpoint names, or DB schema details
- [ ] Priority is assigned (P0 / P1 / P2)
- [ ] Dependencies on other FRs are explicit
- [ ] Contains enough business context to support UI Content, Architecture, and Change Plan handoff
- [ ] Scenario extension appended when relevant

Fix silently if a requirement fails these checks. Do not stop to ask unless the missing information can change scope or correctness.

## FR 写作规则：基础块 + 场景扩展块

每条 FR 由两部分组成：

1. 基础块：描述、前置条件、主流程、异常流程、验收标准、业务规则 / 约束。
2. 场景扩展块：根据 FR 所属场景，从 `scenario-extension-blocks.md` 中选取对应模板追加在基础块之后。

场景识别方式：阅读 FR 描述，匹配下表中的识别信号，一个 FR 可能匹配多个场景类型。

| 场景类型 | 识别信号 |
|---|---|
| 表单/新建编辑页 | 关键词：新增、编辑、填写、提交、创建、修改 |
| 列表/查询页 | 关键词：查看列表、搜索、筛选、分页、导出 |
| 详情页 | 关键词：查看详情、详情页、信息展示 |
| 外部系统协作 | 关键词：对接、集成、调用第三方、同步、推送、Webhook、外部审批 |
| 数据导入/导出 | 关键词：导入、导出、上传文件、下载、批量 |
| 通知/消息 | 关键词：通知、提醒、消息、邮件、短信、推送 |
| 权限/角色 | 关键词：权限、角色、访问控制、可见范围 |
| 工作流/审批 | 关键词：审批、流程、状态流转、待办、驳回 |

## Section Writing Notes

### Section 3：场景扩展块使用原则

- 每条 FR 至少检查一次场景匹配，确保不遗漏扩展块。
- 一条 FR 可以追加多个扩展块，例如带权限控制的列表页 = 扩展块 B + 扩展块 G。
- 信息缺失时不要写“待定”为事实，放入 Section 6 Open Questions 并注明影响的 FR。
- 扩展块中的枚举选项应使用实际值，不保留括号内的选项列表。
- 扩展块只记录功能性 UI / 业务合约：字段、列、筛选、操作、状态、校验、权限、反馈。不要写视觉布局、组件库、颜色、图标或具体排版。
- 如果需要进一步说明页面清单、页面内容、页面元素和跨页面交互流程，在 SRS 之后生成独立 UI Content，不要塞进 FR 正文。

### Section 5.2：假设

- 每个对话中记录的 `[ASSUMPTION]` 必须出现在主文档或标准文档的这里。
- Epic 模式下，模块文档中的假设仅作引用，完整内容以主文档为准。
- 不因“显而易见”而省略假设条目。

### Section 2.5：现有基线影响

- 仅在 baseline-aware 模式下填写；没有可识别基线时写“未发现可信基线来源”，不要猜。
- 只记录用户可观察业务行为、角色权限、状态、流程、入口、兼容要求的影响。
- 不写 API endpoint、数据库表字段、ORM、代码模块、迁移脚本或实现方案。
- 每条受影响 FR 必须在 FR 正文和 Section 7 中标注“变更类型”和“影响基线”。
- 影响基线来源优先级：`openspec/specs/` > active change artifacts > `docs/spec-migration/` > 历史 SRS > 用户明确说明 > 从代码推断（低可信，必须标注）。

### Section 6：Open Questions

- 对话中提及但未解决的事项放这里，不放进 FR 正文。
- 用户未提及但实现时必须明确的事项也放这里，注明：`(未在需求中提及 — 实施前请确认)`。

### Section 7：变更候选清单

- 规模估算是粗估，`aisee:change-plan` 会细化。
- 依赖关系与 FR 正文中的“依赖”字段保持一致。
- Epic 模式下，主文档 Section 7 中的 FR ID 必须附相对路径链接指向对应模块文档。
- baseline-aware 模式下，必须包含“变更类型”和“影响基线”列，便于 `aisee:change-plan` 生成 source-map seed。
