# Aisee CLI、上下文索引与 ID Registry 设计方案

## 背景

在 Aisee、OpenSpec 与 Compound Engineering 串通之后，最大的效率瓶颈不再是“能不能生成文档”，而是：

- AI 每次都要重新读取大量 SRS、UI 内容规格、技术架构、OpenSpec change 和 review 记录。
- 不同 skill 之间容易复制上下文，导致重复文档和事实漂移。
- Compound Engineering 的 `ce-work`、`ce-doc-review`、`ce-code-review` 需要准确输入，但不应该重新理解全局需求。
- 如果用 ID 串联需求、页面、spec、任务、代码和验证记录，就必须保证 ID 不乱、不重复、不复用。

因此建议新增一个 **Aisee CLI**，作为面向 AI 的上下文索引、解析、查询和初始化工具。

## 定位

```text
OpenSpec CLI
= 管理 OpenSpec change / spec / schema / validate / archive

Aisee CLI
= 解析 Aisee + OpenSpec + Compound 产物，返回结构化 context JSON

Compound Engineering
= 审核、执行、测试、提交、PR、复盘
```

Aisee CLI 不替代 OpenSpec CLI，也不替代 Compound Engineering。它的核心价值是为 AI 和 skill 提供 **高效、准确、可追踪的上下文接口**。

## 设计原则

- **只读优先**：V1 默认只解析、索引、查询和检查，不生成业务文档，不执行 archive。
- **JSON 优先**：所有关键命令都支持 `--json`，方便 AI 精准消费。
- **来源可追踪**：返回内容必须包含文件路径、标题、行号、hash 或摘要。
- **ID 驱动**：通过稳定 ID 查询需求、页面、接口、硬件约束、固件行为、验证项和任务。
- **OpenSpec 作为规范事实源**：Aisee CLI 解析 OpenSpec change，但不重写 OpenSpec 状态机。
- **Compound 作为执行消费方**：Aisee CLI 可生成给 `ce-doc-review`、`ce-work`、`ce-code-review` 的 context pack。
- **幂等初始化**：bootstrap 能检查和补齐环境，但必须可审计、可回滚、默认先 plan。

## CLI 能力分层

### doctor

只检查，不修改。

```bash
aisee doctor --json
```

输出示例：

```json
{
  "openspec": {
    "cli": "missing",
    "project_initialized": false
  },
  "aisee": {
    "schemas_installed": false,
    "memory_initialized": false,
    "hooks_installed": false,
    "context_index": "missing",
    "id_registry": "missing"
  },
  "compound": {
    "plugin_available": false,
    "skills": {
      "ce-work": false,
      "ce-doc-review": false,
      "ce-code-review": false
    }
  }
}
```

### bootstrap

生成或执行项目初始化计划。

```bash
aisee bootstrap --plan --json
aisee bootstrap --apply
```

`--plan` 只输出计划，不修改文件。

`--apply` 可以执行：

- 检查或安装 OpenSpec CLI。
- 调用 `openspec init`。
- 安装或同步 Aisee schema pack。
- 执行 Aisee 项目记忆初始化。
- 创建或修复 `AGENTS.md`、`openspec/project.md`、`.memory/`。
- 安装或修复 Codex hooks。
- 检查 Compound Engineering plugin 是否可用。
- 检查 `ce-doc-review`、`ce-work`、`ce-code-review` 等 skill 是否存在。

高影响操作必须确认：

- 覆盖或修改 `AGENTS.md`、旧项目兼容用 `CLAUDE.md`、`openspec/project.md`。
- 修改 `.codex/hooks.json`。
- 安装全局依赖。
- 删除、迁移或重命名已有文件。

### install / init 子命令

`bootstrap` 应该只是编排器，底层能力拆成可单独调用的命令：

```bash
aisee install openspec
aisee install compound
aisee init project
aisee init memory
aisee init hooks
aisee schemas install
```

这样便于调试，也避免一个命令做太多不可见修改。

## 上下文索引能力

### sources

登记 change 外部的 Aisee 产物来源。

SRS、UI content、architecture、device-context、design-assets 等通常不在 OpenSpec change 目录内，仅依赖 change schema 无法发现这些上游产物。因此需要项目级来源登记：

```text
.aisee/sources.json
```

它不是内容副本，只记录来源、scope、模板和 parser。

示例：

