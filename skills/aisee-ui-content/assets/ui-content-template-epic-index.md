# Epic 索引模板

用于 Epic 模式的 `00-index.md`。索引只写总览、文档导航、页面总览、流程总览和追踪总表，不展开完整页面详情。

```markdown
# UI 内容规格索引：{功能名}

**文档编号**：UIC-{YYYY-MM-DD}-{slug}-index
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**来源 SRS / 需求**：{path or description}
**场景模式**：{new-build / enhancement / inventory}
**ID Scope**：{scope}

> 正式 PAGE / FLOW / STATE ID 必须来自 `aisee/registry/id-registry.json`。工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 临时占位符，并标注 `[ID-RESERVATION-REQUIRED]`。

---

## 1. 来源与范围

- 覆盖 FR：{{scope}}:FR-001 ~ {{scope}}:FR-00X
- 覆盖模块：{modules}
- 覆盖平台：{platforms}
- 输出模式：Epic
- 本次 UI 工作类型：{新建 / 二开增量 / 现有盘点}

不在范围：
- 视觉设计规范
- 组件库选择
- 前端实现方案
- API / 数据库设计

---

## 2. 现有 UI 事实来源

| 来源类型 | 路径 / 位置 | 可确认内容 | 备注 |
|----------|-------------|------------|------|
| 历史 UI 文档 / OpenSpec baseline / source-map / 路由 / 页面代码 / 截图 | {path or description} | {页面、入口、流程、权限、状态} | {note} |

---

## 3. 文档索引

| 文档 | 路径 | 覆盖范围 | 页面范围 |
|------|------|----------|----------|
| {模块 A} | [`./01-{module-a}.md`](./01-{module-a}.md) | {{scope}}:FR-001 ~ {{scope}}:FR-00X | {{scope}}:PAGE-001 ~ {{scope}}:PAGE-00X |
| 跨模块流程 | [`./shared-flows.md`](./shared-flows.md) | {FRs} | {flows} |
| 平台差异 | [`./platform-diff.md`](./platform-diff.md) | {FRs} | {platforms} |

---

## 4. 受影响 UI 范围

| 状态 | 页面 / 入口 / 流程 | 所属模块 | 当前来源 | 本次变化 | 展开文档 |
|------|-------------------|----------|----------|----------|----------|
| Existing / Changed / New / Deprecated / Unknown | PAGE-001 / NAV-001 / FLOW-001 | {module} | {来源} | {变化摘要或“无变化”} | {doc or 无} |

---

## 5. 平台范围

| 平台 | 是否覆盖 | 用户角色 | 关键能力 / 限制 |
|------|----------|----------|----------------|
| PC Web / Admin | 是/否 | {roles} | {notes} |
| Mobile Web / H5 | 是/否 | {roles} | {notes} |
| Native App | 是/否 | {roles} | {notes} |
| 微信小程序 | 是/否 | {roles} | {notes} |

---

## 6. 页面总览

| 页面 ID | 页面名称 | 变化状态 | 页面类型 | 所属模块 | 关联 FR | 适用平台 | 文档 |
|---------|----------|----------|----------|----------|---------|----------|------|
| {{scope}}:PAGE-001 | {name} | New / Changed / Existing / Deprecated / Unknown | {type} | {module} | {{scope}}:FR-001 | {platforms} | [`./01-{module-a}.md`](./01-{module-a}.md#page-001) |

---

## 7. 流程总览

| 流程 ID | 流程名称 | 起点 | 终点 | 关联 FR | 文档 |
|---------|----------|------|------|---------|------|
| {{scope}}:FLOW-001 | {name} | {{scope}}:PAGE-001 | {{scope}}:PAGE-003 | {{scope}}:FR-001 | [`./shared-flows.md`](./shared-flows.md#flow-001) |

---

## 8. FR 追踪总表

| FR | 覆盖页面 | 覆盖文档 | 是否完整 | 备注 |
|----|----------|----------|----------|------|
| {{scope}}:FR-001 | {{scope}}:PAGE-001, {{scope}}:PAGE-002 | `01-{module-a}.md` | 是/否 | {note} |

---

## 9. 全局待确认事项

| 编号 | 问题 | 影响模块 | 影响页面 | 影响 FR | 影响平台 |
|------|------|----------|----------|---------|----------|
| Q-001 | {question or 无} | {module} | PAGE-xxx | FR-xxx | {platform} |
```
