# Spec Migration Index 模板

用于生成 `aisee/docs/spec-migration/<YYYY-MM-DD>-<slug>/00-index.md`。

```markdown
# OpenSpec Baseline Migration：{project/module}

**文档编号**：SM-{YYYY-MM-DD}-{slug}
**状态**：草稿 / 已写入 baseline / 待确认
**范围**：{project/module/path}
**创建日期**：{date}

---

## 1. 迁移目标

- 目标：将现有系统当前行为整理为 `openspec/specs/` baseline。
- 不做：新需求、未来规划、代码实现、change delta。

## 2. 扫描证据

| 来源 | 路径 / 描述 | 类型 | 可信度 | 备注 |
|------|-------------|------|--------|------|
| {source} | `{path}` | code/test/doc/api | high/medium/low | {note} |

## 3. 能力地图

| 能力 | 职责 | 不负责 | 主要证据 | 目标 spec |
|------|------|--------|----------|-----------|
| {capability} | {responsibility} | {out of scope} | {evidence} | `openspec/specs/{capability}/spec.md` |

## 4. 目标目录结构

```text
openspec/specs/
├── project.md
└── {capability}/
    └── spec.md
```

## 5. Spec 写入计划

| 批次 | Spec | 状态 | 负责人 | 阻塞项 |
|------|------|------|--------|--------|
| 1 | `openspec/specs/{capability}/spec.md` | draft/ready/written | {owner} | {tags or 无} |

## 6. 行为冲突与缺口

| 编号 | 标记 | 内容 | 证据 | 处理建议 |
|------|------|------|------|----------|
| SM-001 | [EVIDENCE-GAP] / [BEHAVIOR-CONFLICT] / [CURRENT-BEHAVIOR] / [SPEC-OWNER-REQUIRED] | {content} | {source} | {next step} |

## 7. Open Questions

| 编号 | 问题 | 影响 spec | 是否阻塞 |
|------|------|-----------|----------|
| Q-001 | {question or 无} | {spec} | 是/否 |

## 8. 后续工作

- 确认 Open Questions。
- 将 ready specs 写入 `openspec/specs/`。
- 后续新需求使用 OpenSpec change 流程管理。
```

## 写作规则

- 迁移索引可以保留证据路径、可信度和冲突细节。
- 正式 baseline spec 只写行为契约，不写扫描过程。
- 大项目必须分批，不一次性写满全部 spec。
