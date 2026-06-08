# aisee:design-spec — Tokens 与组件策略扩展模板

仅在已有组件库 / theme / design system，或需要明确 token、组件策略、状态规则时读取。

```markdown
## Design Tokens

> 如果 token 来自既有组件库或 theme，写来源和覆盖规则；不要凭空创建品牌色。未确认项写 Open Questions。

### 色彩

| Token | 用途 | 值 / 来源 | 状态 | 备注 |
|---|---|---|---|---|
| color.primary | 主品牌 / 主操作 | {value or Source ID} | 复用 / 覆盖 / 新建 / 待确认 | {note} |
| color.success / warning / danger / info | 状态反馈 | {value or Source ID} | {status} | {note} |

### 字体与文字层级

| Token | 用途 | 值 / 来源 | 状态 | 备注 |
|---|---|---|---|---|
| font.family | 字体族 | {value or Source ID} | {status} | {note} |
| text.heading / body / caption | 标题 / 正文 / 辅助信息 | {rule} | {status} | {note} |

### 间距、圆角、阴影、动效

| 类型 | 规则 | 来源 | 适用范围 |
|---|---|---|---|
| 间距 | {rule} | {Source ID} | {scope} |
| 圆角 | {rule} | {Source ID} | {scope} |
| 阴影 / 边框 | {rule} | {Source ID} | {scope} |
| 动效节奏 | {rule} | {Source ID} | {scope} |

## 组件策略

### 基础组件库 / 设计系统

| 项 | 内容 | 来源 | 状态 |
|---|---|---|---|
| 组件库 | {name/version or 未确认} | {Source ID} | 已确认 / 待确认 |
| 主题来源 | {theme/token path or 未确认} | {Source ID} | 已确认 / 待确认 |
| 使用策略 | 直接采用 / 基于组件库扩展 / 自建 | {Source ID} | 已确认 / 待确认 |

### 组件使用边界

| 组件 / 类别 | 策略 | 适用场景 | 禁止事项 | 来源 |
|---|---|---|---|---|
| Button / Form / Table / Modal / Drawer / Navigation / Card / Toast | 直接使用 / 业务封装 / 自定义 / 禁止魔改 | {scenario} | {don't} | {Source ID} |

### 状态规则

| 状态 | 视觉 / 交互规则 | 适用组件 | 来源 |
|---|---|---|---|
| hover / focus / active / disabled / loading / error / success / warning | {rule} | {components} | {Source ID} |
```
