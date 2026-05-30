# AI Coding Spec 开发范式与 OpenSpec 自定义 Schema 指南（更新版）

> 本文档整合了围绕 AI Coding、Web App / 小程序开发材料体系、业务型 SRS、OpenSpec change 生命周期、自定义 schema 设计，以及 skill 职责拆分的完整讨论。  
> 核心目标是：既保留业务需求表达，又避免在 OpenSpec change 之前生成过重、重复的技术文档。

---

## 1. 背景与目标

在 AI Coding 项目中，尤其是 Web App / 小程序开发过程中，我们通常会生成大量材料，例如：

- SRS
- UI Content
- 设计规范
- 数据库设计
- 接口设计
- 任务拆解
- 验收标准
- 测试用例

这些材料可以帮助 AI 更稳定地生成代码，但如果文档生命周期设计不清晰，就容易出现重复。

当前讨论的核心问题是：

> 在基于 OpenSpec 做项目管理，并设计自定义 schema 的情况下，是否应该在创建 change 之前先生成完整 SRS、UI Content、接口设计、数据库设计等材料？

最终建议是：

> **业务型 SRS 可以保留，但不建议在 change 前生成完整技术型 SRS / UI Content / API / DB 文档。**  
> **change 前只做业务理解和 change 拆分；详细技术规格放到每个 change 内；change 完成后再沉淀为 baseline specs。**

---

## 2. 你的当前意图

你的目标并不是简单地产生一堆文档，而是希望形成一套适合 AI Coding 的项目管理和规格生成范式：

1. 基于 OpenSpec 管理项目需求、变更和系统规格。
2. 针对 Web App / 小程序开发，沉淀一套可复用的 spec 材料体系。
3. 通过自定义 schema 规范 AI 生成的材料格式。
4. 通过 skill 自动完成需求理解、change 拆分和 change authoring。
5. 减少重复文档，避免 SRS、UI Content、proposal、design、spec delta 之间互相重叠。
6. 最终让 AI 在编码时有明确的业务边界、页面结构、接口契约、数据模型、验收标准和禁止事项。

---

## 3. 关键判断：业务型 SRS 应该保留

如果 SRS 只描述业务，不涉及技术，那么它不应该被取消。

业务型 SRS 的价值是：

- 描述业务目标
- 描述用户角色
- 描述业务流程
- 描述业务规则
- 描述业务范围和非目标
- 作为 change split skill 的上游输入
- 帮助所有 change 保持业务一致性

但它不应该承担技术设计职责。

### 3.1 业务型 SRS 应该写什么

业务型 SRS 建议包含：

```text
# Business SRS

1. 业务背景
2. 目标用户 / 角色
3. 业务目标
4. 业务范围
5. 业务能力列表
6. 核心业务流程
7. 业务规则
8. 权限与角色规则
9. 非目标范围
10. 优先级 / MVP 范围
11. 待确认问题
```

### 3.2 业务型 SRS 不应该写什么

业务型 SRS 不建议包含：

```text
- 页面结构
- 页面区块
- 组件拆分
- 接口 path
- 请求响应字段
- 数据库表字段
- 前端状态管理
- 技术栈细节
- 代码目录结构
- 开发任务步骤
```

这些内容应该进入 change 内部的 spec delta 和 design 文档。

### 3.3 示例边界

业务型 SRS 可以写：

```text
用户可以通过手机号验证码登录系统。
验证码 5 分钟内有效。
同一手机号 60 秒内只能发送一次验证码。
登录后用户可以访问个人中心和创建订单。
```

但不建议写：

```text
登录页包含手机号输入框、验证码输入框、发送验证码按钮、登录按钮。
POST /api/auth/login 接口接收 phone 和 code。
users 表包含 id、phone、nickname、avatar_url 字段。
```

后者属于 page spec、api spec 和 data model / database table spec。

---

## 4. 文档重复的根本原因

当前容易重复的原因是：

```text
change 之前已经生成完整 SRS / UI Content / API / DB
↓
change 中又要生成 proposal.md / design.md / tasks.md / spec delta
↓
同一批信息被重复描述
```

