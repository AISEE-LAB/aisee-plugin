# Reflect 可复用知识候选

本文维护 `aisee:reflect` 的跨项目复用判断、去敏要求，以及与 Compound `docs/solutions/` 的边界。只有用户要求跨项目复用、避免重复犯错，或复盘中出现可泛化经验时读取。

## 与 Compound 知识沉淀的边界

```text
ce-compound = 具体已解决工程问题的 solution
aisee:reflect = 会话复盘、memory 候选、skill/workflow 改进、跨项目复用候选
```

路由规则：

- 用户说“把刚才这个 bug/问题的解决方案记录下来” -> 建议 `ce-compound`。
- 用户说“复盘这次会话、沉淀经验、以后别再犯、优化 skill/workflow” -> 使用 `aisee:reflect`。
- 用户说“这个经验能不能跨项目复用” -> 使用 `aisee:reflect` 生成 reusable knowledge candidate。
- 用户说“清理/审查已有 solutions 是否过期” -> 建议 `ce-compound-refresh`。

Reflect 可以引用 `docs/solutions/...` 作为证据来源，但不要复制或改写同一 solution 内容。

## 可复用知识候选判断

适合作为 reusable knowledge candidate 的信号：

- 不是当前项目专有，其他项目在相同技术栈、框架、schema、工作流或错误类型下也可能受益。
- 可以明确写出 `applies_to`，例如 stacks、surfaces、phases、schemas。
- 可以写出触发条件，而不是泛泛经验。
- 已经去除项目私密信息、业务敏感信息、客户名称、内部 URL、token、路径中的秘密信息。
- 有证据来源，例如 reflect 文档、`docs/solutions/...`、review 结论、测试失败或已验证修复。

每条至少包含可转成 knowledge card 的必填机器字段：

- 候选 ID。
- 标题。
- 适用范围。
- 触发条件。
- 推荐动作。
- 不适用边界。

证据来源、风险类型、tags 和去敏检查属于 review 信息，不是 active card 的硬必填字段。后续 `aisee:knowledge-curate` 可以用这些信息批量审查、泛化和去重。

如果候选来自具体已解决问题，不复制 solution 正文；引用 `docs/solutions/...` 或建议先运行 `ce-compound`。

## Compound Solution Follow-up

适合建议 `ce-compound` 的信号：

- 本次会话刚解决了一个具体 bug、构建失败、测试失败、集成问题或工程排查问题。
- 已有清晰症状、根因、修复方式和预防措施。
- 该内容更像 solution 文档，而不是偏好、workflow fix、skill patch 或跨项目知识卡。

输出 follow-up，而不是在 reflect 中重写 solution：

```text
Suggested follow-up: run ce-compound for the concrete solution.
```

## 写入位置

路径：

```text
aisee/docs/reflect/knowledge-candidates/YYYY-MM-DD_<slug>.md
```

## 模板

````markdown
# Reusable Knowledge Candidate: <title>

_Date: YYYY-MM-DD_
_Status: candidate_

## Card Draft

```yaml
id: <kebab-case-id>
title: <title>
status: candidate
applies_to:
  stacks: []
  frameworks: []
  phases: []
  schemas: []
  surfaces: []
trigger:
  - <observable condition>
recommended_action:
  - <actionable rule>
boundaries:
  - <when this should not be applied>
```

## Review Info

```yaml
risk_types: []
tags: []
evidence:
  - type: reflect | solution | review | test
    repo:
    path:
```

## Problem

<what agents or developers tend to get wrong>

## Generalization Notes

<what project-specific details were removed or generalized>

## Sensitive Information Check

- [ ] No secrets, tokens, cookies, production credentials, customer data, or private URLs.
- [ ] Project-specific names have been generalized or explicitly marked project-only.
- [ ] The candidate is not copied from a solution doc; it references the solution if needed.

## Curate Follow-up

Suggested follow-up: run `aisee:knowledge-curate` when there are enough reusable candidates for batch review.
````

Reusable knowledge candidates remain project-local review assets. They do not automatically enter global knowledge, user home memory, other projects, active skills, or `aisee-team-knowledge`.
