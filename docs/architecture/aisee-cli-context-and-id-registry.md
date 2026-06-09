# Aisee CLI、上下文索引与 Anchor 设计

## 维护边界

本文描述 **当前生效** 的 Aisee CLI 设计，不保留旧 full ID / `aisee id` lifecycle 方案作为现行规则。

若与以下事实源冲突，以事实源为准：

- [plugins/aisee-plugin/references/id-policy.md](/Users/fengliang/PycharmProjects/aisee-plugin/plugins/aisee-plugin/references/id-policy.md)
- [plugins/aisee-plugin/references/source-map-contract.md](/Users/fengliang/PycharmProjects/aisee-plugin/plugins/aisee-plugin/references/source-map-contract.md)
- `src/aisee_cli/`
- `tests/`

## 1. 目标

Aisee CLI 不是第二套规范系统。它的目标只有三个：

1. 解析 planning docs、OpenSpec artifacts 和 evidence 中的最小可用上下文。
2. 用 anchor ref 精准定位片段，而不是让 agent 全量扫描仓库。
3. 为 `ce-work`、`verify`、`review`、跨项目只读上下文提供稳定 JSON 入口。

## 2. 当前正式模型

### 2.1 标识模型

当前正式规则：

- 文档内只写 `local ID`，例如 `FR-001`、`PAGE-001`、`DEC-001`
- 跨文档只写 `anchor ref`

```text
docs/requirements/auth-srs.md#FR-001
aisee/docs/ui-content/auth-ui.md#PAGE-001
srs:auth-login#FR-001
```

以下不再是正式模型：

- `scope:TYPE-001`
- `aisee id reserve / activate / deprecate`
- `<!-- aisee:id ... -->`

旧 full ID 若仍出现在历史文档中，只作为兼容诊断文本处理。

### 2.2 事实源分工

| 层 | 作用 | 是否事实源 |
|---|---|---|
| planning docs / OpenSpec artifacts | 承载正文、local ID、anchor 引用；planning docs frontmatter 只承载索引字段 | 是 |
| `aisee/registry/sources.json` | 来源注册与 alias | 是 |
| `aisee index` 输出 | 文档扫描后的 anchor occurrence 视图 | 否，可重建 |
| `aisee/cache/context-index.json` | 缓存 | 否 |
| `docs/reviews/*` / `docs/verification/*` | review / test / manual evidence | 是 |

`aisee/registry/id-registry.json` 现在不是正式 authoring 事实源；如仓库保留该文件，只用于历史兼容。

## 3. 命令职责

### 3.1 `aisee index`

扫描文档并建立：

- document
- local ID occurrence
- anchor ref occurrence
- alias 映射
- 相关代码/测试路径线索

输出面向 machine-readable context，不负责写回规范。

### 3.2 `aisee get <anchor-ref>`

按 anchor ref 返回：

- `reference_type`
- `document`
- `local_id`
- `source`
- `references`
- `relations`
- `issues`

示例：

```bash
aisee get docs/requirements/auth-srs.md#FR-001 --json
aisee get srs:auth-login#FR-001 --json
```

### 3.3 `aisee trace <anchor-ref>`

返回该锚点与：

- change
- 相关页面 / 流程 / 状态
- 代码路径 / 测试路径
- legacy full ID 诊断

的关系视图。

### 3.4 `aisee context pack`

围绕当前 change 生成 schema-aware JSON：

- `facts.parsed`
- `facts.derived`
- `gaps`
- `guardrails`
- `evidence`

它依赖：

- `source-map.md`
- 当前 change artifacts
- `sources.json`
- review / verification evidence

它不把缓存或摘要当事实源。

### 3.5 `aisee contract *`

只读暴露 change contracts 和被允许的上下文片段。

支持：

- `manifest`
- `summary`
- `get`
- `serve`

跨项目消费者必须：

1. 先读 manifest
2. 再按 change / artifact / anchor 获取片段

禁止 provider 暴露全仓库任意读取。

## 4. Source Map 规则

`source-map.md` 是当前 change 的路由中心。

当前正式列语义：

- `Ref` / `Refs`：跨文档 anchor ref
- 本 change 内新产物：local ID
- `Artifact Applicability`：Required yes/no + 原因
- `Implementation Paths`：候选代码 / 测试 / contract 路径
- `Verification Evidence`：预期或已存在证据入口

不再使用：

- `ID` 作为正式跨文档列
- full ID lifecycle 状态

## 5. 诊断与兼容

CLI 仍会报告以下问题，但它们是 **诊断**，不是 authoring 入口：

- `ANCHOR_ALIAS_NOT_FOUND`
- `ANCHOR_DOCUMENT_MISSING`
- `ANCHOR_LOCAL_ID_MISSING`
- `LEGACY_FULL_ID_REFERENCE`
- `SOURCE_MAP_LEGACY_FULL_ID`

设计原则：

- 缺锚点：报 risk / blocker，不静默全文 fallback
- 旧 full ID：报兼容诊断，不继续生成新 full ID

## 6. 与 OpenSpec / CE 的边界

```text
OpenSpec
= schema / change artifacts / validate / archive / baseline specs

Aisee CLI
= anchor-aware context companion

Compound Engineering
= implementation / review / test / commit / PR / reflect
```

Aisee CLI 不负责：

- 修改 OpenSpec baseline
- 替代 `openspec validate`
- 替代 `openspec archive`
- 生成平行任务系统

## 7. 迁移原则

历史仓库从旧模型迁向当前模型时：

1. 文档正文先改为 local ID
2. `source-map.md` 改为 `Ref/Refs`
3. `sources.json` 增加 alias
4. `aisee get/trace` 改用 anchor ref
5. 旧 full ID 仅保留为短期兼容诊断，逐步清除
