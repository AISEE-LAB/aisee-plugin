# Service Contract: {{change-name}} / Service Contract Scope

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

## 契约归属与同步

> 本节必须与 source-map.md 的 `Contract Ownership / Sync` 表保持一致。
> service-contract.md 是面向人和 AI 阅读的服务契约；OpenAPI、events、webhooks、proto 等机器可读文件是可选附件，不默认要求生成。

| 项目 | 值 | 说明 |
|---|---|---|
| Contract Owner | backend / frontend-bff / contract-repo / external-provider / shared / N/A | 权威维护方 |
| Canonical Source | service-contract.md / contracts/openapi.yaml / contracts/events.yaml / contracts/webhooks.yaml / contracts/proto/*.proto / external | 冲突时以此为准 |
| Backend Provider | repo / package / URL / N/A | 服务提供方 |
| Frontend Consumer | repo / app / package / N/A | 服务消费方，可多个 |
| Sync Mode | manual-copy / git-submodule / package / local-http / artifact-export / N/A | 跨仓库同步方式 |
| Conflict Rule | canonical-source-wins / provider-wins / consumer-request-provider-approval / N/A | 冲突解决规则 |
| Version / Commit / Tag | commit / tag / package version / document version / N/A | 当前同步引用 |

## 机器可读契约附件

> 只登记本 change 实际需要追踪的附件。不存在时写 N/A 和原因，不要为了模板完整而生成空文件。

| 类型 | 路径 / 包 / URL | 来源 | 状态 | 关联能力 ID | 备注 |
|---|---|---|---|---|---|
| OpenAPI | contracts/openapi.yaml / N/A | source-map / provider repo / contract repo | existing / changed / new / N/A | {{scope}}:API-001 / N/A | |
| Events | contracts/events.yaml / N/A | source-map / provider repo / contract repo | existing / changed / new / N/A | {{scope}}:API-001 / N/A | |
| Webhooks | contracts/webhooks.yaml / N/A | source-map / provider repo / contract repo | existing / changed / new / N/A | {{scope}}:API-001 / N/A | |
| Proto | contracts/proto/*.proto / N/A | source-map / provider repo / contract repo | existing / changed / new / N/A | {{scope}}:API-001 / N/A | |

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

## 覆盖检查

- [ ] 覆盖相关上游 ID：{{scope}}:FR-001 / {{scope}}:RULE-001 / {{scope}}:API-001 / N/A。
- [ ] 已引用必要的 ui-contract / data-model / change-context / N/A。
- [ ] 契约 owner、canonical source、provider、consumer、sync mode 和 version/ref 已与 source-map.md 对齐，或已写明 N/A 原因。
- [ ] 声明的机器可读契约附件已在 source-map.md 追踪，或已写明 N/A 原因。
- [ ] 请求、响应、命令参数、权限、错误、幂等、分页、排序、过滤、重试和超时已覆盖本 change 影响。
- [ ] 数据读写、事务、一致性和失败处理已与 data-model.md 对齐，或已写明 N/A。
- [ ] 需要的验证证据已登记到 source-map.md 或 tasks.md。
