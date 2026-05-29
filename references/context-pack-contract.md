# Context Pack Contract

`aisee context pack` 默认调用时直接解析，不维护第二份内容事实源。

事实源：

- Markdown / OpenSpec artifacts：内容事实源。
- `.aisee/id-registry.json`：ID 分配和生命周期事实源。
- `.aisee/sources.json`：change 外部 Aisee 产物来源登记事实源。
- `.aisee/cache/context-index.json`：可删除、可重建缓存，不是事实源。

默认输出只包含：

- `parsed`：从模板化 Markdown / OpenSpec artifacts 直接解析。
- `derived`：根据 source-map、ID registry、文件关系和校验规则推导。

AI 生成摘要必须显式启用，并在 JSON 中标记为 `generated`。
