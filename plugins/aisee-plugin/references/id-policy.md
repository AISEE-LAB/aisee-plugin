# Numbering Policy

本文维护 Aisee 编号规则。

## 1. 正式模型

Aisee 当前只把编号作为 skill/template 的写作约束：

```text
<TYPE>-<number>
```

示例：

```text
FR-001
PAGE-001
DEC-001
API-001
SPEC-001
TASK-001
TEST-001
```

规则：

- 编号只在所属文档或当前 change artifact 内要求唯一。
- 文档正文只显示 `FR-001`、`PAGE-001` 这类短编号，不显示 `scope:TYPE-001`。
- 当前轮次无法定稿时，可使用 `TYPE-NEW-001`，并标注 `[NUMBERING-FINALIZATION-REQUIRED]`。
- 跨文档来源在 `source_refs`、`source-map.md` 或 context pack 中以 repo-relative path、外部引用或 `path#编号` 这类 source ref 表达。

## 2. 事实源分工

当前分工如下：

- OpenSpec change artifacts / baseline specs：承载规范事实、任务和归档依据。
- planning docs：承载版本或迭代输入，不是 baseline。
- `source-map.md`：承载当前 change 的来源、适用性、候选路径和 evidence 路由。
- `aisee context pack`：调用时生成的 JSON 视图，不是长期事实源。

## 3. Authoring 约束

- SRS / UI Content / Architecture / Design / Change artifacts 只写文档内编号。
- `source-map.md` 的来源和路由表只写 `Ref` / `Refs` 或编号。
- change 内新增对象如 `SPEC / API / DATA / TASK / TEST`，也只写文档内编号。
- 不要为了满足模板创建无用编号、无用 `source_refs` 或无用 `source-map.md` 行。
