# aisee:ui-content — 模板入口

在 Phase 6 先读取本文件，再按场景和输出模式读取对应模板。不要一次性加载所有模板。

---

## 选择顺序

1. 判断场景模式：`new-build` / `enhancement` / `inventory`
2. 判断输出模式：`standard` / `epic`
3. 读取必要模板和写作规则
4. 生成文档前执行质量检查

---

## 模板索引

| 场景 / 文档 | 读取文件 | 使用时机 |
|-------------|----------|----------|
| 标准新建 | `ui-content-template-standard.md` | 新系统或新模块，生成单文件完整 UI 内容规格 |
| 标准二开 | `ui-content-template-enhancement.md` | 现有系统二次开发，生成单文件 UI 增量规格 |
| 标准盘点 | `ui-content-template-inventory.md` | 老项目迁移或现有 UI 盘点，生成单文件 UI 索引 |
| Epic 索引 | `ui-content-template-epic-index.md` | Epic 模式的 `00-index.md` |
| Epic 模块 | `ui-content-template-epic-module.md` | Epic 模式的模块 UI 内容规格 |
| 跨流程 | `ui-content-template-shared-flows.md` | 仅跨模块、跨端、跨角色或长链路流程复杂时生成 |
| 平台差异 | `ui-content-template-platform-diff.md` | 仅多端差异复杂时生成 |
| 写作规则 | `../references/writing-rules.md` | 每次生成 UI 内容规格都必须读取 |

---

## 读取规则

### 标准模式

- `new-build`：读取 `ui-content-template-standard.md` 和 `../references/writing-rules.md`
- `enhancement`：读取 `ui-content-template-enhancement.md` 和 `../references/writing-rules.md`
- `inventory`：读取 `ui-content-template-inventory.md` 和 `../references/writing-rules.md`

### Epic 模式

始终读取：
- `ui-content-template-epic-index.md`
- `ui-content-template-epic-module.md`
- `../references/writing-rules.md`

按需读取：
- 存在跨模块、跨端、跨角色或长链路流程时，读取 `ui-content-template-shared-flows.md`
- 多端差异复杂时，读取 `ui-content-template-platform-diff.md`

---

## 质量检查清单

生成前逐项检查：

- [ ] 没有写视觉设计规范、布局稿、组件库或实现方案
- [ ] 已判断场景模式：new-build / enhancement / inventory
- [ ] 二开场景没有重写未变化的既有 UI，只引用来源并展开差异
- [ ] 盘点场景没有设计新需求，只整理已确认的现有 UI
- [ ] 所有页面都有页面 ID、页面目标、入口、完成后去向、关联 FR 或现有事实来源
- [ ] PAGE / FLOW / STATE 使用 local ID，或已标注 `[ID-FINALIZATION-REQUIRED]`
- [ ] 页面详情内保留了入口来源、返回规则、参与流程和去向规则
- [ ] `shared-flows.md` 只用于跨模块、跨端、跨角色或长链路流程
- [ ] 所有 FR 都能追踪到页面、元素、操作或非页面型系统行为
- [ ] 平台范围已明确，未默认 PC 或移动端
- [ ] 多角色差异已覆盖入口、字段、按钮、数据范围和操作权限
- [ ] 表单字段包含必填、默认值、校验、联动、只读/禁用、提交反馈
- [ ] 危险操作包含确认、取消、成功、失败、恢复规则
- [ ] 状态反馈覆盖加载、空、无结果、错误、无权限、提交中、成功、失败
- [ ] Open Questions 只放未确认事项，不把假设写成事实
- [ ] 标准模式没有超过 8 个页面详情
