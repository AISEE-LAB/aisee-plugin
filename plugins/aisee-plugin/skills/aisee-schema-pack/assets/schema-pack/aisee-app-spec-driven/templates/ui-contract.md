# UI Contract: {{change-name}} / UI Contract Scope

状态：适用 / N/A

N/A 原因：

> 如果状态为 N/A，写明原因后即可停止，不需要填写后续表格。
> 本文只描述页面内容结构、状态、操作、权限可见性、前端数据需求，以及本 change 必须遵循的设计规范引用。不要在这里重新定义或复制完整视觉设计、组件库、配色、排版或像素级布局；这些仍以 Design Spec / Design Assets 为事实源。

## 来源与范围

| 来源 | 路径 / 来源 ID | 关联上游 Ref / Local ID | 本 change 用途 | 备注 |
|---|---|---|---|---|
| UI Content | aisee/docs/ui-content/... | docs/...#PAGE-001 / docs/...#FLOW-001 | 页面内容、字段、操作、状态、权限可见性 | |
| Design Spec | aisee/docs/design-spec/... | PAT-001 / docs/...#PAGE-001 | 组件库策略、tokens、Design Read、响应式、可访问性、验收规则 | 只引用，不复制全文 |
| Design Assets / dev-visual-brief | aisee/docs/design-assets/... | docs/...#PAGE-001 | 参考图、素材路径、视觉验收重点 | 只引用路径和适用约束 |
| Architecture / change-context | change-context.md | CONSTRAINT-001 | 平台、前端边界、性能或技术约束 | |

## UI 变更范围

| 状态 | UI 对象 Local ID | 名称 | 来源 | 本 change 处理 | 是否需要实现 |
|---|---|---|---|---|---|
| Existing / Changed / New / Deprecated / Unknown | PAGE-001 / FLOW-001 / STATE-001 | | UI Content / source-map / code / screenshot | 复用 / 修改 / 新增 / 下线 / 待确认 | yes / no |

> Existing 只引用来源，不重写完整页面规格；Changed / New / Deprecated 必须展开本 change 影响。

## 设计依据与实现约束

| 来源 | 路径 / 来源 ID | 适用页面 | 对实现有约束力的内容 | 验收方式 |
|---|---|---|---|---|
| Design Spec | docs/design/... | PAGE-001 | 组件库 / tokens / 布局规则 / 响应式规则 / 可访问性 / 动效 / N/A | 视觉走查 / 截图对比 / 组件用法检查 / N/A |
| Design Assets | assets/... | PAGE-001 | logo / 图标 / 插图 / 图片 / SVG / 素材状态 / N/A | 资产路径存在 / 渲染检查 / N/A |
| dev-visual-brief | aisee/docs/design-assets/briefs/dev-visual-brief.md | PAGE-001 / section / state | 参考图映射 / extraction confidence / 视觉验收重点 / N/A | 浏览器截图对比 / 人工走查 / N/A |

## 页面清单

| 页面 Local ID | 名称 | 类型 | 变更状态 | 关联 FR / FLOW | 入口 | 完成后去向 |
|---|---|---|---|---|---|---|
| PAGE-001 | | 列表页 / 详情页 / 表单页 / 设置页 / 结果页 / 弹窗 | New / Changed / Existing / Deprecated | docs/...#FR-001 | | |

## 页面内容结构

### PAGE-001 {{页面名}}

- 页面目标：
- 内容区块：
- 字段 / 列表列：
- 操作：
- 权限可见性：
- 完成后去向：
- 设计规范引用：Design Spec / dev-visual-brief / N/A
- 不展开原因（Existing 或 N/A 时填写）：

## 页面状态

| 状态 | 展示内容 | 可用操作 | 恢复 / 跳转 |
|---|---|---|---|
| 加载中 | | | |
| 空状态 | | | |
| 搜索无结果 | | | |
| 错误 | | | |
| 无权限 | | | |
| 提交中 | | | |
| 成功 | | | |
| 失败 | | | |

## 前端数据需求

> 本表只描述前端需要什么数据、由哪个能力提供、当前能力状态如何；不要在这里定义 API 字段、错误码或服务事实源。

| 页面 / 元素 | 需要的数据 | 来源能力 | 后端能力状态 | 状态 / 权限影响 | 关联 ID | 备注 |
|---|---|---|---|---|---|---|
| PAGE-001 | | API-001 / 本地状态 / 配置 | ready / missing / changed / blocked / N/A | loading / empty / error / permission | docs/...#FR-001 | 契约细节见 service-contract.md / N/A |

## 交互与流程

| 流程 Local ID | 起点 | 操作 | 目标 | 携带信息 | 中断恢复 |
|---|---|---|---|---|---|
| FLOW-001 | PAGE-001 | | PAGE-002 / PAGE-003（弹窗） | | |

## 前端状态 ID

| 状态 Local ID | 所属页面 / 流程 | 状态名称 | 触发条件 | 退出条件 |
|---|---|---|---|---|
| STATE-001 | PAGE-001 / FLOW-001 | | | |

## 覆盖检查

- [ ] 覆盖相关上游 Ref / Local ID：docs/...#FR-001 / PAGE-001 / FLOW-001 / N/A。
- [ ] 已引用必要的 Design Spec / Design Assets / dev-visual-brief / N/A。
- [ ] 已引用必要的 service-contract / data-model / N/A。
- [ ] 页面、操作、状态、权限可见性和前端数据需求已覆盖本 change 影响。
- [ ] 当前端依赖后端能力时，已标注后端能力状态，并把 API 事实源交给 service-contract.md / source-map.md。
- [ ] 需要的验证证据已登记到 source-map.md 或 tasks.md。
