# Service Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

> 如果状态为 N/A，写明原因后即可停止，不需要填写后续表格。
> 本文覆盖 API、后端服务能力、异步任务、定时任务、CLI/工具命令和外部集成。只写服务契约，不写代码实现步骤。

## 能力清单

| 能力完整 ID | 类型 | 能力 | 关联上游 ID | 关联 UI / 数据 |
|---|---|---|---|---|
| {{scope}}:API-001 | API / backend service / async job / scheduled job / CLI / integration | | {{scope}}:FR-001 | {{scope}}:PAGE-001 / {{scope}}:DATA-001 / N/A |

## 接口契约

### {{scope}}:API-001 {{能力名}}

- 方法 / 路径：
- CLI / Job / Integration 入口：
- 鉴权：
- 权限 / 数据范围：
- 请求参数：
- 响应结构：
- 错误语义：
- 幂等 / 并发 / 重试：
- 分页 / 排序 / 过滤：
- 速率限制 / 超时 / 取消：

## 业务逻辑

- 状态流转：
- 校验规则：
- 数据读写：
- 异步任务 / 通知：
- 外部集成：
- 失败恢复：

## 可观测性与审计

- 日志：
- 指标：
- 告警：
- 审计记录：
- 隐私 / 脱敏：

## 服务追踪矩阵

| 上游 ID | 能力 ID | PAGE / FLOW | DATA | CONSTRAINT / RISK | 验收场景 | 是否完整 |
|---|---|---|---|---|---|
| {{scope}}:FR-001 | {{scope}}:API-001 | {{scope}}:PAGE-001 / N/A | {{scope}}:DATA-001 / N/A | {{scope}}:CONSTRAINT-001 / N/A | specs/... | 是 / 否 |