```json
{
  "version": 1,
  "sources": {
    "requirements": [
      {
        "scope": "auth",
        "type": "srs",
        "path": "docs/requirements/auth-srs.md",
        "template": "aisee-srs",
        "parser": "srs"
      }
    ],
    "ui_content": [
      {
        "scope": "auth",
        "type": "ui-content",
        "path": "docs/ui-content/auth-ui.md",
        "template": "aisee-ui-content",
        "parser": "ui-content"
      }
    ],
    "architecture": [
      {
        "scope": "auth",
        "type": "architecture",
        "path": "docs/architecture/auth-architecture.md",
        "template": "aisee-architecture",
        "parser": "architecture"
      }
    ]
  }
}
```

推荐命令：

```bash
aisee sources add --scope auth --type srs --path docs/requirements/auth-srs.md --template aisee-srs
aisee sources list --json
aisee sources check --json
```

### index

扫描项目并建立可重建缓存。

```bash
aisee index --json
```

`aisee index` 不创建第二份内容事实源。它只用于检查、加速查询和发现断链。缓存可以删除并重建。

建议扫描范围：

```text
.aisee/sources.json
.aisee/id-registry.json
docs/requirements/**
docs/ui-content/**
docs/architecture/**
docs/design-assets/**
docs/svg-assets/**
openspec/changes/**
openspec/specs/**
docs/reviews/**
docs/verification/**
```

输出文件建议放在 cache 目录：

```text
.aisee/cache/context-index.json
```

规则：

- cache 可删除。
- cache 可重建。
- cache 不手改。
- cache 不作为权威内容来源。
- `context pack` 默认可以绕过 cache 直接解析。

### get

根据 ID 精准查询原文和结构化内容。

```bash
aisee get auth:FR-001 --json
aisee get payment:PAGE-003 --json
aisee get device-sampling:FW-002 --json
```

返回示例：

```json
{
  "id": "auth:FR-001",
  "type": "FR",
  "scope": "auth",
  "title": "用户手机号验证码登录",
  "source": {
    "path": "docs/requirements/auth-srs.md",
    "heading": "FR-001 用户手机号验证码登录",
    "line_start": 42,
    "line_end": 58,
    "hash": "sha256:..."
  },
  "content": {
    "summary": "用户可以使用手机号和验证码登录。",
    "acceptance_criteria": [
      "验证码正确且未过期时登录成功",
      "验证码错误时展示错误提示"
    ],
    "priority": "must"
  },
  "relations": {
    "pages": ["auth:PAGE-001"],
    "changes": ["change:add-auth-login"],
    "tasks": ["auth:TASK-001", "auth:TASK-002"],
    "specs": ["auth:SPEC-001"]
  }
}
```

### trace

根据任意 ID 查询上下游关系。

```bash
aisee trace auth:FR-001 --json
```

返回链路：

```text
auth:FR-001
  -> auth:PAGE-001
  -> change:add-auth-login
  -> auth:SPEC-001
  -> auth:TASK-002
  -> src/auth/session.ts
  -> tests/auth/session.test.ts
```

### change inspect

解析单个 OpenSpec change 的完整上下文。

```bash
aisee change inspect add-auth-login --json
```

解析内容：

- `proposal.md`
- `design.md`
- `specs/**/spec.md`
- `tasks.md`
- `source-map.md`
- `ui-contract.md`
- `service-contract.md`
- `data-model.md`
- `hardware-contract.md`
- `firmware-contract.md`
- `runtime-contract.md`
- `verification-contract.md`
- review records
- verification records

CLI 应该 schema-aware，不要把 App/Web schema 硬套到硬件/嵌入式 change。

### context pack

调用时直接解析 Markdown、OpenSpec artifacts、ID Registry、sources registry 和 source-map，为不同 skill 或 CE 能力生成最小上下文包。

```bash
aisee context pack --change add-auth-login --for ce-doc-review --json
aisee context pack --change add-auth-login --for ce-work --json
aisee context pack --change add-auth-login --for ce-code-review --json
aisee context pack --change add-auth-login --for aisee-verify --json
```

默认行为：

```text
1. 读取 .aisee/sources.json，发现 SRS / UI content / architecture / device-context 等 change 外部产物。
2. 读取 .aisee/id-registry.json，获取 ID 分配和生命周期。
3. 读取 openspec/changes/<change>/source-map.md，获取当前 change 关联的上游 ID、文件和 artifact。
4. 读取 openspec/config.yaml 与 change/.openspec.yaml，识别当前 change schema。
5. 读取 schema.yaml 与 artifact 模板，解析 change 内部 OpenSpec artifacts。
6. 按 Aisee source template 解析 change 外部产物。
7. 输出 JSON。
```

JSON 是当前 Markdown / artifact 的结构化视图，不是新生成的事实源。默认只包含：