典型重复关系如下：

```text
SRS            ≈ capability spec / proposal / acceptance
UI Content     ≈ page spec / interaction spec / design
接口设计        ≈ api spec delta
数据库设计      ≈ data model / database table delta
设计规范        ≈ design-system / component spec
```

因此，不是材料不重要，而是它们被放在了错误的生命周期里。

---

## 5. 推荐的整体范式

最终推荐范式是：

```text
Business SRS
↓
Intake / Planning
↓
Change Plan
↓
OpenSpec Change Authoring
↓
Spec Delta
↓
Implementation
↓
Acceptance
↓
Baseline Specs
```

一句话总结：

> **change 前保留业务蓝图和规划材料；change 内生成详细技术规格；change 后沉淀为系统基线。**

---

## 6. Change 前、中、后的材料分工

### 6.1 Change 前：Planning / Intake

change 前只生成轻量材料：

- Business SRS
- intake brief
- change plan

change 前不要生成完整技术材料：

- 不生成完整 UI Content
- 不生成完整 API Design
- 不生成完整 Database Design
- 不生成完整 Component Spec
- 不生成完整 Task Breakdown

这一阶段的目标是：

```text
理解需求
识别业务边界
识别非目标
识别风险和不确定点
拆分 change
定义 change 依赖
```

### 6.2 Change 中：Authoring

每个 change 内生成详细内容：

```text
changes/{change-id}/
  proposal.md
  design.md
  tasks.md
  specs/
    capabilities/
    pages/
    components/
    apis/
    data-models/
    database-tables/
    permissions/
    state-machines/
    acceptance/
```

其中：

- proposal.md：说明这个 change 为什么做、做什么、不做什么
- design.md：说明这个 change 怎么做、影响哪些系统对象、有哪些设计取舍
- tasks.md：说明实现步骤
- spec delta：说明这个 change 对系统事实的增量修改

### 6.3 Change 后：Baseline Specs

change 实现并验收后，将 spec delta 合并到 baseline specs：

```text
openspec/specs/
  capabilities/
  pages/
  components/
  apis/
  data-models/
  database-tables/
  permissions/
  state-machines/
  acceptance/
```

baseline specs 表示当前系统事实，供后续 change 和 AI Coding 参考。

---

## 7. 是否需要先把所有 change 写完再实现

不建议一开始把所有 change 都写到非常详细再实现。

更推荐：

```text
全局规划，分批细化，逐步实现
```

也就是：

```text
1. 先写 Business SRS
2. 生成全局 change plan
3. 确定 MVP / 第一批 change
4. 只详细 author 当前批次 change
5. 实现、验收、合并 baseline specs
6. 再 author 下一批 change
```

原因是：

- 后续 change 可能会因前面实现结果而变化
- 一开始细化所有技术设计容易浪费
- AI Coding 更适合小步、可验证、可回滚地推进
- OpenSpec 的优势就在于变更驱动，而不是一次性写完所有系统规格

---

## 8. 推荐流程

### 8.1 完整流程

```text
1. 编写 Business SRS
   - 只描述业务目标、业务能力、业务流程、业务规则、非目标

2. 生成 Intake Brief
   - 描述原始意图、初步范围、风险、不确定点

3. 使用 change split skill 拆分 Change Plan
   - 拆出 change 列表
   - 标注依赖关系
   - 标注优先级
   - 标注每个 change 涉及哪些 artifact

4. 选择 MVP / 当前批次 Change

5. 使用 change authoring skill 生成 change 详细内容
   - proposal.md
   - design.md
   - tasks.md
   - capability delta
   - page delta
   - api delta
   - data-model delta
   - component delta
   - state-machine delta
   - acceptance delta

6. 执行开发

7. 验收 change

8. 合并 spec delta 到 baseline specs

9. 进入下一批 change
```

### 8.2 简化流程

```text
Business SRS
↓
Change Plan
↓
Current Batch Changes
↓
Implementation
↓
Acceptance
↓
Baseline Specs
```

