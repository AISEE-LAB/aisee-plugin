# Service Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

> 如果状态为 N/A，写明原因后即可停止，不需要填写后续表格。
> 本文覆盖 API、后端服务能力、异步任务、定时任务、CLI/工具命令和外部集成。只写服务契约，不写代码实现步骤，不重复 specs 中的业务需求全文。

## 来源与范围

| 来源 | 路径 / 来源 ID | 关联上游 ID | 本 change 用途 | 备注 |
|---|---|---|---|---|
| Specs | specs/... | {{scope}}:SPEC-001 | 用户可观察行为和验收场景 | 只引用，不复制场景全文 |
| UI Contract | ui-contract.md | {{scope}}:PAGE-001 / {{scope}}:FLOW-001 | 前端数据需求、操作触发点、状态反馈 | N/A 时写原因 |
| Data Model | data-model.md | {{scope}}:DATA-001 | 数据读写对象、字段约束、迁移影响 | N/A 时写原因 |
| Change Context | change-context.md | {{scope}}:CONSTRAINT-001 / {{scope}}:RISK-001 | 平台、权限、性能、集成、风险约束 | |
| Existing system / source-map | source-map.md / code / docs | {{scope}}:API-001 | 既有接口、命令、job 或集成事实 | Existing 只引用来源 |

## 服务变更范围

| 状态 | 能力完整 ID | 类型 | 名称 | 来源 | 本 change 处理 | 是否需要实现 |
|---|---|---|---|---|---|---|
| Existing / Changed / New / Deprecated / Unknown | {{scope}}:API-001 | API / backend service / async job / scheduled job / CLI / integration | | source-map / code / docs / specs | 复用 / 修改 / 新增 / 下线 / 待确认 | yes / no |

> Existing 只引用来源，不重写完整契约；Changed / New / Deprecated 必须展开本 change 影响。

## 能力清单

| 能力完整 ID | 类型 | 变更状态 | 能力 | 关联上游 ID | 关联 UI / 数据 | 关联约束 |
|---|---|---|---|---|---|---|
| {{scope}}:API-001 | API / backend service / async job / scheduled job / CLI / integration | New / Changed / Existing / Deprecated | | {{scope}}:FR-001 | {{scope}}:PAGE-001 / {{scope}}:DATA-001 / N/A | {{scope}}:CONSTRAINT-001 / N/A |

## 能力契约

### {{scope}}:API-001 {{能力名}}

- 类型：API / backend service / async job / scheduled job / CLI / integration
- 变更状态：New / Changed / Existing / Deprecated / Unknown
- 不展开原因（Existing 或 N/A 时填写）：

#### 入口

- 方法 / 路径：
- CLI / Job / Integration 入口：
- 触发来源：UI 操作 / 系统事件 / 定时 / 外部回调 / 手工命令 / N/A
- 调用方：
- 被调用方：

#### 请求 / 输入

- 鉴权：
- 权限 / 数据范围：
- 请求参数：
- CLI 参数 / 环境变量：
- Job payload / 消息格式：
- Integration payload：

#### 响应 / 输出

- 响应结构：
- CLI 输出：
- Job 结果：
- Webhook / Integration 回调：

#### 错误与边界

- 错误语义：
- 权限失败：
- 参数校验失败：
- 数据不存在 / 状态冲突：
- 外部依赖失败：
- 幂等 / 并发 / 重试：
- 分页 / 排序 / 过滤：
- 速率限制 / 超时 / 取消：

## 业务规则引用

| 规则 / 场景 ID | 服务能力 ID | 服务侧必须保证的契约 | 备注 |
|---|---|---|---|
| {{scope}}:SPEC-001 / {{scope}}:RULE-001 | {{scope}}:API-001 | 状态流转 / 校验规则 / 数据读写 / 通知 / 失败恢复 | 不复制 specs 全文 |

## 数据读写与事务

| 能力 ID | DATA ID | 操作 | 一致性 / 事务 | 失败处理 | 备注 |
|---|---|---|---|---|---|
| {{scope}}:API-001 | {{scope}}:DATA-001 / N/A | create / read / update / delete / enqueue / publish | 强一致 / 最终一致 / N/A | 回滚 / 补偿 / 重试 / N/A | |

## 可观测性与审计

- 日志：
- 指标：
- 告警：
- 审计记录：
- 隐私 / 脱敏：

## 服务追踪矩阵

| 上游 ID | 能力 ID | PAGE / FLOW | DATA | CONSTRAINT / RISK | 验收场景 | 是否完整 |
|---|---|---|---|---|---|---|
| {{scope}}:FR-001 | {{scope}}:API-001 | {{scope}}:PAGE-001 / N/A | {{scope}}:DATA-001 / N/A | {{scope}}:CONSTRAINT-001 / N/A | specs/... | 是 / 否 |

## 服务验收证据

| 验收项 | 适用能力 | 依据 | 证据要求 | 是否阻塞 |
|---|---|---|---|---|
| 契约完整性 | {{scope}}:API-001 | service-contract.md / specs | 接口测试 / CLI 输出 / job 运行记录 / 人工验证 | yes / no |
| 权限与错误语义 | {{scope}}:API-001 | specs / change-context.md | 测试 / 日志 / 人工验证 | yes / no |
| 数据读写一致性 | {{scope}}:API-001 | data-model.md | 测试 / 数据检查 / 回滚验证 | yes / no |
| 幂等、重试、超时 | {{scope}}:API-001 | change-context.md | 测试 / 运行记录 / N/A | yes / no |
| 可观测性与审计 | {{scope}}:API-001 | change-context.md / 安全约束 | 日志 / 指标 / 审计记录 / N/A | yes / no |