```text
parsed
= 从模板化 Markdown / OpenSpec artifacts 直接解析

derived
= 根据 source-map、ID registry、文件关系和校验规则推导
```

默认不包含 AI 生成摘要。需要摘要或压缩内容时必须显式开启：

```bash
aisee context pack --change add-auth-login --for ce-work --json --with-summary
```

若包含 generated 字段，必须标记来源：

```json
{
  "summary": {
    "mode": "generated",
    "text": "...",
    "model": "..."
  }
}
```

解析器应是 template-aware，不应自由猜测任意 Markdown。高置信解析依赖：

```text
- Aisee source template
- OpenSpec schema.yaml
- artifact templates
- frontmatter
- 固定 heading
- ID marker
- source-map 约定
```

不同目标的上下文不同：

```text
ce-doc-review:
  proposal / design / specs / tasks / source-map / contracts
  不包含完整代码上下文，除非文档声明依赖现有代码事实

ce-work:
  specs / tasks / source-map / design / contracts / execution rules
  不重复 SRS 全文，只引用相关 ID

ce-code-review:
  change 目标 / tasks / source-map / diff / test evidence / review checklist

aisee-verify:
  全部 artifact 摘要 / ID 关系 / gaps / validate 结果 / review 结果
```

### gaps

检查断链、缺口和不一致。

```bash
aisee gaps --change add-auth-login --json
```

检查项：

- FR 没有进入任何 OpenSpec change。
- PAGE 没有映射到 UI contract 或 tasks。
- TASK 没有上游 FR/SPEC。
- source-map 指向不存在文件。
- spec 描述了行为，但 tasks 没有实现项。
- tasks 有实现项，但没有验证记录。
- review finding 没有处理或记录接受理由。
- 硬件/嵌入式缺少样机版本、固件版本、台架/HIL/量产测试记录。

## Aisee Skill 如何使用 CLI

### aisee:flow

使用：

```bash
aisee doctor --json
aisee index --json
aisee gaps --json
aisee flow inspect --json
aisee flow next --json
aisee context pack --change <change> --for flow --json
```

职责：

- 读取项目状态、OpenSpec change、sources registry、ID registry、source-map、review/test 记录。
- 判断当前 workflow stage。
- 识别缺口、断链、过期和冲突。
- 输出工作流状态卡。
- 编排下一组 Aisee skill、OpenSpec 操作和 CE gate。
- 阻止错误跳步。

`aisee:flow` 不负责拆 change，也不为多个 change 决定最终 schema。它只给 domain 或 schema family hint；per-change schema 由 `aisee:change-plan` 决定。

建议 CLI 返回结构：

```json
{
  "stage": "context-ready",
  "domain_hint": "app",
  "known_inputs": {
    "srs": "docs/requirements/auth-srs.md",
    "ui_content": "docs/ui-content/auth-ui.md",
    "architecture": "docs/architecture/auth-architecture.md"
  },
  "missing": [
    "change-plan",
    "openspec-change-artifacts"
  ],
  "blocking": [
    "cannot-enter-ce-work-before-change-authored"
  ],
  "recommended_path": [
    "aisee:change-plan",
    "aisee:change-author",
    "ce-doc-review",
    "aisee:verify"
  ],
  "guardrails": [
    "do-not-create-parallel-ce-plan",
    "per-change-schema-owned-by-change-plan"
  ]
}
```

推荐 workflow stage：

```text
uninitialized
idea
requirement-ready
context-ready
change-planned
change-authored
doc-reviewed
implementation-ready
implemented
verified
archive-ready
```

### aisee:change-author

使用：

```bash
aisee change inspect <change> --json
aisee get <id> --json
aisee trace <id> --json
```

职责：

- 根据 schema 补齐 OpenSpec artifacts。
- 只引用 SRS/UI/architecture 中的 ID，不复制整段内容。
- 为 `source-map.md` 建立关系。

### aisee:implementation-bridge

使用：

```bash
aisee context pack --change <change> --for ce-work --json
```

输出给 CE 的薄交接块：

```md
# Implementation Brief

## Authoritative Source

- Change: `openspec/changes/<change-id>`
- Tasks: `openspec/changes/<change-id>/tasks.md`
- Source Map: `openspec/changes/<change-id>/source-map.md`
- Specs: `openspec/changes/<change-id>/specs/**/spec.md`

## Execution Rules

- 按 `tasks.md` 执行。
- 不创建新的长期任务清单。
- 不扩大 change 范围。
- 如发现需求/spec 不一致，先回写当前 OpenSpec change。
- 完成后更新 `tasks.md` 和验证记录。

## Recommended Compound Skill

- `ce-work`
- 实现后使用 `ce-code-review`
- 失败时使用 `ce-debug`
```

