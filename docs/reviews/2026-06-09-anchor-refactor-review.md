# Agile Planning Anchor Refactor 审查记录

审查日期：2026-06-09

审查范围：

- `src/aisee_cli/` 中 anchor ref 解析、`get/trace`、`source-map`、`context-pack`、`contract_server` 与 `change checks`
- app schema templates / examples
- app full lifecycle fixture
- `aisee:srs` / `aisee:ui-content` / `aisee:architecture` / `aisee:change-author` / `aisee:change-plan` / `aisee:flow` 相关主链路文案

## 结论

当前主链路已经切到 local ID + anchor ref 模型：

- `aisee get` / `aisee trace` 以 anchor ref 为正式输入；
- `source-map.md` 以 `Ref` / `Refs` 承载跨文档追踪；
- `context-pack`、`author-check`、`change inspect`、`verify/archive checks` 围绕 anchor resolution 工作；
- app schema example、fixture 和关键测试已迁移。

本轮未发现新的实现级 blocker。主要剩余风险是历史架构文档和少量低频模板仍保留旧 full ID 讨论，它们现在更像“历史设计快照”，不应继续作为 authoring 入口。

## 验证

执行：

```bash
pytest -q tests/test_source_map.py tests/test_cli_context_bus.py tests/test_id_registry.py tests/test_context_pack.py tests/test_change_checks.py tests/test_doctor_flow_schema.py tests/test_contract_context.py tests/test_contract_server.py tests/test_lifecycle_dogfood.py tests/test_schema_pack_examples.py
```

结果：

- `75 passed`

## 已处理重点

1. 新增 `anchor_refs.py`，统一 local ID、path anchor、alias anchor 解析。
2. `index/get/trace/source-map/context-pack` 改为 anchor-aware。
3. `aisee id` 生命周期命令从正式 CLI 主路径移除。
4. `contract_server` 改为暴露 anchor-aware 读取入口。
5. app schema `source-map` template、example、fixture 迁移到 `Ref/Refs` 模型。
6. `change-author`、`change-plan`、`srs`、`ui-content`、`architecture` 的高频旧文案已替换。

## 剩余风险

1. `docs/architecture/aisee-cli-context-and-id-registry.md` 与 `docs/architecture/aisee-openspec-compound-integration.md` 仍保留大段旧 full ID 历史设计；已加顶部提示，但尚未整篇重写。
2. 个别低频模板和旧计划文档仍提到 `id-registry.json` 或 `ID-RESERVATION-REQUIRED`；不会影响当前核心测试，但后续应继续清理。
3. 当前审查主要覆盖主链路与 app schema；device-domain 模板与硬件链路只做了有限清理。
