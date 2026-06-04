# aisee:architecture — Software Domain Blocks

用于 app / web / mini-program / desktop / backend-service / cli-tool / job-async / integration / data / hybrid-software 技术域。只保留与当前需求相关的块，不要机械输出全部块。

```markdown
## 12. Domain Context Blocks（按需）

> 每块只写摘要级事实、约束、缺口和后续 artifact 提示；不写具体接口、字段、命令参数或任务契约。

### 12.1 Web / Frontend Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 前端框架 / 路由 / 状态管理 / 组件库技术事实 / theme 来源 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.2 Backend / Service Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 服务边界 / API 风格 / 鉴权 / 权限 / 错误处理 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.3 CLI / Tool Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 命令入口 / 配置来源 / 输出格式 / 退出码 / 分发方式 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.4 Job / Async Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 触发方式 / 调度器 / 队列 / 幂等 / 重试 / 失败处理 / 可观测性 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.5 Integration Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 第三方系统 / 协议 / 鉴权 / 回调 / 限流 / 失败处理 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.6 Data / Migration Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 数据归属 / 迁移机制 / 兼容旧数据 / 回滚 / 报表影响 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.7 Verification / Test Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 单元测试 / E2E / 合约测试 / 集成测试 / 回归测试 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.8 Device Collaboration Context（按需）

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 设备状态 / 数据上报 / 告警 / 上位机协作 / IoT 运行环境 / 可靠性约束 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |
```