### aisee:verify

使用：

```bash
aisee gaps --change <change> --json
aisee context pack --change <change> --for aisee-verify --json
```

职责：

- 查一致性。
- 查缺口。
- 查 drift。
- 消费 `ce-doc-review`、`ce-code-review`、`ce-test-*` 的结果。

### aisee:archive-guard

使用：

```bash
aisee gaps --change <change> --json
openspec validate <change>
```

职责：

- 读取已有验证和 review 结果。
- 判断是否可以执行 `openspec archive`。
- 不重新做完整 review，不重新规划 change。

## Compound Engineering 的使用位置

Compound 不应和 OpenSpec `tasks.md` 争夺任务事实源。

建议规则：

```text
tasks.md
= 唯一长期任务清单

ce:plan
= 可选任务细化器；结论必须回写 tasks.md/source-map.md

ce:work
= 按单个 OpenSpec change 工程包执行
```

推荐插入点：

```text
需求 / 规范阶段:
  ce-doc-review
  审核 SRS、design.md、contracts、tasks.md

实现阶段:
  ce-work
  按 OpenSpec change 执行代码修改

问题定位:
  ce-debug
  处理测试失败、行为异常、实现阻塞

实现后:
  ce-code-review
  ce-test-browser / ce-test-xcode

交付阶段:
  ce-commit
  ce-commit-push-pr
  ce-resolve-pr-feedback
  ce-compound
```

CE 输出归档规则：

```text
ce-doc-review
  -> docs/reviews/<change-id>-doc-review.md
  -> 只记录 findings；需要长期保留的结论回写 owner 文档

ce-work
  -> 直接修改代码和必要的 tasks/verification 记录
  -> 不长期保存平行 plan

ce-code-review
  -> docs/reviews/<change-id>-code-review.md 或 PR review
  -> P0/P1 必须处理或记录接受理由

ce-debug
  -> 可写入 verification record 或 implementation note
  -> 影响规范时回写 OpenSpec change
```

## ID 管理方案

ID 不能只靠人工维护，必须由 CLI 约束。

### ID 类型

建议使用类型前缀：

```text
FR-001    功能需求
NFR-001   非功能需求
PAGE-001  页面
FLOW-001  用户流程
API-001   接口能力
DATA-001  数据实体或字段
AUTH-001  权限规则
HW-001    硬件约束
FW-001    固件行为
RT-001    运行时约束
VER-001   验证项
SPEC-001  规范行为
TASK-001  任务
RISK-001  风险
DEC-001   设计决策
```

### 命名空间

完整 ID 使用：

```text
<scope>:<TYPE>-<number>
```

示例：

```text
auth:FR-001
auth:PAGE-001
payment:FR-001
device-sampling:HW-001
device-sampling:FW-001
```

文档中可以显示短 ID，但机器索引用完整 ID：

```md
### FR-001 用户登录
<!-- aisee:id auth:FR-001 -->
```

跨文档引用必须使用完整 ID：

```md
覆盖需求：`auth:FR-001`
```

## ID Registry

建议路径：

```text
.aisee/id-registry.json
```

职责：

- 记录已经分配过哪些 ID。
- 记录 ID 生命周期。
- 防止重复分配。
- 防止删除后复用。
- 记录 owner 文档。

示例结构：

```json
{
  "version": 1,
  "scopes": {
    "auth": {
      "counters": {
        "FR": 4,
        "PAGE": 2,
        "TASK": 6
      },
      "ids": {
        "auth:FR-001": {
          "type": "FR",
          "number": 1,
          "status": "active",
          "title": "用户手机号验证码登录",
          "owner": "docs/requirements/auth-srs.md",
          "created_at": "2026-05-28T10:00:00+08:00",
          "updated_at": "2026-05-28T10:00:00+08:00"
        },
        "auth:FR-002": {
          "type": "FR",
          "number": 2,
          "status": "deprecated",
          "title": "用户密码登录",
          "owner": "docs/requirements/auth-srs.md",
          "replaced_by": ["auth:FR-004"],
          "reason": "登录方式拆分后废弃",
          "created_at": "2026-05-28T10:02:00+08:00",
          "updated_at": "2026-05-28T11:10:00+08:00"
        }
      }
    }
  }
}
```

### ID 状态

