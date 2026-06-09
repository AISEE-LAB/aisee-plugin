# Planning Doc Frontmatter Contract

本文定义 Aisee 普通 planning docs 的统一 YAML frontmatter 合同。它只服务文档身份、状态、检索和来源追踪，不提升 planning docs 的事实源级别。

## 适用范围

适用于以下 planning docs：

- SRS
- UI Content
- Architecture
- Design Spec
- Design Assets 索引 / brief
- Implementation Brief
- Reflect

不适用于：

- OpenSpec change artifacts
- OpenSpec baseline specs
- `source-map.md`
- `tasks.md`
- schema contract artifacts

## 最小字段

所有 planning docs frontmatter 至少包含：

```yaml
title: "文档标题"
doc_type: "srs | ui-content | architecture | design-spec | design-assets | implementation-brief | reflect"
status: "draft | active | superseded | archived"
date: "YYYY-MM-DD"
scope: "项目 / 模块 / 功能 / change"
owner: "作者、团队或待填写"
source_refs:
  - "docs/...#FR-001"
change_refs:
  - "openspec/changes/<change>"
anchors:
  - "docs/...#LOCAL-ID"
```

## 字段规则

- `title`：人类可读标题；正文标题可更长，但不要冲突。
- `doc_type`：固定集合，供索引与筛选使用。
- `status`：planning doc 自身状态，不等同于 OpenSpec lifecycle。
- `date`：当前文档版本日期。
- `scope`：文档覆盖范围；允许项目、模块、功能、页面组或 change。
- `owner`：当前维护者、团队或 `待填写`。
- `source_refs`：上游来源，优先使用 repo-relative path 或 anchor ref。
- `change_refs`：已关联的 OpenSpec changes；没有时可为空数组。
- `anchors`：本文档内主要 local IDs 对外暴露的 anchor refs；没有时可为空数组。

## 边界

- frontmatter 不承载需求正文、验收规则、实现约束或 baseline 事实。
- planning docs 的长期规范事实仍由 OpenSpec change 和 baseline specs 持有。
- 旧 `scope:TYPE-001` full ID 不得进入 frontmatter。
- `source_refs`、`change_refs`、`anchors` 应优先使用 anchor ref 或 repo-relative path。
