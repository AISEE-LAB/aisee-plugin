# aisee:srs — Epic Module Document Template

Use this template for each module document in Epic mode.

```markdown
# {模块名称} — 需求详情文档

**所属主文档**：[`./00-main.md`](./00-main.md)
**文档编号**：SRS-{YYYY-MM-DD}-{slug}-{module-slug}
**版本**：v1.0
**状态**：草稿
**创建日期**：{date}
**FR 范围**：FR-{XXX} ~ FR-{YYY}

---

## 模块概述

{1–2 句话说明本模块的职责范围，以及与其他模块的关系。}

---

## 3. 功能需求

> 每条需求使用唯一 ID（FR-001、FR-002…），与主文档 Section 7 对应。

### 3.{N} {功能模块名称}

#### FR-{XXX} {需求标题}

**描述**：{一句话说明该需求交付什么}

**前置条件**：{触发该功能前系统或用户需满足的条件}

**主流程**：
1. {step 1}
2. {step 2}
3. {step 3}

**异常流程**：
- {exception 1} -> {system response}
- {exception 2} -> {system response}

**验收标准**：
- [ ] {criterion 1}
- [ ] {criterion 2}

**业务规则 / 约束**：
- {rule 1}
- {rule 2}

**优先级**：P0 / P1 / P2
**变更类型**：新增 / 修改 / 移除 / 兼容
**影响基线**：{openspec/specs/... or docs/... or "无"}
**依赖**：{FR-xxx 或 "无"}

{根据场景类型追加对应扩展块，无匹配场景则删除此行}

---

## 4. 本模块非功能补充

> 只记录本模块特有的性能、安全、可靠性、可维护性要求；全局非功能要求见主文档 Section 4。无模块级补充时填"无"。

- {requirement or "无"}

---

## 5. 本模块相关假设

> 以下假设已在主文档 Section 5.2 完整记录，此处仅列编号和摘要供快速参考。

| 编号 | 假设摘要 | 确认状态 |
|------|----------|----------|
| A-001 | {brief summary} | 待确认 |

---

## 6. 本模块待确认事项（Open Questions）

| 编号 | 问题 | 影响需求 | 负责人 | 截止日期 |
|------|------|----------|--------|----------|
| Q-001 | {question} | {FR-xxx} | 待指定 | 待定 |

---

## 7. 模块变更候选清单

> 以下功能需求按优先级和依赖关系排列，可作为 `aisee:change-plan` 的输入。只列出本模块范围内的 FR。

| 优先级 | 需求 ID | 标题 | 变更类型 | 影响基线 | 估计规模 | 依赖 |
|--------|---------|------|----------|----------|----------|------|
| P0 | FR-{XXX} | {title} | 新增 / 修改 / 移除 / 兼容 | {baseline ref or 无} | M | 无 |
| P1 | FR-{YYY} | {title} | 修改 | {openspec/specs/...} | S | FR-{XXX} |

---

## 8. 本模块后续交接提示

| 后续环节 | 建议 | 原因 / 关注点 |
|----------|------|---------------|
| UI Content | 需要 / 不需要 | {页面、窗口、状态、权限、多端差异等} |
| Tech Context | 需要 / 不需要 | {既有系统、技术栈、外部系统、异步任务、数据迁移等} |
| Change Plan | 注意事项 | {建议边界、不可拆散的流程、关键依赖、Open Questions} |

**下一步**：将本文档路径传入 `aisee:change-plan`，进行 Change 边界规划：

\`\`\`
aisee:change-plan docs/requirements/{slug}/{module-file}.md
\`\`\`
```
