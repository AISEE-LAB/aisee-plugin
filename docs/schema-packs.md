# Schema Packs

Schema pack 定义 OpenSpec change 内需要生成哪些 artifacts、它们的依赖顺序、模板和 authoring 规则。它不替代 OpenSpec，也不保存项目事实；项目事实仍来自 OpenSpec specs、change artifacts、`source-map.md`、`tasks.md` 和 Aisee registry。

## 目录

源码位置：

```text
plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/
```

安装到项目后的位置：

```text
openspec/schemas/<schema-name>/
```

PyPI / pipx CLI 不再携带 schema pack 副本。Schema pack 内容通过 GitHub-backed Codex marketplace plugin 分发：

```text
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

修改 schema pack 后需要运行：

```bash
python -m pytest tests/test_plugin_marketplace.py tests/test_doctor_flow_schema.py tests/test_schema_pack_examples.py
```

可运行 sample changes 放在对应 schema 的 `examples/` 目录。例如：

```text
plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/examples/add-passwordless-login/
```

这些示例由 GitHub marketplace plugin 直接分发，并由 `tests/test_schema_pack_examples.py` 检查。

## Schema 选择

| Schema | 适用场景 | 说明 |
| --- | --- | --- |
| `aisee-app-spec-driven` | App、小程序、Web、桌面软件、后端/API、CLI、异步任务、常规全栈开发 | 默认软件开发 schema。通过 `source-map.md` 管理 ID 和 artifact 适用性。 |
| `aisee-device-spec-driven` | MCU、RTOS、嵌入式 Linux、IoT、网关、驱动、量产和现场维护 | 硬件和嵌入式专用扩展。当前保留，不作为 app 默认流程。 |
| `aisee-docsite-driven` | 文档站、产品文档、开发者文档 | 用于以文档变更为主要交付物的 change。 |
| `infra-change` | 部署、CI/CD、云资源、网络、运行环境 | 用于需要影响评估和回滚计划的基础设施变更。 |
| `security-audit` | 安全审计、威胁模型、安全修复规划 | 用于审计和安全设计，不替代安全测试报告。 |
| `quick-fix` | 小型、边界清晰、风险低的修复 | 避免为小修复生成过重 artifacts。 |
| `quick-research` | 技术调研、方案比较、建议结论 | 用于研究和决策输入，不直接作为实现任务清单。 |
| `opsx-collab-pr-loop` | 协作、PR loop、外部审查或交接 | 用于协作过程管理，不替代具体业务 schema。 |

推荐规则：

- 新软件功能默认选择 `aisee-app-spec-driven`。
- 小型 bugfix 且不改变公开契约时选择 `quick-fix`。
- 只做技术调研时选择 `quick-research`。
- 文档站作为交付主体时选择 `aisee-docsite-driven`。
- 涉及部署、云资源或回滚时选择 `infra-change`。
- 涉及安全审计或威胁建模时选择 `security-audit`。
- 硬件和嵌入式 change 明确需要时才选择 `aisee-device-spec-driven`。

## App Schema Artifact DAG

`aisee-app-spec-driven` 的最小闭环：

```text
proposal.md
  ↓
source-map.md
  ↓
specs/**/*.md
  ↓
tasks.md
```

按需 artifacts：

```text
source-map.md + specs/**/*.md
  ├─ change-context.md
  ├─ ui-contract.md
  ├─ service-contract.md
  └─ data-model.md
```

这些 artifacts 不是每个 change 都必须完整展开。`source-map.md` 的 Artifact 适用性表必须声明 `Required=yes/no`；`Required=no` 时必须写清楚 N/A 原因。

### Artifact 边界

| Artifact | 写什么 | 不写什么 |
| --- | --- | --- |
| `proposal.md` | 目标、非目标、成功标准、读取顺序 | 接口字段、数据库字段、任务步骤 |
| `source-map.md` | ID 路由、来源、artifact 适用性、候选影响路径、预期证据类型 | 具体实现步骤或最终验证结论 |
| `specs/**/*.md` | 用户可观察行为和验收场景 | UI 布局、API 字段、表字段、代码路径 |
| `change-context.md` | 本 change 承接的架构约束、局部决策和风险 | 全局架构重写 |
| `ui-contract.md` | 页面内容结构、交互状态、权限可见性、前端数据需求 | 完整视觉规范、组件库、配色、像素布局 |
| `service-contract.md` | API、后端能力、CLI/job/integration 契约、provider/consumer、机器可读附件路径 | 脱离 specs/source-map 自造字段 |
| `data-model.md` | 实体、字段、关系、索引、迁移和兼容策略 | 业务需求全文或 API 响应结构 |
| `tasks.md` | 实现任务、验证任务、证据命令或证据路径 | 需求、契约、ID 注册、归档判断 |

## ID 与 Source Map

当前正式模型只使用：

```text
LOCAL-ID
doc-ref#LOCAL-ID
alias#LOCAL-ID
```

AI 不应临时发明 full ID。工具不可用时只能使用临时 local placeholder：

```text
TYPE-NEW-001 [ID-FINALIZATION-REQUIRED]
```

`source-map.md` 负责连接：

- SRS、UI Content、Design Spec / Design Assets、Architecture、Change Plan；
- OpenSpec specs、contracts、tasks；
- API / DATA / TEST / evidence；
- 代码候选影响路径；
- 跨仓库契约来源和同步方式。

## 机器可读契约附件

当 `service-contract.md` 适用时，可以追踪机器可读附件：

```text
contracts/openapi.yaml
contracts/events.yaml
contracts/webhooks.yaml
contracts/proto/*.proto
```

这些附件不是默认必需项。schema 的要求是“能追踪”，不是“每个 change 都生成”。当存在前后端分仓、BFF、SDK 或契约仓库时，应在 `source-map.md` 和 `service-contract.md` 中明确：

- Contract Source；
- Provider；
- Consumer；
- Sync Mode；
- External Repo / Package / Artifact Path；
- Version / Commit / Tag；
- 冲突处理规则。

## 常用命令

列出 schema：

```bash
aisee schemas list --json
```

检查 schema pack：

```bash
aisee schemas check --json --fail-on-blocker
```

`aisee schemas install` 不再从 PyPI wheel 安装 schema packs。需要 schema pack 内容时，通过 marketplace-installed plugin 的 `aisee-schema-pack` 工作流读取并复制插件内 schema。

创建 app change：

```bash
/opsx:new add-login-session --schema aisee-app-spec-driven
```

创建小修复 change：

```bash
/opsx:new fix-login-copy --schema quick-fix
```

## 维护要求

- schema 文件和模板必须同源维护，避免 skill 中复制另一份 schema。
- README 只保留概览，详细规则放在本文档或 `schema.yaml`。
- 修改 schema 后验证 marketplace plugin 中的 schema 内容和示例。
- 公开发布前运行 release smoke test，确认 CLI-only wheel 不包含 schema pack，且 marketplace plugin metadata 可被验证。
