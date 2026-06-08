# aisee:design-spec — Patterns 扩展模板

仅在 UI Content 页面/流程复杂、跨端差异明显，或需要沉淀 Screen Patterns / Interaction Patterns 时读取。

```markdown
## 界面模式 / Screen Patterns

> 不预设固定页面类型。根据 UI Content 的页面、流程、角色、平台和信息密度归纳本项目需要的界面模式。

### 模式总览

| Pattern ID | 模式名称 | 适用页面 / 流程 | 用户任务 | 信息密度 | 主要布局原则 |
|---|---|---|---|---|---|
| PAT-001 | {pattern name} | PAGE-001, FLOW-001 | {task} | 高 / 中 / 低 | {rule} |

### 模式规则

#### PAT-001 {模式名称}

- 适用场景：{scenario}
- 内容组织：{rule}
- 主操作区：{rule}
- 次要操作区：{rule}
- 状态反馈：{rule}
- 响应式变化：{rule}
- 禁止事项：{don't}
- 来源：{Source ID}

## 交互模式 / Interaction Patterns

| 模式 | 规则 | 适用范围 | 禁止事项 | 来源 |
|---|---|---|---|---|
| 导航 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 表单 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 列表 / 表格 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 搜索筛选 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 弹窗 / 抽屉 / 浮层 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 危险操作 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 加载 / 空 / 错误 / 无权限状态 | {rule} | {pages/platforms} | {don't} | {Source ID} |

## 响应式与多端规则

| 平台 / 断点 | 信息组织 | 操作迁移 | 导航规则 | 能力限制 | 来源 |
|---|---|---|---|---|---|
| PC Web / Admin | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| H5 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| App | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| 微信小程序 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| 桌面端 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |

## Pattern 追踪关系

| 页面 / 流程 | Pattern ID | 说明 |
|---|---|---|
| PAGE-001 / FLOW-001 | PAT-001 | {note} |
```
