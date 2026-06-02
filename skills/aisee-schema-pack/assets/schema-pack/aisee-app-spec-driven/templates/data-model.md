# Data Model: {{change-name}}

状态：适用 / N/A

N/A 原因：

> 如果状态为 N/A，写明原因后即可停止，不需要填写后续表格。
> 本文只描述本 change 涉及的数据结构、字段、关系、索引、迁移、兼容和数据治理约束，不重复 specs 中的业务需求全文，不替代 service-contract.md 的接口契约。

## 来源与范围

| 来源 | 路径 / 来源 ID | 关联上游 ID | 本 change 用途 | 备注 |
|---|---|---|---|---|
| Specs | specs/... | {{scope}}:SPEC-001 | 数据相关行为和验收场景 | 只引用，不复制场景全文 |
| Service Contract | service-contract.md | {{scope}}:API-001 | 数据读写、事务、一致性、错误语义 | N/A 时写原因 |
| Change Context | change-context.md | {{scope}}:CONSTRAINT-001 / {{scope}}:RISK-001 | 数据安全、性能、合规、兼容约束 | |
| Existing system / source-map | source-map.md / code / docs / migration | {{scope}}:DATA-001 | 既有表、字段、索引、迁移事实 | Existing 只引用来源 |

## 数据变更范围

| 状态 | DATA 完整 ID | 对象 | 类型 | 来源 | 本 change 处理 | 是否需要实现 |
|---|---|---|---|---|---|---|
| Existing / Changed / New / Deprecated / Unknown | {{scope}}:DATA-001 | | table / entity / view / cache / event / file / config | source-map / code / docs / migration | 复用 / 修改 / 新增 / 下线 / 待确认 | yes / no |

> Existing 只引用来源，不重写完整数据模型；Changed / New / Deprecated 必须展开本 change 影响。

## 实体与表

| DATA 完整 ID | 表 / 实体 | 类型 | 变更状态 | 用途 | 关联上游 ID | 所有者 |
|---|---|---|---|---|---|---|
| {{scope}}:DATA-001 | | table / entity / view / cache / event / file / config | New / Changed / Existing / Deprecated | | {{scope}}:FR-001 | |

## 字段设计

### {{scope}}:DATA-001 {{table_name}}

- 变更状态：New / Changed / Existing / Deprecated / Unknown
- 不展开原因（Existing 或 N/A 时填写）：

| 字段 | 变更状态 | 类型 | 长度 | 必填 | 默认值 | 约束 | 敏感级别 | 说明 |
|---|---|---|---|---:|---|---|---|---|
| id | Existing / Changed / New / Deprecated | | | 是 | | 主键 | public / internal / sensitive / secret | |

## 关系与约束

- 关系：
- 唯一约束：
- 外键 / 引用：
- 删除 / 归档策略：
- 审计字段：
- 敏感数据处理：
- 数据所有权：
- 数据保留周期：

## 索引与查询

| 索引 | 变更状态 | 字段 | 类型 | 支撑查询 / 服务能力 | 备注 |
|---|---|---|---|---|---|
|  | New / Changed / Existing / Deprecated | | 唯一 / 普通 / 复合 / 全文 | {{scope}}:API-001 / 查询条件 | |

## 迁移、回滚与兼容

- 数据迁移：
- 旧数据兼容：
- 回滚策略：
- 灰度 / 双写 / 回填：
- 零停机要求：
- 版本兼容窗口：
- 失败恢复：

## 数据治理与安全

| 数据对象 / 字段 | 分类 | 处理规则 | 关联约束 | 验收方式 |
|---|---|---|---|---|
| {{scope}}:DATA-001.field | public / internal / sensitive / secret | 脱敏 / 加密 / 最小化 / 审计 / 删除 / N/A | {{scope}}:CONSTRAINT-001 / N/A | 测试 / 代码审查 / 人工验证 |

## 覆盖检查

- [ ] 覆盖相关上游 ID：{{scope}}:FR-001 / {{scope}}:DATA-001 / {{scope}}:CONSTRAINT-001 / N/A。
- [ ] 已引用必要的 service-contract / change-context / N/A。
- [ ] 字段、关系、约束、索引、迁移、回滚和兼容策略已覆盖本 change 影响。
- [ ] 敏感数据、审计、保留周期、删除/归档和数据所有权已处理或写明 N/A。
- [ ] 需要的验证证据已登记到 source-map.md 或 tasks.md。
