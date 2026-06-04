# aisee:architecture — Schema Artifact Hints 模板

所有技术域都必须使用。只提示后续契约类型和原因，artifact 名称以 schema pack 为准；不要断言当前 schema 一定存在某个文件。

```markdown
## 13. Schema Artifact Hints

| 技术范围 | 为什么需要后续契约 | 建议 artifact 类型 | 适用 domain / schema | 备注 |
|----------|--------------------|--------------------|----------------------|------|
| {scope} | {reason} | ui-contract / service-contract / data-model / cli-contract / job-contract / integration-contract / security-contract / observability-contract / config-contract / migration-contract / device-collaboration-contract / verification-contract / other | {domain/schema or 待确认} | {note} |
```
