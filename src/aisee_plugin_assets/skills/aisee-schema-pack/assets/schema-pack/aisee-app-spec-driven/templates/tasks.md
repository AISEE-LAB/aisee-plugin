# Tasks: {{change-name}} / Implementation Checklist

> tasks.md 是实现与验证清单，不承载需求、契约、ID 注册、来源追踪或归档判断。需求写入 specs，约束写入 contract artifacts，追踪写入 source-map.md。

## 执行前确认

- [ ] source-map.md 覆盖范围与 proposal.md 一致。
- [ ] specs 覆盖本 change 的 FR / NFR / RULE。
- [ ] Required=yes 的 change-context / ui-contract / service-contract / data-model 已完成。
- [ ] Required=no 的按需 artifact 已在 source-map.md 写明 N/A 原因。
- [ ] 无阻塞项；保留风险已写入 source-map.md。

## 1. 实现

> 每个实现任务必须引用已有 specs / contract / source-map ID，不重新描述需求、页面、接口或数据模型。

- [ ] {{scope}}:TASK-001 实现 {{scope}}:SPEC-001 对应行为，覆盖 {{scope}}:API-001 / {{scope}}:PAGE-001 / {{scope}}:DATA-001 / N/A。
- [ ] {{scope}}:TASK-002 更新必要代码、配置或文档，覆盖 {{scope}}:CONSTRAINT-001 / N/A。

## 2. 验证

> 每个验证任务必须关联 TEST ID，并记录证据命令或证据路径。

- [ ] {{scope}}:TEST-001 验证 {{scope}}:SPEC-001 验收场景；证据：docs/verification/{{change-name}}-test-results.md / N/A。
- [ ] {{scope}}:TEST-002 验证 Required=yes 的 UI / 服务 / 数据 / 架构约束；证据：截图 / 测试命令 / 人工验证记录 / N/A。
- [ ] {{scope}}:TEST-003 运行相关测试、检查命令或人工验证；证据：命令输出 / 验证报告 / N/A。

## 3. 完成确认

- [ ] 所有实现任务完成。
- [ ] 所有验证任务完成，证据路径或命令已记录。
- [ ] 未处理风险已写入 source-map.md 或对应 artifact。
- [ ] 归档前按 aisee:archive-guard 检查。