---

## 9. 文档职责对照表

| 文档 | 生命周期 | 作用 | 是否长期维护 |
|---|---|---|---|
| Business SRS | change 前 | 描述业务目标、业务能力、业务流程、业务规则 | 是 |
| project-context.md | 全局 | 描述产品、平台、技术栈、团队约定 | 是 |
| coding-rules.md | 全局 | 约束 AI 如何写代码 | 是 |
| design-system.md | 全局 / change delta | 全局视觉和组件规范 | 是 |
| intake.md | change 前 | 理解需求、拆分输入 | 通常否 |
| change-plan.md | change 前 | 拆分 change、定义依赖 | 可选保留 |
| proposal.md | change 中 | 定义单个 change 的目标、范围、非目标 | 是，作为变更记录 |
| design.md | change 中 | 解释实现方案、设计取舍、影响范围 | 是，作为变更记录 |
| tasks.md | change 中 | 指导开发执行 | 是，直到完成 |
| capability spec | change delta / baseline | 描述系统能力事实 | 是 |
| page spec | change delta / baseline | 描述页面结构、状态、内容和行为 | 是 |
| component spec | change delta / baseline | 描述组件契约和复用规则 | 是 |
| api spec | change delta / baseline | 描述接口契约 | 是 |
| data model spec | change delta / baseline | 描述业务实体 | 是 |
| database table spec | change delta / baseline | 描述物理表结构 | 是 |
| permission spec | change delta / baseline | 描述角色、权限、数据范围 | 是 |
| state machine spec | change delta / baseline | 描述状态流转和副作用 | 是 |
| acceptance criteria | change / baseline | 描述验收标准 | 是 |
| test cases | change / baseline | 描述测试覆盖 | 是 |

---

## 10. SRS、UI Content、API、DB 的新定位

### 10.1 SRS 的新定位

原来的 SRS 如果只描述业务，可以保留为：

```text
business-srs.md
```

或者：

```text
business-requirements.md
```

它是 change 拆分的业务蓝图。

技术型的功能规格应拆为：

```text
capability spec
acceptance criteria
```

### 10.2 UI Content 的新定位

不要在 change 前生成完整 ui-content.md。

可以改为：

```text
page spec
interaction spec
copy spec
```

对于简单项目：

```text
page spec = UI Content + 页面状态 + 页面行为
```

对于复杂项目：

```text
page spec：页面结构、区块、数据来源
interaction spec：交互、弹窗、表单、Toast
copy spec：文案风格和具体文案
```

### 10.3 API 设计的新定位

API 设计应作为 change 内的 api spec delta：

```text
changes/{change-id}/specs/apis/*.md
```

完成后合并到：

```text
openspec/specs/apis/*.md
```

### 10.4 数据库设计的新定位

数据库设计应拆为：

```text
data model spec
database table spec
```

在 change 内作为 delta 出现：

```text
changes/{change-id}/specs/data-models/*.md
changes/{change-id}/specs/database-tables/*.md
```

完成后合并到 baseline。

---

## 11. 推荐 OpenSpec 目录结构

```text
openspec/
  project-context.md
  business-srs.md
  coding-rules.md
  design-system.md

  schemas/
    planning/
      intake-brief.schema.yaml
      change-plan.schema.yaml

    specs/
      capability.schema.yaml
      page.schema.yaml
      component.schema.yaml
      api.schema.yaml
      data-model.schema.yaml
      database-table.schema.yaml
      permission.schema.yaml
      state-machine.schema.yaml
      acceptance.schema.yaml
      task.schema.yaml

  specs/
    capabilities/
    pages/
    components/
    apis/
    data-models/
    database-tables/
    permissions/
    state-machines/
    acceptance/

  intake/
    2026-05-30-user-auth-and-order.md

  changes/
    add-user-auth/
      proposal.md
      design.md
      tasks.md
      specs/
        capabilities/
          user-auth.md
        pages/
          login-page.md
        apis/
          auth-send-code.md
          auth-login.md
        data-models/
          user.md

    add-product-browsing/
      proposal.md
      design.md
      tasks.md
      specs/
        capabilities/
          product-browsing.md
        pages/
          home-page.md
          product-detail-page.md
        apis/
          product-list.md
          product-detail.md
        data-models/
          product.md
```

