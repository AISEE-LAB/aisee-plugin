# aisee:change-plan — Schema Selection Rules

默认使用 `--schema auto`。不要把所有任务都套到 `aisee-app-spec-driven`。

## 选择规则

| 工作类型 | 推荐 schema | 使用条件 |
|---|---|---|
| App / Web / backend / CLI / job 功能迭代 | `aisee-app-spec-driven` | 需要稳定追踪 SRS / UI Content / Design Spec / Architecture，或需要把前置文档压缩成实现契约 |
| 小 bugfix / hotfix | `quick-fix` | 单一问题、根因或复现路径明确、预计小于等于 1 天、不新增业务能力、不需要新 UI/API/DATA 契约 |
| 文案 / 样式 / 静态配置小改 | `quick-fix` | 用户可见影响小，可用简单验证证明 |
| 技术调研 / 可行性验证 | `quick-research` | 目标是回答问题或做 go/no-go，不承诺生产实现 |
| 外部 PR review / 多轮协作调研 | `opsx-collab-pr-loop` | 输入来自 PR、issue 或外部材料，可能需要多轮 review/checkpoint |
| 文档站 / 知识库维护 | `aisee-docsite-driven` | 改的是内容、导航、信息架构或文档站配置 |
| 基础设施 / 部署 / CI | `infra-change` | 改的是环境、部署、云资源、流水线、网络或回滚风险 |
| 安全敏感变更 | `security-audit` | 涉及认证、授权、隐私、加密、输入攻击面或安全审计 |
| 设备 / 固件 / 嵌入式 / 驱动 / 板级 | `aisee-device-spec-driven` | Linux 设备程序、RTOS、bare-metal、MCU、SoC、板级 bring-up 或硬件相关 change |
| 普通 OpenSpec change | `spec-driven` | 不需要 Aisee 规划链追踪，且项目未安装更合适轻量 schema |

## App Schema v2

`aisee-app-spec-driven` 的最小闭环：

- `proposal.md`
- `source-map.md`
- `specs/**/*.md`
- `tasks.md`

按需 artifacts：

- `change-context.md`
- `ui-contract.md`
- `service-contract.md`
- `data-model.md`

这些按需 artifacts 只有本 change 需要对应架构、UI、服务或数据契约时才 Required=yes。Required=no 必须写具体原因。

## 显式 Schema

如果用户传入 `--schema <name>`：

- 使用用户指定 schema。
- 每个 change block 和每条 `/opsx:new` 命令都必须一致使用该 schema。
- 在 `Schema rationale` 中说明该 schema 是否匹配。
- 如果指定 schema 明显过重或过轻，只输出风险提示，不擅自改 schema。

## Availability Preflight

选定 schema 后，`aisee:change-plan` 还必须检查它是否能被当前项目消费：

- 已安装在 `openspec/schemas/<name>/`：可以继续输出 `/opsx:new "<change>" --schema <name>`。
- 未安装但 marketplace plugin source 可见：输出 blocker，转交 `aisee-schema-pack`，建议 `node <skill-dir>/scripts/setup-schemas.js --schema <name>`。
- source 也不可见：输出 schema availability blocker，并说明 author / implementation 无法继续。

schema 状态检查只使用 `aisee schemas list/check --json`。

## 混合系统

混合系统可以同时需要 app 与 device schema，但每个具体 change 仍只能选择一个 schema。不要为了省事把云端、App、设备和固件塞进一个超大 change。

## Schema Rationale 必须说明

- 为什么选择该 schema。
- 如果不是 `aisee-app-spec-driven`，为什么不需要 SRS / UI Content / Architecture 追踪。
- 需要哪些 upstream docs：SRS / UI Content / Design Spec / Design Assets / Architecture / Issue / PR / none。
- 是否需要 `source-map.md` seed；只有 schema 生成 `source-map.md` 时才要求 seed。
