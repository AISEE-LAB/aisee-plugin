# Change Context: {{change-name}} / Architecture Handoff

状态：适用 / N/A

N/A 原因：

> 如果状态为 N/A，写明原因后即可停止，不需要填写后续内容。
> 本文是 Architecture 到本 change 的轻量交接，只记录实现本 change 必须知道的架构约束、局部决策、风险和转交事项。不重写全局 Architecture，不写页面、接口、表字段或实现步骤。

## 来源与范围

- Architecture 来源：aisee/docs/architecture/... / N/A
- 关联上游 ID：{{scope}}:ARCH-001 / {{scope}}:DEC-001 / {{scope}}:CONSTRAINT-001 / {{scope}}:RISK-001 / N/A
- 本 change 适用原因：
- 不在本文重复的内容：全局技术栈 / 完整模块架构 / 页面内容 / 接口字段 / 数据表字段 / 实现任务

## 承接的架构约束

- {{scope}}:CONSTRAINT-001：
  - 对本 change 的影响：
  - 必须遵守：
  - 不适用或允许偏差：

## 本 Change 局部决策

- {{scope}}:DEC-NEW-001 [ID-RESERVATION-REQUIRED]：
  - 决策：
  - 依据：
  - 影响：
  - 是否需要回写 Architecture：是 / 否

## 风险与阻塞

- {{scope}}:RISK-001：
  - 影响：
  - 处理方式：规避 / 接受 / 待确认
  - 状态：Open / Accepted / Closed

## 转交事项

- ui-contract.md：
  - {{scope}}:CONSTRAINT-001 / N/A：
- service-contract.md：
  - {{scope}}:CONSTRAINT-001 / N/A：
- data-model.md：
  - {{scope}}:CONSTRAINT-001 / N/A：
- tasks.md：
  - {{scope}}:CONSTRAINT-001 / {{scope}}:RISK-001 / N/A：

## 禁止假设

- 不得发明 Architecture 中未确认的技术栈、服务边界、数据归属或集成方式。
- 存在 `[ARCHITECTURE-DECISION-REQUIRED]`、`[STACK-DECISION-REQUIRED]` 或 `[STACK-CONFLICT]` 时，不得把待确认项写成已确认结论。