---

## 12. 推荐 Schema 分类

### 12.1 Planning Schema

用于 change 前的轻量规划材料。

#### intake-brief.schema

```yaml
id:
title:
raw_intent:
business_goal:
target_users:
scenarios:
initial_scope:
non_goals:
constraints:
risks:
open_questions:
suggested_changes:
```

#### change-plan.schema

```yaml
id:
source_intake:
changes:
  - id:
    title:
    goal:
    reason:
    scope:
    non_goals:
    dependencies:
    priority:
    affected_artifacts:
      capabilities:
      pages:
      apis:
      data_models:
      database_tables:
      components:
      permissions:
      state_machines:
    acceptance_focus:
```

### 12.2 Spec Schema

用于 change 内和 baseline specs。

建议包括：

```text
capability.schema
page.schema
component.schema
api.schema
data-model.schema
database-table.schema
permission.schema
state-machine.schema
acceptance.schema
task.schema
```

---

## 13. 核心 Artifact Schema 示例

### 13.1 Capability Spec

```yaml
id: CAP-AUTH-001
name: 用户登录
status: active
priority: P0
actors:
  - visitor
related_pages:
  - PAGE-LOGIN
related_apis:
  - API-AUTH-LOGIN
related_models:
  - MODEL-USER
rules:
  - 手机号必须通过验证码验证
  - 验证码 5 分钟内有效
non_goals:
  - 不支持微信一键登录
  - 不支持邮箱登录
acceptance:
  - AC-AUTH-001
```

### 13.2 Page Spec

```yaml
id: PAGE-LOGIN
name: 登录页
route: /pages/login/index
platform:
  - miniapp
auth_required: false
entry_from:
  - 首页
  - 我的页
blocks:
  - id: phone-input
    type: form-field
    content: 手机号输入框
    data_source: local.form.phone
  - id: code-input
    type: form-field
    content: 验证码输入框
    data_source: local.form.code
  - id: submit-button
    type: button
    text: 登录
    action: submit_login
states:
  loading: 显示按钮 loading
  empty: 不适用
  error: Toast 展示错误信息
  unauthorized: 不适用
related_apis:
  - API-AUTH-SEND-CODE
  - API-AUTH-LOGIN
```

### 13.3 Component Spec

```yaml
id: CMP-PRODUCT-CARD
name: ProductCard
type: business
used_by:
  - PAGE-HOME
  - PAGE-SEARCH
props:
  productId:
    type: string
    required: true
  title:
    type: string
    required: true
  imageUrl:
    type: string
    required: true
  price:
    type: number
    required: true
events:
  click:
    description: 跳转商品详情页
style_rules:
  - 图片比例 1:1
  - 标题最多展示两行
  - 价格使用主题色
```

### 13.4 API Spec

```yaml
id: API-AUTH-LOGIN
name: 用户登录
method: POST
path: /api/auth/login
auth_required: false
request:
  phone:
    type: string
    required: true
  code:
    type: string
    required: true
response:
  token:
    type: string
  user:
    $ref: MODEL-USER
errors:
  - code: INVALID_CODE
    message: 验证码错误
  - code: CODE_EXPIRED
    message: 验证码已过期
related_pages:
  - PAGE-LOGIN
```

### 13.5 Data Model Spec

```yaml
id: MODEL-USER
name: 用户
description: 系统中的注册用户
fields:
  id:
    type: string
  phone:
    type: string
  nickname:
    type: string
  avatarUrl:
    type: string
states:
  status:
    values:
      - active
      - disabled
related_tables:
  - users
```

### 13.6 Database Table Spec

```yaml
table: users
columns:
  id:
    type: varchar(36)
    primary_key: true
  phone:
    type: varchar(20)
    unique: true
    nullable: false
  nickname:
    type: varchar(50)
  created_at:
    type: datetime
indexes:
  - name: idx_users_phone
    columns:
      - phone
```

