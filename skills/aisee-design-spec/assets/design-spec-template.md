# aisee:design-spec — 设计规范模板

本模板用于生成项目级或模块级 UI 设计规范。它不是 UI 内容规格、参考图集合或前端实现方案。

---

## 质量检查清单

- [ ] 已判断设计策略：adopt / extend / rewrite
- [ ] 已列出设计来源，并标注来源路径、用途和可信度
- [ ] 没有复制 `design-assets` 的资产说明、生成参数或素材清单
- [ ] 没有写 SRS、UI 内容规格、API、数据库或实现代码
- [ ] 没有写具体页面像素稿或 Figma 节点结构
- [ ] Screen Patterns 来自当前 UI Content / 页面 / 流程，不是固定页面类型枚举
- [ ] 组件策略覆盖直接使用、业务封装、禁止魔改和状态规则
- [ ] 响应式、多端和可访问性规则已覆盖
- [ ] 每条关键设计规则能追踪到来源、用户决策或明确假设
- [ ] Open Questions 只放未确认事项，不把假设写成事实

---

## 文档模板

```markdown
# Design Spec：{项目 / 模块 / 功能名}

**文档编号**：DS-{YYYY-MM-DD}-{slug}
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**来源输入**：{SRS / UI Content / Architecture / Design Assets / 用户输入}
**设计策略**：adopt / extend / rewrite

---

## 1. 来源与范围

### 1.1 本文覆盖
- 需求 / 模块：{name}
- 覆盖页面 / 流程：{PAGE/FLOW or 无}
- 覆盖平台：{platforms}
- 用途：为 UI 设计、Design Assets、change-plan 和后续实现提供设计规范事实源

### 1.2 不在范围
- 不生成 SRS 或 UI 内容规格
- 不生成参考图、图片、图标、插画或素材
- 不写具体页面像素稿或 Figma 节点结构
- 不写前端实现方案、CSS、组件 props 或代码文件结构
- 不写 API / 数据库设计

### 1.3 设计来源

| Source ID | 类型 | 路径 / 位置 | 用途 | 可信度 | 备注 |
|-----------|------|-------------|------|--------|------|
| DA-001 / DSRC-001 / UIC-001 / ARCH-001 | Logo / 参考图 / 截图 / UI Content / Architecture / 组件库 / theme / 用户说明 | {path or description} | {usage} | high / medium / low | {note} |

---

## 2. 设计策略

**策略**：adopt / extend / rewrite

### 2.1 策略依据
- {为什么选择该策略，引用 Source ID}

### 2.2 复用 / 调整 / 重写范围

| 范围 | 决策 | 来源 | 说明 |
|------|------|------|------|
| 组件库 | 复用 / 扩展 / 重写 / 未确认 | {Source ID} | {note} |
| Design Tokens | 复用 / 覆盖 / 新建 / 未确认 | {Source ID} | {note} |
| 界面模式 | 复用 / 调整 / 新建 / 未确认 | {Source ID} | {note} |
| 素材与插画 | 复用 / 新增 / 不需要 / 未确认 | {Source ID} | {note} |

---

## 3. 设计原则

| 原则 | 规则 | 来源 | 适用范围 |
|------|------|------|----------|
| 信息密度 | {高 / 中 / 低及原因} | {Source ID} | {pages/platforms} |
| 视觉层级 | {rule} | {Source ID} | {scope} |
| 品牌表达 | {rule} | {Source ID} | {scope} |
| 任务效率 | {rule} | {Source ID} | {scope} |
| 平台一致性 | {rule} | {Source ID} | {scope} |

---

## 4. Design Tokens

> 如果 token 来自既有组件库或 theme，写来源和覆盖规则；不要凭空创建品牌色。未确认项写 Open Questions。

### 4.1 色彩

| Token | 用途 | 值 / 来源 | 状态 | 备注 |
|-------|------|-----------|------|------|
| color.primary | 主品牌 / 主操作 | {value or Source ID} | 复用 / 覆盖 / 新建 / 待确认 | {note} |
| color.success / warning / danger / info | 状态反馈 | {value or Source ID} | {status} | {note} |

### 4.2 字体与文字层级

| Token | 用途 | 值 / 来源 | 状态 | 备注 |
|-------|------|-----------|------|------|
| font.family | 字体族 | {value or Source ID} | {status} | {note} |
| text.heading / body / caption | 标题 / 正文 / 辅助信息 | {rule} | {status} | {note} |

### 4.3 间距、圆角、阴影、动效

| 类型 | 规则 | 来源 | 适用范围 |
|------|------|------|----------|
| 间距 | {rule} | {Source ID} | {scope} |
| 圆角 | {rule} | {Source ID} | {scope} |
| 阴影 / 边框 | {rule} | {Source ID} | {scope} |
| 动效节奏 | {rule} | {Source ID} | {scope} |

---

## 5. 组件策略

### 5.1 基础组件库 / 设计系统

| 项 | 内容 | 来源 | 状态 |
|----|------|------|------|
| 组件库 | {name/version or 未确认} | {Source ID} | 已确认 / 待确认 |
| 主题来源 | {theme/token path or 未确认} | {Source ID} | 已确认 / 待确认 |
| 使用策略 | 直接采用 / 基于组件库扩展 / 自建 | {Source ID} | 已确认 / 待确认 |

### 5.2 组件使用边界

| 组件 / 类别 | 策略 | 适用场景 | 禁止事项 | 来源 |
|-------------|------|----------|----------|------|
| Button / Form / Table / Modal / Drawer / Navigation / Card / Toast | 直接使用 / 业务封装 / 自定义 / 禁止魔改 | {scenario} | {don't} | {Source ID} |

### 5.3 状态规则

| 状态 | 视觉 / 交互规则 | 适用组件 | 来源 |
|------|-----------------|----------|------|
| hover / focus / active / disabled / loading / error / success / warning | {rule} | {components} | {Source ID} |

---

## 6. 界面模式 / Screen Patterns

> 不预设固定页面类型。根据 UI Content 的页面、流程、角色、平台和信息密度归纳本项目需要的界面模式。

### 6.1 模式总览

| Pattern ID | 模式名称 | 适用页面 / 流程 | 用户任务 | 信息密度 | 主要布局原则 |
|------------|----------|-----------------|----------|----------|--------------|
| PAT-001 | {pattern name} | PAGE-001, FLOW-001 | {task} | 高 / 中 / 低 | {rule} |

### 6.2 模式规则

#### PAT-001 {模式名称}

- 适用场景：{scenario}
- 内容组织：{rule}
- 主操作区：{rule}
- 次要操作区：{rule}
- 状态反馈：{rule}
- 响应式变化：{rule}
- 禁止事项：{don't}
- 来源：{Source ID}

---

## 7. 交互模式 / Interaction Patterns

| 模式 | 规则 | 适用范围 | 禁止事项 | 来源 |
|------|------|----------|----------|------|
| 导航 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 表单 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 列表 / 表格 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 搜索筛选 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 弹窗 / 抽屉 / 浮层 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 危险操作 | {rule} | {pages/platforms} | {don't} | {Source ID} |
| 加载 / 空 / 错误 / 无权限状态 | {rule} | {pages/platforms} | {don't} | {Source ID} |

---

## 8. 响应式与多端规则

| 平台 / 断点 | 信息组织 | 操作迁移 | 导航规则 | 能力限制 | 来源 |
|-------------|----------|----------|----------|----------|------|
| PC Web / Admin | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| H5 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| App | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| 微信小程序 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |
| 桌面端 | {rule} | {rule} | {rule} | {limit or 无} | {Source ID} |

---

## 9. 可访问性规则

| 规则 | 要求 | 适用范围 | 来源 |
|------|------|----------|------|
| 对比度 | {rule} | {scope} | {Source ID} |
| 键盘访问 | {rule} | {scope} | {Source ID} |
| 焦点状态 | {rule} | {scope} | {Source ID} |
| 状态可感知 | {rule} | {scope} | {Source ID} |
| 错误提示 | {rule} | {scope} | {Source ID} |

---

## 10. Do / Don't

| Do | Don't | 原因 | 来源 |
|----|-------|------|------|
| {recommended practice} | {forbidden practice} | {reason} | {Source ID} |

---

## 11. 追踪关系

### 11.1 来源到规则

| Source ID | 影响的设计规则 | 说明 |
|-----------|----------------|------|
| DA-001 | 色彩 / 品牌表达 / token | {note} |

### 11.2 UI Content 到 Screen Pattern

| 页面 / 流程 | Pattern ID | 说明 |
|-------------|------------|------|
| PAGE-001 / FLOW-001 | PAT-001 | {note} |

### 11.3 组件策略到页面

| 组件策略 | 影响页面 / 模式 | 说明 |
|----------|-----------------|------|
| {strategy} | PAGE-001 / PAT-001 | {note} |

---

## 12. 给下游的使用提示

### 12.1 给 aisee:design-assets
- {如何基于本规范生成参考图、素材或 visual brief}

### 12.2 给 aisee:change-plan
- {哪些设计约束会影响 change 边界或前置依赖，只写事实和原因}

### 12.3 给实现阶段
- {实现时应遵循的设计约束，不写代码}

---

## 13. Open Questions

| 编号 | 问题 | 影响范围 | 是否阻塞 change-plan | 建议确认对象 |
|------|------|----------|----------------------|--------------|
| Q-001 | {question or 无} | {scope} | 是/否 | {owner/source} |
```
