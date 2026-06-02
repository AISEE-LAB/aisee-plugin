# aisee:change-plan — Change Boundary Algorithm

本文件定义 change 边界算法。`aisee:change-plan` 输出的是可独立交付的 OpenSpec change，不是 SRS 模块复制、页面清单复制、架构分层复制或任务列表复制。

## 1. 可独立交付

每个 change 单独合并后，系统必须仍处于可工作状态。

- 只添加数据库表但没有使用它的行为，不算可独立交付。
- 只添加半成品 UI，不算可独立交付。
- 使用 feature flag 可以算可独立交付，但 flag-off 路径必须保持既有行为，且需要在 In Scope 中写明。

检查问题：如果今天只合并这个 change，其他 change 都不合并，系统是否仍能正确工作？

## 2. 单一 Owner

每个 change 应该有一个可以独立做技术决策的 owner。一个 change 同时触及多个业务域或多个 owner 时，优先拆分，除非存在强纵向切片理由。

## 3. 规划策略

### vertical

默认策略。每个 change 交付一个端到端的用户、操作者、系统或设备可观察场景。

避免机械横向切分，例如“全部 DB”“全部 API”“全部 UI”，除非存在共享数据模型、共享事件格式或共享设备协议等强技术前置。

### risk

优先处理最不确定的部分。最高风险 change 可以是 spike 或 PoC，但必须标记：

```text
Title: [SPIKE] 验证 <approach>
In Scope:
  - Prototype implementation to validate feasibility
  - Decision document: go / no-go + recommended approach
Out of Scope:
  - Production-quality code
  - Error handling beyond happy path
```

高风险信号包括：
- 首次集成第三方服务。
- 技术可行性不确定。
- 需要性能基准验证。
- 硬件、固件或设备约束尚未验证。

### parallel

同一 phase 内的 changes 不应共享可变状态，也不应要求多个团队在实现过程中持续协调。

- 如需共享 contract、事件类型、数据模型、设备协议或配置约定，优先规划一个 S 级前置 change。
- 对每个并行 change 复查可独立交付。
- 在依赖图中明确标记并行组。

## 4. 粒度与数量

| 标记 | 估计工作量 | 使用场景 |
|---|---:|---|
| S | 1-3 天 | 单一组件或单一场景，实施路径清晰 |
| M | 3-7 天 | 多组件协作，需要设计决策 |
| L | 7-14 天 | 架构范围较大，或不确定性较高 |

`--granularity` 是约束，不是偏好：

| 粒度 | 输出约束 |
|---|---|
| fine | 优先 S；避免 M；除非明确说明，否则不输出 L |
| medium | 允许 S/M；除非边界天然不可拆，否则避免 L |
| coarse | 允许 S/M/L；不得输出 XL |

规则：
- 默认最多输出 8 个 changes。
- 没有明确提醒 epic planning 时，不得输出超过 8 个 changes。
- 超过 14 天的 XL change 必须继续拆分；无法拆分时标记风险并建议补充 brainstorm 或需求澄清。
- `--single-if-small` 且范围明确小于等于 3 天、单一 owner、无高风险耦合时，只输出一个 change。

## 5. Out of Scope

每个 change 必须有非空 Out of Scope。用于防止实现阶段范围膨胀。

隐含但未说明的事项，放到相关 change 的 Out of Scope，并标注：

```text
需求中未说明，纳入前请确认
```

## 6. 依赖纪律

- 只有当一个 change 必须先合并，另一个 change 才能开始实现时，才标记依赖。
- “设计时需要知道”不等于实现依赖。
- 优先支持并行。
- 不得创建循环依赖。

## 7. Source-map Seed

只有当前 schema 生成 `source-map.md` 时，planned change 才必须包含 source-map seed。具体字段规则见 `source-map-rules.md`。
