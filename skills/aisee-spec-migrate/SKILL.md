---
name: aisee:spec-migrate
description: 基于已有项目快速整理 OpenSpec baseline specs，把现有代码、路由、页面、测试、API 文档和业务文档反向归纳为 openspec/specs/ 下的当前行为规范。用于“把旧项目迁移到 OpenSpec 管理”“整理现有系统 spec 基线”“从代码生成 OpenSpec specs”“补齐 openspec/specs”“建立 baseline spec”时触发。不要用于新需求 SRS、change 边界规划、design.md、tasks.md、实现代码或未来功能规划。
---

# aisee:spec-migrate — 现有项目 Spec 基线迁移

把已有项目的当前行为整理成 OpenSpec 静态层 `openspec/specs/`。它回答“系统现在是什么”，为后续 `/opsx:new`、delta specs 和 archive 建立基线。

它不是 `aisee:srs`：不整理未来需求。  
它不是 `aisee:change-plan`：不规划 OpenSpec change 边界。  
它不写 change 级 `design.md`。

## 输入

用户提供以下任意一种输入：
- 现有项目目录
- 现有需求文档、README、接口文档、测试目录
- 已初始化的 OpenSpec 项目
- 指定模块或目录范围

可选参数：
- `--scope project|module|path|auto` — 迁移范围，默认 `auto`
- `--mode inventory|draft|write|auto` — 只盘点、生成草案或写入 baseline specs，默认 `auto`
- `--batch-size <n>` — 单批最多生成的 spec 文件数，默认 5
- `--write patch|direct|chat` — 写入方式，默认 `patch`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:spec-migrate` 只产出现有系统行为的 OpenSpec baseline。

必须输出或写入：
- 迁移范围和证据来源
- 能力边界图：按业务能力 / 领域划分，不按文件类型机械划分
- `openspec/specs/` 目录规划
- `openspec/specs/project.md` 的缺口建议或补丁
- `openspec/specs/<capability>/spec.md` baseline specs
- 证据追踪、可信度、冲突和 Open Questions
- 迁移批次计划，避免一次生成巨型 spec

禁止输出：
- 新功能需求或未来规划
- active change 的 delta spec，除非用户明确要求 bootstrap change
- `/opsx:new`、`/opsx:propose`、`/opsx:apply` 执行命令
- `proposal.md`、`design.md`、`tasks.md`
- 数据库迁移、实现计划或代码修改
- 无证据的业务规则断言

---

## Phase 0 — 预检

确认 OpenSpec 状态：

```bash
node -e "const fs=require('fs'); for (const p of ['openspec/config.yaml','openspec/specs']) { try { const s=fs.statSync(p); console.log(p + ':' + (s.isDirectory()?'dir':'file')); } catch { console.log(p + ':missing'); } }"
```

处理规则：
- 缺少 `openspec/config.yaml`：停止写入 `openspec/specs/`，建议先运行 `openspec init` 或 `aisee:init`。
- 缺少 `openspec/specs/`：可以创建目录补丁，但必须说明这是 baseline migration。
- 已有 `openspec/specs/`：先读取现有 spec，避免覆盖和重复建模。
- 已有 active changes：读取 `openspec/changes/`，标注可能冲突；不要把 active delta 当作 baseline 事实。

---

## Phase 1 — 扫描现有项目

静默收集项目结构：

```bash
find . -maxdepth 3 \( -name package.json -o -name pyproject.toml -o -name go.mod -o -name Cargo.toml -o -name pom.xml -o -name Gemfile -o -name README.md -o -name openapi.yaml -o -name openapi.json \) 2>/dev/null | head -120
find . -maxdepth 4 \( -iname '*route*' -o -iname '*controller*' -o -iname '*page*' -o -iname '*screen*' -o -iname '*model*' -o -iname '*schema*' -o -iname '*test*' -o -iname '*spec*' \) 2>/dev/null | head -200
find docs -maxdepth 3 -type f 2>/dev/null | head -120
```

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

---

## Phase 2 — 能力边界建模

读取 `references/question-bank.md`，只追问会影响能力边界或 baseline 事实的问题。

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

---

## Phase 3 — 生成迁移索引

读取 `assets/migration-index-template.md`，生成：

`docs/spec-migration/<YYYY-MM-DD>-<slug>/00-index.md`

内容包括：
- 迁移范围
- 扫描证据
- 能力地图
- 目标 `openspec/specs/` 树
- 每个 spec 的来源、可信度、负责人和状态
- 冲突、缺口和 Open Questions
- 分批迁移计划

如果用户只要求评估，停在索引，不写 `openspec/specs/`。

---

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
- 或生成带 `[EVIDENCE-GAP]` 的草案，只在 `docs/spec-migration/` 中保留，不写入 `openspec/specs/`。

---

## Phase 5 — 校验

至少执行：

```bash
find openspec/specs -name '*.md' -maxdepth 4 -print
rg -n "### Requirement:|SHALL|MUST|#### Scenario:" openspec/specs docs/spec-migration 2>/dev/null
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

---

## 完成输出

完成后输出：

> Spec 基线迁移已整理：`docs/spec-migration/{slug}/00-index.md`
>
> 写入 / 建议写入：{N} 个 baseline spec，覆盖 {M} 个能力，发现 {C} 个冲突、{Q} 个待确认项。
>
> 下一步：确认 Open Questions 后，后续新需求使用 `aisee:srs → aisee:ui-content / aisee:architecture → aisee:change-plan → /opsx:new`。

若存在阻塞项：

> 存在迁移阻塞项：{tags}
> 不建议在这些能力上继续创建新 change，直到 baseline spec 确认。

---

## Guardrails

- 只描述当前系统行为，不描述未来要做什么。
- 不把 active change 的 delta 当作 baseline 已有能力。
- 不覆盖已有 `openspec/specs/`；先 diff，再 patch。
- 不生成巨型单文件 spec。
- 不按文件类型、技术层或数据库表机械拆 spec。
- 不把低可信度推断写入正式 baseline。
- 不把 `docs/spec-migration/` 当作 OpenSpec 规范来源；最终规范必须落在 `openspec/specs/`。
- 如果缺少 OpenSpec 初始化，先让用户运行 `openspec init` 或 `aisee:init`。

---

## 与 aisee 链路集成

```text
已有项目
  └─ aisee:init                 ← 初始化 OpenSpec 与项目上下文
       └─ aisee:spec-migrate    ← 反向整理现有系统 baseline specs
            └─ openspec/specs/  ← 当前系统行为基线

后续新需求
  ├─ aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:architecture
  └─ aisee:change-plan
       └─ /opsx:new <change>
            └─ aisee:change-author
                └─ schema artifacts + apply tracks
```
