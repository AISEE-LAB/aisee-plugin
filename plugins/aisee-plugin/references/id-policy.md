# ID Policy

本文是 Aisee 当前正式 ID / anchor 规则的维护源。

## 1. 正式模型

Aisee 当前只使用两层标识：

- 文档内 `local ID`
- 跨文档 `anchor ref`

### Local ID

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
```

规则：

- local ID 只在所属文档内要求唯一。
- 文档正文只显示 local ID，不显示 `scope:TYPE-001`。
- 当前轮次无法定稿时，可使用 `TYPE-NEW-001`，并标注 `[ID-FINALIZATION-REQUIRED]`。

### Anchor Ref

```text
<repo-relative-path>#<LOCAL-ID>
<source-kind>:<slug>#<LOCAL-ID>
```

示例：

```text
docs/requirements/auth-srs.md#FR-001
aisee/docs/ui-content/auth-ui.md#PAGE-001
srs:auth-login#FR-001
ui-content:auth-login#PAGE-001
```

规则：

- 跨文档追踪、`source-map.md`、`aisee get`、`aisee trace`、跨项目上下文都使用 anchor ref。
- `path#heading` 这类普通 Markdown 链接不是 Aisee anchor，只有 `#<LOCAL-ID>` 形式才算。
- alias 由 `aisee/registry/sources.json` 提供；alias 只是可读性入口，不是独立事实源。

## 2. 不再使用的旧模型

以下内容不再是正式 authoring 规则：

- `scope:TYPE-001`
- `aisee id reserve`
- `aisee id activate`
- `aisee id deprecate`
- `<!-- aisee:id ... -->`
- 把 `aisee/registry/id-registry.json` 当作需求生命周期事实源

如果仓库里仍出现这些文本，只按历史兼容或诊断处理，不应继续生成新的同类内容。

## 3. 事实源分工

当前分工如下：

- planning docs / OpenSpec artifacts：承载 local ID 与正文事实
- `aisee/registry/sources.json`：承载文档来源注册与 alias
- `aisee index`：构建可重建的 anchor occurrence 索引
- `aisee/cache/context-index.json`：缓存，不是事实源

`aisee/registry/id-registry.json` 如保留，只视为历史兼容路径；当前主链路不依赖它完成 authoring、lookup 或 traceability。

## 4. Authoring 约束

- SRS / UI Content / Architecture / Design / Change artifacts 只写 local ID。
- `source-map.md` 的 Upstream / Trace 表只写 `Ref` / `Refs`，不再写 `ID` 列。
- change 内新增对象如 `SPEC / API / DATA / TASK / TEST`，也只写 local ID。
- 既有 full ID 迁移时，优先改成 `doc-ref#LOCAL-ID`；不要发明新的 full ID。
