# ID Policy

本文是 Aisee ID 格式、分配规则和生命周期状态的维护源。

完整 ID 使用：

```text
<scope>:<TYPE>-<number>
```

示例：

```text
auth:FR-001
auth:PAGE-001
payment:FR-001
device-sampling:HW-001
device-sampling:FW-001
```

规则：

- ID 只能由 Aisee CLI 分配。
- `aisee/registry/id-registry.json` 记录 ID 生命周期。
- counters 只增不减。
- 删除过的 ID 不复用。
- 跨文档引用使用完整 ID。
- 人类文档可以显示短 ID，但应保留 `<!-- aisee:id ... -->` 标记。
