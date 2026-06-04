# aisee:design-spec — 模板入口

按规范范围读取最小必要模板，不要一次性加载所有模板。

## 选择规则

| 场景 | 必读模板 | 按需模板 |
|---|---|---|
| 功能级、轻量设计约束、局部 UI 规范 | `design-spec-template-light.md` | `design-spec-template-tokens.md`，仅当涉及 token / 组件策略 |
| 项目级、模块级、跨页面或多端 UI 规范 | `design-spec-template-standard.md` | `design-spec-template-tokens.md`、`design-spec-template-patterns.md` |
| 已有组件库 / theme / design system，需要明确采用或扩展策略 | `design-spec-template-standard.md` | `design-spec-template-tokens.md` |
| UI Content 页面/流程复杂，需要沉淀 Screen Patterns / Interaction Patterns | `design-spec-template-standard.md` | `design-spec-template-patterns.md` |

扩展模板用于替换主模板中的同类摘要章节，不要追加成重复章节。

## 通用质量检查

- [ ] 已判断设计策略：adopt / extend / rewrite
- [ ] 已写 Design Read，并说明产品类型、受众、平台、气质、任务目标和禁用方向
- [ ] 已列出设计来源，并标注来源路径、用途和可信度
- [ ] 没有复制 `design-assets` 的资产说明、生成参数或素材清单
- [ ] 没有写 SRS、UI 内容规格、API、数据库或实现代码
- [ ] 没有写具体页面像素稿或 Figma 节点结构
- [ ] 每条关键设计规则能追踪到来源、用户决策或明确假设
- [ ] Open Questions 只放未确认事项，不把假设写成事实