### 13.7 Permission Spec

```yaml
id: PERM-ORDER
resource: order
roles:
  visitor:
    can:
      - browse_products
    cannot:
      - create_order
      - view_order
  user:
    can:
      - create_order
      - view_own_order
    data_scope: own
  admin:
    can:
      - view_all_orders
      - update_order_status
    data_scope: all
```

### 13.8 State Machine Spec

```yaml
id: SM-ORDER
entity: order
field: status
states:
  - pending_payment
  - paid
  - shipped
  - completed
  - cancelled
  - refunded
transitions:
  - from: pending_payment
    to: paid
    trigger: payment_success_callback
    actor: system
    side_effects:
      - create_payment_record
      - reduce_stock
      - notify_user
  - from: pending_payment
    to: cancelled
    trigger: user_cancel_order
    actor: user
```

### 13.9 Acceptance Spec

```yaml
id: AC-AUTH-001
capability: CAP-AUTH-001
scenario: 手机号验证码登录成功
given:
  - 用户未登录
  - 手机号已获取有效验证码
when:
  - 用户输入手机号和验证码
  - 用户点击登录按钮
then:
  - 系统返回 token
  - 前端保存登录态
  - 页面跳转到来源页
test_cases:
  - TC-AUTH-001
```

---

## 14. Skill 职责拆分建议

你现在已经有一个 change 拆分 skill。建议进一步拆成三个 skill，职责更清晰。

### 14.1 需求 Intake Skill

输入：

```text
用户原始需求
项目上下文
当前 specs
```

输出：

```text
intake.md
```

职责：

```text
理解意图
识别范围
识别非目标
识别不确定点
```

### 14.2 Change Split Skill

输入：

```text
intake.md
business-srs.md
当前 specs
项目规则
```

输出：

```text
change-plan.md
```

职责：

```text
拆分 change
定义依赖
判断每个 change 涉及哪些 artifact
判断 change 粒度是否合适
```

### 14.3 Change Authoring Skill

输入：

```text
change-plan 中的某个 change
当前 specs
项目 schema
```

输出：

```text
proposal.md
design.md
tasks.md
spec deltas
```

职责：

```text
生成 OpenSpec change 目录
生成 proposal
生成 design
生成 tasks
生成对应 spec delta
```

---

## 15. AI Coding 的核心原则

每份 spec 最好都包含：

```text
1. 要做什么
2. 不做什么
3. 怎么验收
```

示例：

```text
功能：商品搜索

要做：
- 用户可以输入关键词搜索商品
- 支持搜索结果分页
- 支持空状态和错误状态

不做：
- 不做搜索历史
- 不做热门搜索
- 不做语义搜索
- 不做筛选排序

验收：
- 输入关键词后展示结果
- 结果为空时展示空状态
- 接口失败时展示错误提示
- 下拉到底部时加载下一页
```

这比传统 PRD 更适合 AI Coding，因为它既规定目标，也规定边界和完成标准。

---

## 16. 最终结论

你的直觉是正确的：当前有些文档确实重复了。

原因不是 SRS、UI Content、API Design、Database Design 不重要，而是它们被放在了错误的阶段。

最终建议是：

```text
保留业务型 SRS
不要在 change 前生成完整技术设计
change 前只做 planning
change 内生成详细 spec delta
change 后合并 baseline specs
```

更具体地说：

```text
Business SRS：
描述业务目标、业务能力、业务流程、业务规则。

Change Plan：
描述需求应该拆成哪些 change、它们的依赖和优先级。

Proposal：
描述单个 change 的目标、范围和非目标。

Design：
描述单个 change 的实现方案和设计取舍。

Spec Delta：
描述单个 change 对系统事实的增量修改。

Baseline Specs：
描述当前系统已经具备的能力、页面、接口、数据、权限和状态机。
```

所以，你不是要减少文档，而是要重新安排文档生命周期。

最终范式可以概括为：

> **业务先行，变更驱动，规格沉淀，分批实现。**
