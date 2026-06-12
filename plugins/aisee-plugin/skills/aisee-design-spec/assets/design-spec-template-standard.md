# aisee:design-spec — 标准模板

用于项目级、模块级、跨页面、多端或需要完整 design spec / delta planning doc 的场景。

```markdown
---
title: "Design Spec：{项目 / 模块 / 功能名}"
doc_type: "design-spec"
status: "draft"
date: "{date}"
scope: "{project / module / feature}"
owner: "{作者或团队}"
source_refs:
  - "{SRS / UI Content / Architecture / Design Assets}"
change_refs: []
---

# Design Spec：{项目 / 模块 / 功能名}

**文档编号**：DS-{YYYY-MM-DD}-{slug}
**版本**：v1.0
**来源输入**：{SRS / UI Content / Architecture / Design Assets / 用户输入}
**设计策略**：adopt / extend / rewrite

---

## 1. 来源与范围

### 1.1 本文覆盖
- 需求 / 模块：{name}
- 覆盖页面 / 流程：{PAGE/FLOW or 无}
- 覆盖平台：{platforms}
- 用途：为 UI 设计、Design Assets、change-plan 和后续实现提供 design spec / delta planning input

### 1.2 不在范围
- 不生成 SRS 或 UI 内容规格
- 不生成参考图、图片、图标、插画或素材
- 不写具体页面像素稿或 Figma 节点结构
- 不写前端实现方案、CSS、组件 props 或代码文件结构
- 不写 API / 数据库设计

### 1.3 设计来源

| Source ID | 类型 | 路径 / 位置 | 用途 | 可信度 | 备注 |
|---|---|---|---|---|---|
| DA-001 / DSRC-001 / UIC-001 / ARCH-001 | Logo / 参考图 / 截图 / UI Content / Architecture / 组件库 / theme / 用户说明 | {path or description} | {usage} | high / medium / low | {note} |

---

## 2. 设计策略

**策略**：adopt / extend / rewrite

### 2.1 策略依据
- {为什么选择该策略，引用 Source ID}

### 2.2 复用 / 调整 / 重写范围

| 范围 | 决策 | 来源 | 说明 |
|---|---|---|---|
| 组件库 | 复用 / 扩展 / 重写 / 未确认 | {Source ID} | {note} |
| Design Tokens | 复用 / 覆盖 / 新建 / 未确认 | {Source ID} | {note} |
| 界面模式 | 复用 / 调整 / 新建 / 未确认 | {Source ID} | {note} |
| 素材与插画 | 复用 / 新增 / 不需要 / 未确认 | {Source ID} | {note} |

---

## 3. Design Read 与设计参数

### 3.1 Design Read

将本产品读作：{产品类型}，面向 {目标受众}，运行在 {平台}，设计语言应偏 {气质}，优先服务 {任务目标}，避免 {默认审美或风险}。

### 3.2 设计参数

| 参数 | 值（1-5） | 解释 | 来源 |
|---|---:|---|---|
| visual_density | {1-5} | {单屏视觉密度和留白强度} | {Source ID} |
| content_density | {1-5} | {字段、列表、表格和信息量密度} | {Source ID} |
| brand_expression | {1-5} | {品牌视觉表达强度} | {Source ID} |
| motion_level | {1-5} | {动效使用范围和强度} | {Source ID} |
| component_customization | {1-5} | {组件库定制程度} | {Source ID} |

---

## 4. 设计原则

| 原则 | 规则 | 来源 | 适用范围 |
|---|---|---|---|
| 信息密度 | {高 / 中 / 低及原因} | {Source ID} | {pages/platforms} |
| 视觉层级 | {rule} | {Source ID} | {scope} |
| 品牌表达 | {rule} | {Source ID} | {scope} |
| 任务效率 | {rule} | {Source ID} | {scope} |
| 平台一致性 | {rule} | {Source ID} | {scope} |

---

## 5. Design Tokens

> 若 token 或组件策略复杂，读取 `design-spec-template-tokens.md`，用详细章节替换本节和第 6 节；否则在本节写摘要和来源。

| Token 类别 | 规则摘要 | 来源 | 状态 |
|---|---|---|---|
| 色彩 | {rule} | {Source ID} | 复用 / 覆盖 / 新建 / 待确认 |
| 字体与文字层级 | {rule} | {Source ID} | {status} |
| 间距、圆角、阴影、动效 | {rule} | {Source ID} | {status} |

---

## 6. 组件策略

> 若组件策略复杂，读取 `design-spec-template-tokens.md`，用详细章节替换第 5 节和本节。

| 组件 / 类别 | 策略 | 适用场景 | 禁止事项 | 来源 |
|---|---|---|---|---|
| Button / Form / Table / Modal / Drawer / Navigation / Card / Toast | 直接使用 / 业务封装 / 自定义 / 禁止魔改 | {scenario} | {don't} | {Source ID} |

---

## 7. 界面与交互模式

> 若页面/流程复杂，读取 `design-spec-template-patterns.md`，用详细章节替换本节。

| Pattern ID | 模式名称 | 适用页面 / 流程 | 用户任务 | 主要布局原则 | 来源 |
|---|---|---|---|---|---|
| PAT-001 | {pattern name} | PAGE-001, FLOW-001 | {task} | {rule} | {Source ID} |

---

## 8. 响应式、多端与可访问性规则

| 规则类别 | 要求 | 适用范围 | 来源 |
|---|---|---|---|
| 响应式 / 多端 | {rule} | {platforms} | {Source ID} |
| 对比度 | {rule} | {scope} | {Source ID} |
| 键盘访问 / 焦点状态 | {rule} | {scope} | {Source ID} |
| 错误提示 / 状态可感知 | {rule} | {scope} | {Source ID} |

---

## 9. Do / Don't

| Do | Don't | 原因 | 来源 |
|---|---|---|---|
| {recommended practice} | {forbidden practice} | {reason} | {Source ID} |

---

## 10. 视觉验收规则

| 验收项 | 要求 | 适用页面 / 模式 | 证据 |
|---|---|---|---|
| 截图比对 | {与 design-assets / dev-visual-brief / 参考图的比对重点} | {PAGE/PAT} | 浏览器截图 / 人工走查 / N/A |
| 移动端适配 | {断点、溢出、触控目标、导航折叠} | {platforms} | mobile screenshot / N/A |
| 对比度与可访问性 | {文字、按钮、表单、状态色} | {scope} | contrast check / manual |
| 状态完整性 | {loading / empty / error / disabled / success 等} | {components/patterns} | screenshot / test evidence |
| 组件一致性 | {组件库复用、禁止魔改、token 使用} | {components} | code review / visual review |

---

## 11. 追踪关系

| 来源 / 页面 / 组件策略 | 影响的规则 / Pattern | 说明 |
|---|---|---|
| DA-001 / PAGE-001 / strategy | PAT-001 / token / 组件规则 | {note} |

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
|---|---|---|---|---|
| Q-001 | {question or 无} | {scope} | 是/否 | {owner/source} |
```
