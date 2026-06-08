---
name: aisee:knowledge-curate
description: 批量审查项目内 reusable knowledge candidates，把 reflect/solution/review/test 证据去敏、泛化、去重并整理成可提交到 aisee-team-knowledge 的 card drafts。用于用户明确要求“整理可复用知识”“提炼到团队知识”“curate knowledge”“准备团队知识 PR”“把候选经验批量审查”时触发。只产出审查报告和草稿；不自动写入 team repo、创建分支、提交、合并或 PR。
---

# aisee:knowledge-curate

## CLI preflight

调用 `aisee ...` 前先按 `references/cli-preflight.md` 确认 CLI 可用；team knowledge 模板位于本 skill 的 `assets/team-knowledge/` 或外部知识库，不来自 PyPI wheel。

批量审查项目内候选知识，产出可人工 review 的 team knowledge card drafts。

## 职责

- 读取项目内 `aisee/docs/reflect/knowledge-candidates/`。
- 按需读取相关 `docs/solutions/` frontmatter 或摘要证据。
- 去除项目私密信息、客户信息、内部 URL、secrets 和不可公开路径。
- 泛化候选，使其适用于相同技术栈、schema、phase、surface 或 risk 类型。
- 合并重复候选，标记 stale candidate。
- 输出 batch review report 和 card drafts。

## 不负责

- 不替代 `aisee:reflect`；reflect 负责生成项目内候选。
- 不替代 `ce-compound`；具体工程问题 solution 仍由 Compound 记录。
- 不复制 solution 正文。
- 不把 candidate 自动提升为 active card。
- 不自动写入 `aisee-team-knowledge`；用户授权后可以建议运行 `aisee knowledge promote-batch`。
- 不创建分支、commit、push、merge 或 PR，除非用户明确授权并提供 team repo 路径。
- 不让 team knowledge 覆盖 OpenSpec specs、tasks、contracts、source-map 或 baseline。

## Phase 0 — 扫描候选

扫描时遵守 `.gitignore`，优先使用 `rg --files`：

```bash
rg --files aisee/docs/reflect docs/solutions 2>/dev/null | rg 'knowledge-candidates|solutions|reflect'
```

如果没有 project-local candidates，只输出“没有可审查候选”，不要临时从聊天记录或全仓库生成 team card。

## Workflow

按需读取 references：

- 执行批量审查时读取 `references/workflow.md`。
- 生成正式 batch review report 时读取 `references/batch-review-template.md`。
- 需要确认 card 字段时读取 `references/knowledge-card-contract.md` 或项目根目录 `references/knowledge-card-contract.md`。

默认流程：

1. 收集候选文件和 evidence 引用。
2. 过滤一次性、项目专有或证据不足的候选。
3. 对剩余候选做去敏、泛化和边界补全。
4. 与已配置 team knowledge active cards 做概念去重；没有配置时只做项目内去重。
5. 生成 batch review report。
6. 仅当用户明确要求写文件时，写入 `aisee/docs/reflect/knowledge-curation/YYYY-MM-DD_<slug>.md`。

## Guardrails

- 默认只输出审查报告，不改 team repo。
- 写入 team repo 前必须再次确认用户授权和目标路径；优先使用 `aisee knowledge promote-batch --curation <path> --team-path <path> --pack <id> --json` 写入本地 worktree。
- `promote-batch` 不会创建分支、commit、push、merge 或 PR；这些 Git 动作仍需用户明确授权。
- 推荐 batch review：积累 3-10 条真实可复用候选后再提交。
- 安全、高风险或公开接口类候选可以建议单独 PR，但仍需用户授权。
- 每条 draft 必须包含 required machine fields：`id`、`title`、`status`、`applies_to`、`trigger`、`recommended_action`、`boundaries`。
- `evidence`、`risk_types`、`tags` 是 review 信息，不是 active card 硬必填。
- 最终回复列出候选数量、合并数量、拒绝数量、draft 数量、敏感信息风险和写入路径。
