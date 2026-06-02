# Spec Migration 工作流

本文维护 `aisee:spec-migrate` 的详细执行流程。`SKILL.md` 只保留入口、边界、扫描规则和 reference 路由。

## Phase 1 — 读取证据

按需读取：

- README、产品文档、接口文档、OpenAPI
- 路由 / 页面 / controller / service / model / schema
- 测试用例、fixture、seed 数据
- 权限中间件、状态机、任务队列、通知、导入导出
- 现有 `openspec/project.md` 和 `openspec/specs/`

证据优先级：

- `high`：测试、OpenAPI、路由、schema、现有 spec、稳定项目文档
- `medium`：README、页面文本、用户明确说明
- `low`：命名推断、目录结构推断；只能作为候选，不能写成确定需求

文件扫描必须遵守 `.gitignore`。不要从 ignored 文件、依赖包、构建输出、缓存内容或生成产物中提取 baseline 事实。

## Phase 2 — 能力边界建模

需要追问时读取 `references/question-bank.md`，只问会影响能力边界或 baseline 事实的问题。

建模原则：

- 按业务能力划分：认证、用户、订单、支付、通知、报表等。
- 不按代码层划分：不要生成 `frontend/spec.md`、`backend/spec.md`、`database/spec.md` 这类技术层 spec。
- 跨模块规则放 `openspec/specs/project.md` 或 `_global/<topic>/spec.md`。
- 单个 spec 预计超过 200 行时拆子能力。
- 单个批次不超过 `--batch-size` 个 spec 文件；大项目先生成迁移索引和第一批。

冲突处理：

- 代码与文档冲突：标注 `[BEHAVIOR-CONFLICT]`。
- 缺少证据：标注 `[EVIDENCE-GAP]`。
- 行为看似 bug 但已被测试固定：标注 `[CURRENT-BEHAVIOR]`，不要改写成理想行为。
- 需要业务负责人确认：标注 `[SPEC-OWNER-REQUIRED]`。

## Phase 3 — 生成迁移索引

读取 `assets/migration-index-template.md`，生成：

```text
aisee/docs/spec-migration/<YYYY-MM-DD>-<slug>/00-index.md
```

内容包括：

- 迁移范围
- 扫描证据
- 能力地图
- 目标 `openspec/specs/` 树
- 每个 spec 的来源、可信度、负责人和状态
- 冲突、缺口和 Open Questions
- 分批迁移计划

如果用户只要求评估，停在索引，不写 `openspec/specs/`。

## Phase 4 — 生成 baseline specs

不要使用本 skill 内置的 spec 正文模板；OpenSpec spec 格式必须以当前项目环境中的 OpenSpec CLI 为准。

先解析当前环境：

```bash
openspec --version
openspec templates --schema spec-driven --json
```

用途：

- `templates --schema ... --json` 返回的 `specs.path` 是 change delta spec 的官方模板。只有用户明确要求通过 bootstrap change 迁移时，才读取并使用该模板。
- `openspec/specs/` 下的 baseline 静态 spec 不使用 change delta 模板；它必须通过当前 `openspec validate <capability>` 校验。若校验提示与本技能说明不一致，以当前 CLI 校验提示为准。

默认写入：

```text
openspec/specs/project.md
openspec/specs/<capability>/spec.md
```

格式规则：

- 直接写入 `openspec/specs/` 的 baseline 使用 OpenSpec 静态 spec 格式；生成后必须用 `openspec validate <capability>` 验证。
- 只有在用户明确要求通过 bootstrap change 迁移时，才在 `openspec/changes/<change>/specs/` 使用当前 schema 的 delta `specs.path` 模板。
- 每条 Requirement 必须满足当前 OpenSpec 校验器的强制规则，包括 `SHALL` / `MUST` 和至少一个 Scenario。
- Scenario 必须满足当前 OpenSpec 校验器识别的格式；不要凭记忆或旧模板猜测格式。
- 不把实现细节写成需求；写用户可观察行为、系统契约和业务约束。
- 来源证据写入迁移索引；spec 文件只保留必要的职责、依赖和行为契约。

如果证据不足：

- 不生成该 Requirement，写入 Open Questions。
- 或生成带 `[EVIDENCE-GAP]` 的草案，只在 `aisee/docs/spec-migration/` 中保留，不写入 `openspec/specs/`。

## Phase 5 — 校验

至少执行：

```bash
find openspec/specs -maxdepth 4 -name '*.md' -print
rg -n "### Requirement:|SHALL|MUST|#### Scenario:" openspec/specs aisee/docs/spec-migration 2>/dev/null
```

如果写入了某个 capability，例如 `auth`，必须运行：

```bash
openspec validate auth
```

如果写入多个 capability，逐个运行。也可以补充运行：

```bash
openspec validate
```

若校验命令不可用，说明未验证项和风险。

## 完成输出

完成后输出：

```text
Spec 基线迁移已整理：aisee/docs/spec-migration/{slug}/00-index.md

写入 / 建议写入：{N} 个 baseline spec，覆盖 {M} 个能力，发现 {C} 个冲突、{Q} 个待确认项。

下一步：确认 Open Questions 后，后续新需求使用 aisee:srs → aisee:ui-content / aisee:architecture → aisee:change-plan → /opsx:new。
```

若存在阻塞项：

```text
存在迁移阻塞项：{tags}
不建议在这些能力上继续创建新 change，直到 baseline spec 确认。
```
