# aisee:change-design — 模板使用规则

本文件不是 `design.md` 模板。

`aisee:change-design` 必须使用当前 OpenSpec schema 提供的官方模板：

```bash
openspec templates --schema <schema> --json
```

然后检查返回 JSON 中是否存在 `design.path`。如果不存在，说明当前 schema 不包含 design artifact，停止并输出 `[DESIGN-ARTIFACT-NOT-APPLICABLE]`，不要创建 `design.md`。

存在 `design.path` 时，读取该路径对应的模板。

默认 `spec-driven` 的模板由 OpenSpec 包提供；custom schema 的模板由项目 `openspec/schemas/<schema>/templates/design.md` 或解析结果指定。

---

## 填充原则

- 保持官方模板的顶层章节、顺序和语义。
- 不要把本文件当作可复制的 `design.md` 模板。
- 不要新增官方模板之外的顶层章节，除非 schema artifact instruction 明确要求。
- 设计细节应折叠到官方模板的相应章节内：
  - 背景、当前状态、约束、上游来源 → `Context`
  - 设计目标和不做事项 → `Goals / Non-Goals`
  - 页面承载、数据流、接口、数据模型、权限、状态机、迁移、回滚、测试策略等关键方案 → `Decisions`
  - 风险、取舍、迁移风险、技术栈缺口、Open Questions → `Risks / Trade-offs` 或 schema instruction 指定章节
- 对默认 `spec-driven`，schema instruction 提到 `Migration Plan` 和 `Open Questions`；如果模板没有这些顶层标题，可以作为 `Risks / Trade-offs` 下的子标题，或按团队 OpenSpec 约定追加，但必须说明来源是 schema instruction。

---

## 内容检查清单

- [ ] 已读取当前 change 的 `.openspec.yaml`
- [ ] 已确认当前 schema 包含 `design.path`；否则已停止并输出 `[DESIGN-ARTIFACT-NOT-APPLICABLE]`
- [ ] 已读取官方 `design.md` 模板
- [ ] design 输出保持官方模板顶层结构
- [ ] 没有新增未确认业务需求
- [ ] 关键设计能追踪到 proposal、SRS、UI 内容规格、技术上下文或现有代码事实
- [ ] 项目级技术栈缺失时标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`
- [ ] 需求缺口标注 `[SPEC-GAP]`
- [ ] 需要修改上游需求或 proposal 时标注 `[SPEC-CHANGE-REQUIRED]`
