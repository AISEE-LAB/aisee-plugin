---
name: aisee:verify
description: 按当前 OpenSpec change 的 schema 验证 artifacts、tasks、source-map、ID、review/test evidence、OpenSpec validate 和实现状态是否一致。用于实现前后读取 change inspect、context pack 和当前 artifacts，输出 schema-aware 问题清单与修复建议；不把 app schema 的 source-map/contracts 要求套到 quick-fix、quick-research、docsite、infra、security 或其它轻量 schema。
---

# aisee:verify

`aisee:verify` 是当前 change 的 schema-aware 一致性诊断器。它不创建事实源，不替代 OpenSpec parser，也不做 archive 放行审批；OpenSpec artifact 合法性以 `openspec validate` 和当前 schema 为准。

## Reviewer lens 边界

如需 Aisee 审查 lens，`aisee:verify` 只建议或消费只读一致性审查结论：

- `aisee-change-architect`：change 边界、依赖、粒度和可独立交付性。
- `aisee-spec-reviewer`：schema artifacts、contracts、source-map、tasks 的完整性、一致性和可验证性。
- `aisee-implementation-reviewer`：实现、tasks、source-map/spec 和 evidence 是否一致，是否可进入 verify/archive。

这些 lens 不修改代码、不运行测试、不提交 PR、不解决 CI，也不替代 `ce-doc-review`、`ce-code-review`、`ce-test-*` 或 `ce-work`。接口、UI、硬件、固件、安全和验证差异只能作为 schema-aware check lenses。

触发时机：

- `aisee-spec-reviewer`：实现前发现 artifacts/contracts/tasks/source-map 一致性不清时，可建议回到该 role 先审。
- `aisee-implementation-reviewer`：`ce-work` 完成后、正式输出 verify 结论前建议触发或消费其结果。
- `aisee-change-architect`：verify 阶段只在发现当前实现暴露 change 边界错误时建议回退触发，不作为常规 verify 子步骤。

## 职责

- 识别当前 change 使用的 schema，并只检查该 schema 声明的 artifacts、requires、apply tracks 和验证证据。
- 自动读取只读 CLI JSON：`change inspect`、`context pack --for aisee-verify`。用户不承担常规手工运行 CLI 的路径。
- 运行或建议运行 `openspec validate <change>`。
- 运行 `aisee change inspect <change> --json`、`aisee context pack --change <change> --for aisee-verify --json`，并结合当前 artifacts/evidence 诊断一致性。
- 对需要 `source-map.md` 的 schema，检查 ID、source-map、artifact applicability、代码路径、测试路径和 evidence 是否闭合。
- 对不生成 `source-map.md` 的 schema，只检查 schema artifacts、tasks、OpenSpec validate、review/test/manual evidence 和当前 change 明确引用的路径。
- 消费已有 `ce-doc-review`、`ce-code-review`、`ce-test-*`、人工验证记录和监控/预览证据。
- 识别当前 change 是否触及公开接口或高风险表面，并输出是否建议审查代理 / Tier 2 code review。
- 输出 BLOCKER / RISK / INFO findings、修复建议和 archive-guard 前置状态。

## 不负责

- 创建、拆分或重新规划 change。
- 替代 `ce-code-review`、`ce-doc-review` 或测试工具。
- 修改 artifacts、代码、baseline specs 或 evidence。
- 判断是否可以执行 `openspec archive`；这是 `aisee:archive-guard` 的职责。
- 重新解析 OpenSpec proposal/spec/tasks/design/contracts 的业务语义。
- 为轻量 schema 强制补 app schema 才需要的 `source-map.md`、`ui-contract.md`、`service-contract.md`、`data-model.md` 或 `change-context.md`。

## 输入入口

必须以当前 change 为入口。按顺序运行：

```bash
aisee change inspect <change> --json
aisee context pack --change <change> --for aisee-verify --json
```

同时建议运行：

```bash
openspec validate <change>
```

如果 CLI 不可用，只读取当前 change 目录、当前 schema、schema 声明的 artifacts、已有 review/test/manual evidence，以及当前 artifacts 明确引用的路径。只有 schema 生成 `source-map.md` 时才读取 source-map。

## Schema 上下文

先从 `change inspect`、change metadata 或 schema 文件确认：

- `schema_name`：当前 schema 名称。
- `schema_artifacts`：schema 声明的 artifact id 与生成文件。
- `source_map_required`：schema 是否生成 `source-map.md`。
- `apply_tracks`：schema apply 阶段跟踪的文件，通常是 `tasks.md`。
- `required_contracts`：仅 app/device 等 source-map schema 中 Required=yes 的按需 artifacts。

若当前 schema 不生成 `source-map.md`，`source_map_required=false` 应由 CLI/context pack 直接体现；不要手工补伪 source-map。

## 输入处理规则

