# Aisee Harness 设计

## 目标

Aisee harness 是开发者侧的质量保障设施，用来验证 CLI 契约、skill 行为和工作流场景。它不是用户工作流步骤，不是 OpenSpec artifact，也不是运行时事实源。

Harness 设计分三层：

- **CLI Contract Harness**：验证 JSON 结构、退出码、命令元数据、读写边界是否稳定。
- **Skill Eval Harness**：评估 skill 是否遵守职责、是否提出必要澄清、是否避免禁止输出、是否保持事实源边界。
- **Workflow Scenario Harness**：通过代表性项目 fixture 验证 Aisee、OpenSpec 和 CE 的阶段衔接。

## 非目标

Harness 不应该：

- 成为新的 OpenSpec schema 或 artifact 类型；
- 作为正常工作流的一部分写入或修改用户项目；
- 决定 change 是否可以 archive；
- 替代 `openspec validate`、`aisee doctor` 或 `aisee context pack`；
- 成为 agent 编排层。

## 分层

### CLI Contract Harness

当前实现：`tests/` 下的 `pytest` 测试。

检查范围：

- 命令退出码；
- `status`、`issues`、`summary`、`meta.command`、`writes` 等 JSON 字段；
- 只读命令保持只读；
- cache 标记为可重建且不是事实源；
- 缺少子命令时返回可消费的 JSON 错误；
- `aisee doctor` 能报告 OpenSpec 和 Compound 可用性。

fixture 应保持小而本地化；只有多个场景复用时才提取为共享 fixture。

### Skill Eval Harness

当前实现：`skills/<skill>/evals/evals.json`。

这些 eval 文件是场景定义，还不是自动 runner 的强契约。它们应该足够结构化，方便未来 runner 在不重写 case 的前提下消费。

Skill eval 重点检查：

- skill 是否停留在自身职责内；
- 是否提出必要澄清问题；
- 是否避免禁止 artifact 或实现细节；
- 是否保持 Aisee/OpenSpec 事实源边界；
- 交接建议是否兼容当前 schema 和 CLI 规则。

### Workflow Scenario Harness

未来 fixture 目录建议：

```text
tests/fixtures/projects/
  uninitialized/
  app-context-ready/
  app-change-authored/
  app-implementation-ready/
  app-implemented-missing-evidence/
  app-archive-ready/
```

Workflow fixture 只验证阶段转换和上下文交接，不测试 AI 文案质量。

## Skill Eval Case Schema

Skill eval 文件应使用下面的结构，同时保留 `prompt` 和 `expected_output` 以兼容已有内容：

```json
{
  "schema_version": "aisee.skill-eval.v1",
  "skill_name": "aisee:srs",
  "harness": {
    "type": "skill-eval",
    "owner": "aisee",
    "fact_source_policy": "eval cases are test inputs, not runtime facts"
  },
  "evals": [
    {
      "id": "srs-001",
      "name": "ui-heavy-admin-feature",
      "scenario": "new-app | enhancement | migration | device-boundary | review",
      "prompt": "面向 skill 的真实用户请求。",
      "context": {
        "files": [],
        "assumptions": []
      },
      "expected_output": "兼容旧 eval 的简要预期。",
      "expected_outputs": [
        "可评分的具体预期行为。"
      ],
      "must_ask": [
        "skill 必须提出的澄清问题或缺失决策。"
      ],
      "must_include": [
        "必须出现的章节、标记、追踪关系或交接提示。"
      ],
      "must_not": [
        "禁止输出的 artifact、行为或未确认假设。"
      ],
      "quality_checks": [
        "可审查的质量标准。"
      ],
      "fact_source_constraints": [
        "避免平行事实源或不受支持来源的规则。"
      ],
      "files": []
    }
  ]
}
```

字段规则：

- `id` 使用稳定字符串，不只用序号。
- `prompt` 应接近真实用户请求。
- `expected_output` 是向后兼容的简要总结。
- `expected_outputs` 是未来 runner 可评分的结构化检查清单。
- 当场景包含范围、业务规则、架构、平台、证据或迁移决策缺口时，必须填写 `must_ask`。
- `must_not` 必须覆盖该 skill 最容易越界的 artifact 或行为。
- `fact_source_constraints` 应在相关场景中说明 OpenSpec、Aisee docs、ID registry、source-map 或 CLI JSON 的边界。

## Runner 策略

当前不构建重型 runner。

近期策略：

1. CLI harness 继续使用 `pytest`。
2. 逐步规范高价值 skill 的 eval 文件。
3. 等足够多 eval 文件采用该 schema 后，再增加静态 JSON 校验。

后续可选：

1. 增加小型 eval linter，检查必填字段和稳定 ID。
2. 可选增加模型评分，检查 `expected_outputs`、`must_include` 和 `must_not`。
3. 模型评分只作为审查建议，不能写项目事实，也不能批准 archive。

## 归属

- CLI harness：`tests/`。
- Skill eval harness：`skills/<skill>/evals/`。
- Workflow scenario harness：未来的 `tests/fixtures/projects/`。
- Harness 设计：本文档。

