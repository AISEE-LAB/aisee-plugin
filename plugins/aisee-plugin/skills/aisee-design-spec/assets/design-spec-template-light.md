# aisee:design-spec — 轻量模板

用于功能级、局部模块或只需要约束下游设计/实现的小范围设计规范。

```markdown
---
title: "Design Spec：{功能 / 模块名}"
doc_type: "design-spec"
status: "draft"
date: "{date}"
scope: "{project / module / feature}"
owner: "{作者或团队}"
source_refs:
  - "{SRS / UI Content / Architecture / Design Assets}"
change_refs: []
---

# Design Spec：{功能 / 模块名}

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

## 4. 核心设计规则

| 规则类别 | 规则 | 来源 | 适用范围 |
|---|---|---|---|
| 信息密度 | {rule} | {Source ID} | {pages/platforms} |
| 视觉层级 | {rule} | {Source ID} | {scope} |
| 组件使用 | {rule} | {Source ID} | {scope} |
| 状态反馈 | {rule} | {Source ID} | {scope} |
| 响应式 / 多端 | {rule} | {Source ID} | {scope} |

---

## 5. Do / Don't

| Do | Don't | 原因 | 来源 |
|---|---|---|---|
| {recommended practice} | {forbidden practice} | {reason} | {Source ID} |

---

## 6. 视觉验收规则

| 验收项 | 要求 | 适用页面 / 模式 | 证据 |
|---|---|---|---|
| 截图比对 | {比对重点} | {PAGE/PAT} | 浏览器截图 / 人工走查 / N/A |
| 移动端适配 | {断点、溢出、触控目标、导航折叠} | {platforms} | mobile screenshot / N/A |
| 状态完整性 | {loading / empty / error / disabled / success 等} | {components/patterns} | screenshot / test evidence |

---

## 7. 下游使用提示

- 给 `aisee:design-assets`：{如何基于本规范生成参考图、素材或 visual brief}
- 给 `aisee:change-plan`：{哪些设计约束会影响 change 边界或前置依赖，只写事实和原因}
- 给实现阶段：{实现时应遵循的设计约束，不写代码}

---

## 8. Open Questions

| 编号 | 问题 | 影响范围 | 是否阻塞 change-plan | 建议确认对象 |
|---|---|---|---|---|
| Q-001 | {question or 无} | {scope} | 是/否 | {owner/source} |
```