- `SCHEMA_METADATA_MISSING` / `SCHEMA_MISMATCH` / `SCHEMA_NOT_INSTALLED` / `SCHEMA_NOT_FOUND`：直接输出 BLOCKER，不接受 default schema fallback。
- `change inspect.ids.registry.missing / temporary / inactive` 非空：app/device/source-map schema 至少输出 RISK；inactive 或 removed ID 输出 BLOCKER。非 source-map schema 只检查当前 artifacts 明确声明的 ID。
- `context pack.facts.derived.checks` 是结构化检查入口。verify 报告不是新事实源。
- `context pack.evidence.details` 可用于读取 validate/test/review 的轻量解析结果；路径数组仍是 evidence 原始入口。
- `openspec validate` 未运行时输出 RISK；运行失败且无接受理由时输出 BLOCKER。
- 已有 CE review/test 结果只作为 evidence；verify 不替代它们。
- 未关闭的 P0 必须输出 BLOCKER；未关闭的 P1 至少输出 RISK。accepted risk 可视为已处理，但 archive-guard 仍需判断是否可接受。
- 标记为 N/A 的 artifact 必须写明原因；缺少原因时输出 RISK。只检查当前 schema 会生成或当前 change 实际保留的 artifact。

## 审查代理建议

当当前 change 触及以下任一表面时，必须在输出中给出 `Review Recommendation`：

- 公开 CLI 命令、参数、JSON 输出或退出码。
- HTTP endpoint、局域网/远程服务、API/service contract、OpenAPI/events/webhooks/proto 等机器可读契约。
- schema、artifact template、source-map parser、contract parser、ID registry、context pack 或 OpenSpec 衔接逻辑。
- 文件/路径读取、目录遍历、缓存、包安装、package assets、dependency manifest。
- 认证、权限、安全、隐私、敏感信息、生产配置或回滚策略。

规则：

- Recommendation 只提示审查门禁，不自动启动 subagent 或审查代理。
- 如果用户已明确授权“使用审查代理做 Tier 2 code review”，优先使用可用的 CE / harness 审查能力，并把结果作为 evidence。
- 如果尚未授权，在 `Suggested Next Step` 中给出可执行提示：`使用审查代理做 Tier 2 code review`。
- 如果审查代理不可用，执行本地重点自审，并在 `Evidence Reviewed` 或 `Findings` 中说明限制。
- 不满足上述表面时，可以写 `Review Recommendation: not required`，但仍保留已有 review/test evidence 检查。

## Schema 最低门槛

| Schema 类型 | 必查内容 | 不强制要求 |
|---|---|---|
| `aisee-app-spec-driven` | proposal、source-map、specs、tasks、Required=yes contracts、ID registry、代码/测试/evidence 追踪 | Required=no contracts 展开全文 |
| `aisee-device-spec-driven` | proposal、source-map、device specs/tasks、硬件/固件/验证证据追踪 | app-only UI/service/data contracts |
| `quick-fix` | problem、solution、tasks、修复范围、测试或人工验证、回滚/监控记录 | SRS、specs、source-map、contracts |
| `quick-research` | question、findings、recommendation、依据链接或实验记录、结论是否回答原问题 | 代码实现、apply、测试矩阵、source-map |
| `aisee-docsite-driven` | proposal、doc-change、tasks、构建/链接/预览验证、Archive Updates | specs、contracts、source-map |
| `infra-change` | proposal、impact-assessment、rollback-plan、tasks、预检/回滚/变更后验证证据 | app contracts、UI/data specs |
| `security-audit` | proposal、threat-model、security specs/design、tasks、安全 review/test evidence、Critical/High 风险处理 | 非安全相关的冗余 UI/data contract |

## 检查项

| 维度 | 检查内容 |
|---|---|
| Schema artifacts | schema 声明的 artifacts 是否存在；requires 顺序是否满足；N/A 是否有原因 |
| Source-map / ID | 仅在 schema 需要时检查上游 ID、产出 ID、owner artifact、代码路径、测试路径和 evidence 闭合 |
| OpenSpec validate | `openspec validate` 是否通过；失败项是否处理或有接受理由 |
| Tasks / apply tracks | tasks 是否覆盖实现、验证、证据记录；checkbox 状态是否真实；apply tracks 是否与 schema 一致 |
| Implementation drift | 代码、配置、文档或站点结构是否偏离当前 change artifacts |
| Review / test evidence | CE P0/P1、测试失败、人工验证缺口、构建/预览/监控证据是否处理或记录接受理由 |
| Archive readiness signals | 是否存在会阻止 archive-guard 的 blocker 或未说明风险 |

## Severity

- `BLOCKER`：不能进入 archive-guard，必须先修。
- `RISK`：可以继续，但 archive-guard 需要看到接受理由或补充证据。
- `INFO`：提示项，不阻断。

## 输出

```md
# Aisee Verify Report

## Result

pass / fail / pass-with-risk

## Schema Context

- Schema:
- Source-map required: yes / no
- Required artifacts:
- Required contracts:
- Skipped artifacts and reasons:

## Inputs

- Author check:
- Gaps:
- Change inspect:
- Verify check:
- Context pack:
- OpenSpec validate:

## Findings

### BLOCKER
### RISK
### INFO

## Required Fixes

## Evidence Reviewed

## Review Recommendation

- Required: yes / no
- Reason:
- Existing evidence:
- Suggested action:

## Archive-Guard Readiness

- Ready for archive-guard: yes / no / with-risk
- Reasons:

## Suggested Next Step
```
