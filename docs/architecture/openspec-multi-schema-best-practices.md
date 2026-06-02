# OpenSpec 多 Schema 共存：结论与最佳实践

> **结论先行**：一个 OpenSpec 项目可以同时存在多个 Schema，这是官方设计的核心能力，并非边缘情况。Schema 之间在设计上是隔离的，**不会产生 Schema 级别的冲突**——但存在两个需要主动管理的潜在冲突点。

---

## 一、为什么多 Schema 不冲突

每个 Schema 作用于**单个 Change**，而非整个项目。核心隔离机制如下：

```
项目
├── openspec/schemas/spec-driven/         ← Schema 定义（只读模板）
├── openspec/schemas/opsx-collab-pr-loop/ ← Schema 定义（只读模板）
│
└── openspec/changes/
    ├── feature-a/    ← 使用 spec-driven      ← 互相独立，各自的 Schema
    ├── pr-review-1/  ← 使用 opsx-collab-pr-loop
    └── hotfix-login/ ← 使用 spec-driven
```

每个 Change Folder 里的 artifacts 完全由其所绑定的 Schema 决定，不同 Change 之间不共享 artifacts，因此 **Schema 定义本身不会互相冲突**。

---

## 二、两个需要主动管理的潜在冲突点

### 冲突点 A：Delta Spec 逻辑冲突（最重要）

**发生条件**：两个使用不同 Schema 的 Change，同时对 `openspec/specs/` 下的**同一个需求**执行 `MODIFIED` 操作。

```
# 示例：两个 Change 都修改了 "Session Timeout" 需求

feature-auth（spec-driven）的 delta:
  → MODIFIED: Session Timeout（30min → 15min）

pr-review-security（opsx-collab-pr-loop）的 delta:
  → MODIFIED: Session Timeout（30min → 20min）

执行 /opsx:bulk-archive 时 → 报错，拒绝归档
```

**关键点**：冲突发生在 **Archive 阶段**，不是开发阶段。OpenSpec 会检测到逻辑冲突并阻断归档，原始文件不受影响（原子事务机制保证）。

**解决方法**：在 Spec Owner 之间沟通后，让其中一方修改 Delta，改为 `ADDED` 新需求或调整目标值，然后再归档。

---

### 冲突点 B：config.yaml rules 覆盖范围不均等

**发生条件**：`config.yaml` 中的 `rules` 按 artifact 类型 ID 注入，只有 artifact ID 匹配时才生效。

```yaml
# config.yaml 中的 rules
rules:
  proposal:   ← 只注入给 id: proposal 的 artifact
    - Include rollback plan
  specs:      ← 只注入给 id: specs 的 artifact
    - Use Given/When/Then format
  tasks:      ← 只注入给 id: tasks 的 artifact
    - Each task under 2 hours
```

```yaml
# opsx-collab-pr-loop 的 schema.yaml（artifact ID 不同）
artifacts:
  - id: intake          ← ≠ proposal，不会收到 proposal 的 rules
  - id: research-plan   ← ≠ specs，不会收到 specs 的 rules
  - id: implementation  ← ≠ tasks，不会收到 tasks 的 rules
  - id: checkpoints
```

**这不是报错**，但可能导致自定义 Schema 的 artifacts 缺少团队约定的规则注入，产生质量不一致。

**解决方法**：在自定义 Schema 的 `schema.yaml` 中，用 `instruction` 字段为每个 artifact 补充约束，或者在命名 artifact ID 时尽量与 `spec-driven` 保持一致（如保留 `proposal`、`tasks`）。

---

## 三、Schema 解析规则（避免同名覆盖问题）

OpenSpec 按以下优先级解析 Schema 的**来源位置**：

```
1. openspec/schemas/<name>/          ← 项目本地（最高，覆盖所有同名）
2. ~/.local/share/openspec/schemas/  ← 用户全局
3. npm 包内置 schemas/               ← 官方内置（最低）
```

**项目本地 Schema 会覆盖同名官方 Schema**。这是 Fork 修改的设计基础（Fork `spec-driven` 到本地后修改，不影响其他项目），但如果无意中给自定义 Schema 取了与官方相同的名字，会产生静默覆盖，注意用 `openspec schema which --all` 定期检查。

Schema 名称的**使用优先级**（选择哪个 Schema）：

```
1. CLI 显式参数   /opsx:new my-feature --schema my-schema
2. Change 元数据  openspec/changes/<feature>/.openspec.yaml
3. config.yaml   schema: spec-driven
4. 默认          spec-driven
```

---

## 四、多 Schema 最佳实践

### 4.1 按任务类型选择 Schema

| 任务类型 | 推荐 Schema | 理由 |
|----------|------------|------|
| 新功能开发 | `aisee-app-spec-driven` | 承接 SRS / UI Content / Architecture，并细化 UI、服务和数据契约 |
| 普通 Bug Fix | `aisee-app-spec-driven` 或 `quick-fix` | 涉及契约或跨模块影响时走 app schema；单点低风险修复走 quick-fix |
| 小修复 / 紧急 Hotfix | `quick-fix`（自定义） | 只保留问题、方案、任务和验证证据，避免为低风险修复引入重流程 |
| PR Code Review | `opsx-collab-pr-loop` | 以外部输入为驱动 |
| 技术调研 | `opsx-collab-pr-loop` 或 `quick-research` | 无需完整实现流程 |
| 安全相关变更 | `security-audit`（自定义） | 增加威胁模型文档 |
| 基础设施变更 | `infra-change`（自定义） | 增加影响评估和回滚方案 |

