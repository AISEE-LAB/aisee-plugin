# Design Spec Rules

本文件承接 `aisee:design-spec` 的设计策略、Design Read、来源映射和界面模式归纳规则。`SKILL.md` 只保留流程入口；生成设计规范前按需读取本文件。

## 设计策略

默认 `auto`，按来源判断设计策略：

| 策略 | 条件 | 输出重点 |
|---|---|---|
| `adopt` | 已有组件库 / 设计系统 / theme，且用户希望遵循现有规范 | 组件库使用规则、token 来源、禁止自定义范围、页面密度和模式约束 |
| `extend` | 使用组件库作为基础，但需要品牌化、业务化或局部重塑 | token 覆盖、业务组件策略、改造边界、典型界面模式 |
| `rewrite` | 新产品、重大 redesign、品牌体系重建，或组件库不适合作为视觉基线 | 设计语言、token、组件原则、界面模式、响应式、a11y、Do/Don't |

不要替用户做不可逆的设计策略决策。证据不足时标注 `[DESIGN-DECISION-REQUIRED]`。

## Design Read

先用一句话写出 Design Read，再展开参数。Design Read 必须来自来源或明确假设，不能是空泛形容词。

格式：

```text
将本产品读作：{产品类型}，面向 {目标受众}，运行在 {平台}，设计语言应偏 {气质}，优先服务 {任务目标}，避免 {默认审美或风险}。
```

## 设计参数

设计参数使用 1-5 档，写明理由和来源：

| 参数 | 含义 |
|---|---|
| `visual_density` | 单屏视觉密度和留白强度 |
| `content_density` | 信息量、字段量、表格/列表密度 |
| `brand_expression` | 品牌表达强度，低=克制工具，高=强品牌视觉 |
| `motion_level` | 动效强度和使用范围 |
| `component_customization` | 组件库定制程度，低=严格采用，高=深度重塑 |

参数不是审美偏好表；它们用于约束组件策略、Screen Patterns、Design Tokens 和视觉验收。

## 设计来源映射

建立来源表，优先沿用 `design-assets` 索引里的 ID；没有 ID 时分配临时 Source ID：

- `DA-xxx`：来自 design-assets 的资产或索引
- `DSRC-xxx`：本次 design-spec 临时来源
- `UIC-xxx` / `PAGE-xxx` / `FLOW-xxx`：来自 UI Content 的页面和流程
- `ARCH-xxx`：来自 Architecture 的技术事实或约束

来源可信度：

- `high`：来自项目文件、组件库配置、theme/token、代码、设计资产索引、用户明确提供的 Logo/截图
- `medium`：来自 SRS、UI Content、Architecture、用户明确说明
- `low`：从参考图风格或上下文推断，必须标注为假设

`design-spec` 可以引用 `design-assets`，但不要复制资产说明、生成参数或素材清单。

## Screen Patterns

从 UI Content 的页面、流程、角色、平台和信息密度中归纳开放式 Screen Patterns，不使用固定页面类型枚举。

每个 Screen Pattern 必须说明：

- 适用页面 / 流程
- 用户任务
- 信息密度
- 内容组织
- 主操作区与次操作区
- 状态反馈
- 响应式变化
- 禁止事项

如果没有 UI Content，只能基于已确认页面/流程或参考材料生成初版，并把缺口写入 Open Questions。
