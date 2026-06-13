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

## 必做判定维度

每个 change 在选 schema 前，至少按以下维度内部审查一次：

| 维度 | 要判断什么 | 常见信号 |
|---|---|---|
| 交付意图 | 是生产实现、轻量修复、调研结论、文档维护，还是基础设施/安全工作 | “上线功能”“修一个问题”“回答可行性”“改 docs”“改 CI / 部署 / 权限” |
| 可观察结果 | 用户、操作者、系统或设备最终能看到什么变化 | 新能力、修复后的行为、调研结论、审计报告、部署策略、硬件行为 |
| 契约足迹 | 是否需要新增或显著修改 UI / API / DATA / HW / FW / RT / VER 契约 | 新接口、数据模型变化、前端状态流、设备协议、验证合同 |
| 上游追踪 | 是否需要稳定追踪 SRS / UI Content / Design Spec / Architecture / hardware context | 需要把前置 planning docs 压缩进后续实现 contract |
| 风险与不确定性 | 是否仍在回答 go/no-go、根因未明、架构/安全决策未定 | spike、PoC、待确认、一致性策略未定、第三方集成未知 |
| 规模与 owner | 是否单一 owner、预计时长、是否跨多个域 | <=1 天单点修复、跨团队共享前置、横跨 app + infra + security |

不要只看用户表面措辞。用户说“只是小改”但如果已经包含新 API / 数据 / 权限 / 设备契约，就不是 `quick-fix`。

## 结构化裁决规则

每个 change 必须输出一个明确的 schema 裁决，而不是只写一句“推荐 X schema”：

- 至少列出 `Selected schema` 和 `Alternative schemas considered`。
- 至少写出 1 个被拒绝的候选 schema；若确实只有 1 个合理候选，明确写 `No credible alternative`。
- `Selected schema` 的理由必须回到上面的判定维度，而不是重复工作类型名称。
- 被拒绝 schema 的理由必须可操作，例如“会错误要求 source-map / specs”“会把调研结论升级成实现任务”“缺少安全 threat-model”“无法承接 HW/FW/RT/VER”。

推荐的最小内部裁决表：

| 候选 schema | 结论 | 关键理由 |
|---|---|---|
| `quick-fix` | reject | 需要新增服务契约和审计语义，超出单点修复 |
| `aisee-app-spec-driven` | select | 需要 source-map、specs、tasks，并承接 SRS / Architecture 追踪 |

## 低置信度阻断

当以下任一情况成立时，不得硬选 schema；先问最多 1 个决定性问题，或直接输出 `[SCHEMA-SELECTION-BLOCKED]`：

- 两个 schema 都看起来合理，且选择不同 schema 会改变后续 artifact 形态。
- 当前证据无法判断它是生产实现还是调研 / 风险验证。
- 当前证据无法判断它是 app 业务变更，还是 infra/security/device 主导变更。
- 根因未明，可能跨 `quick-fix`、`infra-change`、`security-audit` 或 `aisee-app-spec-driven`。
- 用户显式指定 schema，但输入事实明显指向另一个 schema，且是否接受该风险会影响 author 阶段。

`[SCHEMA-SELECTION-BLOCKED]` 最小内容：

- `Change`
- `Why blocked`
- `Candidate schemas still in contention`
- `Decisive question`
- `Do not run /opsx:new yet`

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
- 在 `Schema rationale` 中说明该 schema 是否匹配，并至少给出 1 个替代 schema 为什么没有被选。
- 如果指定 schema 明显过重或过轻，只输出风险提示，不擅自改 schema。

## Availability Preflight

选定 schema 后，`aisee:change-plan` 还必须检查它是否能被当前项目消费：

- 已安装在 `openspec/schemas/<name>/`：可以继续输出 `/opsx:new "<change>" --schema <name>`。
- 未安装但 marketplace plugin source 可见：输出 blocker，转交 `aisee-schema-pack`，建议 `node <skill-dir>/scripts/setup-schemas.js --schema <name>`。
- source 也不可见：输出 schema availability blocker，并说明 author / implementation 无法继续。

schema 状态检查只使用 `aisee schemas list/check --json`。

## 混合系统

混合系统可以同时需要 app 与 device schema，但每个具体 change 仍只能选择一个 schema。不要为了省事把云端、App、设备和固件塞进一个超大 change。

## 一致性反查

选完 schema 后，必须做一次反查；若反查失败，说明 schema 选错了或边界还没定清：

- 选择 `quick-fix` 时：
  - 不应需要新的 `service-contract.md`、`data-model.md`、`ui-contract.md` 或完整 `source-map.md` 追踪。
  - 不应把新业务能力、跨模块契约或多阶段落地写进 In Scope。
- 选择 `quick-research` 时：
  - 不应输出生产实现任务、上线步骤或承诺交付生产代码。
  - 应把结论写成问题、发现、建议或 go/no-go。
- 选择 `infra-change` 时：
  - 核心交付应是环境、部署、流水线、运行时配置或回滚控制，而不是面向用户的新业务能力。
- 选择 `security-audit` 时：
  - 核心交付应围绕威胁、控制、审计或安全验证；不要把它弱化成普通功能迭代。
- 选择 `aisee-app-spec-driven` 时：
  - 应确实需要 `source-map.md`、`specs/**/*.md`、`tasks.md` 这套追踪闭环。
- 选择 `aisee-device-spec-driven` 时：
  - 应出现 HW / FW / RT / VER 线索；不要回退成 Web/API/DB 主体。

若反查发现矛盾，优先修正 change 边界；边界仍不清时输出 `[SCHEMA-SELECTION-BLOCKED]`。

## Schema Rationale 必须说明

- 为什么选择该 schema。
- 还评估了哪些 schema，为什么没有选它们。
- 如果不是 `aisee-app-spec-driven`，为什么不需要 SRS / UI Content / Architecture 追踪。
- 需要哪些 upstream docs：SRS / UI Content / Design Spec / Design Assets / Architecture / Issue / PR / none。
- 是否需要 `source-map.md` seed；只有 schema 生成 `source-map.md` 时才要求 seed。