```text
reserved    已预留，还没写入文档
active      当前有效
deprecated  已废弃，有替代或原因
merged      合并到其他 ID
split       拆分为多个 ID
removed     删除但禁止复用
```

规则：

- counters 只增不减。
- 删除过的 ID 保留记录，不能复用。
- ID 只能由 CLI 分配。
- 人和 AI 不直接手写新编号。
- owner 指向该 ID 的负责文档。

### ID 命令

```bash
aisee id next --scope auth --type FR --json
aisee id reserve --scope auth --type FR --count 3 --json
aisee id activate auth:FR-005 --owner docs/requirements/auth-srs.md --title "用户扫码登录"
aisee id deprecate auth:FR-002 --replaced-by auth:FR-004 --reason "登录方式拆分"
aisee id check --json
```

`reserve` 返回示例：

```json
{
  "reserved": [
    {
      "id": "auth:FR-005",
      "short_id": "FR-005",
      "status": "reserved"
    }
  ]
}
```

### id-registry、sources 与 cache 分工

```text
.aisee/id-registry.json
= ID 分配和生命周期事实源

.aisee/sources.json
= change 外部 Aisee 产物的来源登记事实源，只记录路径、scope、模板和 parser

.aisee/cache/context-index.json
= 可删除、可重建的解析缓存，用于加速查询；不是事实源
```

不要把三者混在一起。

Registry 负责回答：

```text
这个 ID 是否存在？
这个 ID 是否还能使用？
这个 ID 是否已废弃、合并、拆分或删除？
下一个可用 ID 是什么？
```

Sources 负责回答：

```text
SRS 在哪里？
UI content 在哪里？
architecture / device-context 在哪里？
这些外部产物使用哪个模板和 parser？
```

Context pack 调用时负责直接解析并回答：

```text
这个 ID 当前在哪里？
内容是什么？
关联了哪些页面、spec、tasks、代码和验证记录？
```

Cache 只加速这些回答，不保存权威内容。

## ID 校验规则

`aisee id check` 和 `aisee gaps` 应检查：

- 同一 scope 内 ID 是否重复。
- 文档中出现未注册 ID。
- registry 中 active ID 的 owner 文件不存在。
- reserved ID 超时未激活。
- removed ID 被重新引用。
- deprecated ID 是否还有新增引用。
- source-map 是否存在断链。
- TASK 是否没有上游 FR/SPEC。
- FR 是否没有进入任何 change。
- ID 前缀是否和文档类型匹配。

## 推荐工作流

### 新需求

```text
1. aisee doctor
2. aisee id reserve --scope auth --type FR --count 3
3. aisee:srs 写 SRS，使用预留 ID
4. aisee index
5. aisee id check
6. aisee:ui-content / aisee:device-context
7. aisee:change-plan
8. aisee:change-author
9. aisee context pack --change <change> --for ce-doc-review
10. ce-doc-review
11. aisee:verify
12. aisee context pack --change <change> --for ce-work
13. ce-work
14. ce-code-review / ce-test-*
15. aisee:archive-guard
16. openspec archive
```

### 既有项目初始化

```text
1. aisee doctor --json
2. aisee bootstrap --plan
3. 用户确认
4. aisee bootstrap --apply
5. aisee schemas install
6. aisee index
7. aisee id check
```

## V1 建议边界

第一版不要做太大。

必须做：

- `aisee doctor --json`
- `aisee bootstrap --plan`
- `aisee index --json`
- `aisee get <id> --json`
- `aisee trace <id> --json`
- `aisee change inspect <change> --json`
- `aisee context pack --change <change> --for ce-work --json`
- `.aisee/id-registry.json`
- `aisee id reserve / activate / check`

暂缓：

- 自动生成完整业务文档。
- 自动执行 `openspec archive`。
- 自动创建 PR。
- 自动安装所有全局依赖。
- 复杂图数据库或长期后台服务。

## 最终建议

Aisee CLI 应该成为 Aisee/OpenSpec/Compound 之间的 **上下文总线**。

```text
Aisee skills
  通过 CLI 获取精准上下文

OpenSpec
  提供规范目录、schema、validate、archive

Compound Engineering
  消费 CLI 生成的 context pack 做审核、实现、测试和交付

.aisee/id-registry.json
  管 ID 分配和生命周期

.aisee/sources.json
  管 change 外部 Aisee 产物的来源登记

.aisee/cache/context-index.json
  作为可重建缓存加速查询，不作为事实源
```

这样可以减少重复读取和重复生成文档，让每个 skill 都围绕稳定 ID、source-map 和 JSON context 高效衔接。