---

### 4.2 Schema 文件管理规范

**目录结构要求**：

```
openspec/schemas/
├── opsx-collab-pr-loop/     ← 所有团队共享 Schema 放这里
│   ├── schema.yaml
│   └── templates/
└── quick-fix/               ← 每个 Schema 独立目录
    ├── schema.yaml
    └── templates/
```

**强制要求**：
- 所有 `openspec/schemas/` 下的文件必须提交到 Git
- Schema 新增或修改须走 PR + Tech Lead Review，不得直接 push to main
- Schema 变更合并后通知团队

---

### 4.3 Schema 命名约定

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 任务类型 | `<task-type>` | `quick-fix`、`research` |
| 协作流程 | `opsx-<pattern>-<flow>` | `opsx-collab-pr-loop` |
| 领域专用 | `<domain>-<type>` | `security-audit`、`infra-change` |
| Fork 修改版 | `<original>-<suffix>` | `spec-driven-extended` |

**禁止**：使用与官方内置 Schema 相同的名字（如 `spec-driven`），除非明确意图覆盖它。

---

### 4.4 减少 Delta Spec 逻辑冲突

**原则**：并行的 Change 尽量操作 `openspec/specs/` 的不同领域文件或不同需求段落。

```
推荐：
  feature-a → specs/auth/spec.md（MODIFIED: Session Timeout）
  feature-b → specs/payments/spec.md（ADDED: Checkout V2）
  → Archive 时无冲突

避免：
  feature-a → specs/auth/spec.md（MODIFIED: Session Timeout）
  feature-b → specs/auth/spec.md（MODIFIED: Session Timeout）
  → Archive 时报冲突
```

**遇到冲突时的处理流程**：

```
/opsx:bulk-archive 报冲突
  ↓
确认哪两个 Change 的 Delta 在修改同一需求
  ↓
Spec Owner 之间沟通，确定最终目标值
  ↓
其中一方修改 Delta（MODIFIED → ADDED，或调整值）
  ↓
再次执行 /opsx:bulk-archive
```

---

### 4.5 补齐自定义 Schema 的 rules 覆盖

对于 artifact ID 与 `config.yaml rules` 不匹配的自定义 Schema，在 `schema.yaml` 中用 `instruction` 字段补充约束：

```yaml
# openspec/schemas/opsx-collab-pr-loop/schema.yaml

artifacts:
  - id: intake
    generates: loop/intake.md
    description: "接收 PR/问题，理解背景"
    template: intake.md
    requires: []
    instruction: |
      # 团队规范（等同于 config.yaml rules.proposal）
      - 明确说明问题来源（PR 链接 / Issue 编号）
      - 标注影响范围和受影响的团队
      - 写清楚期望的处理结论

  - id: research-plan
    generates: loop/research-plan.md
    description: "调研计划与方向"
    template: research-plan.md
    requires: [intake]
    instruction: |
      # 团队规范（等同于 config.yaml rules.specs）
      - 使用 Given/When/Then 格式描述验证场景
      - 至少覆盖 2 个边界 case
```

---

### 4.6 废弃 Schema 的流程

```bash
# 1. 确认没有 active change 在用该 Schema
openspec list --json | grep "schema-name"

# 2. 在 schema.yaml 中标注废弃
# description: "[DEPRECATED 2026-06-01] 请使用 spec-driven 替代"

# 3. 通知团队，3 个月后彻底删除
# rm -rf openspec/schemas/deprecated-schema-name/
```

---

## 五、日常调试命令

```bash
# 确认某个 Schema 的实际来源（是项目本地、全局还是官方内置）
openspec schema which spec-driven
openspec schema which --all

# 验证 Schema 格式是否正确（CI 集成前必跑）
openspec schema validate my-schema

# 检查某个 Change 用的是哪个 Schema
openspec show <change-name>

# 查看某个 artifact 实际收到的 instruction（调试 rules 是否生效）
openspec instructions proposal --change my-feature

# 检查并行 Change 之间是否有 Delta 冲突（归档前运行）
openspec validate my-feature --strict
```

---

## 六、快速决策树

```
需要新建 Change？
  ↓
这个任务类型有专用 Schema 吗？
  ├── 有 → 使用 /opsx:new "name" --schema <schema-name>
  └── 没有 → 使用 /opsx:new "name"（默认 spec-driven）

有多个并行 Change 要归档？
  ↓
运行 openspec validate --strict 检查每个 Change
  ├── 无冲突 → /opsx:bulk-archive
  └── 有冲突 → 找到冲突的 MODIFIED 操作 → Spec Owner 沟通 → 修改 Delta → 重试

新建自定义 Schema？
  ├── 基于已有 Schema 修改 → openspec schema fork spec-driven my-schema
  ├── 从零开始 → openspec schema init my-schema
  └── 验证格式 → openspec schema validate my-schema
       └── 提交 PR → Tech Lead Review → merge → 通知团队
```

---

*文档基于 OPENSPEC_SCHEMA_GUIDE.md 与 OPENSPEC_ADVANCED.md 整理。最后更新：2026-04-20*
