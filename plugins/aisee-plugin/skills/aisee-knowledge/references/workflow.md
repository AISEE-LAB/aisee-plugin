# Team Knowledge CLI Workflow

## 1. Inspect

检查当前项目是否已接入团队知识：

```bash
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
```

使用原则：

- `inspect` 看配置、packs 和 cards。
- `doctor` 看 `aisee/knowledge.yaml` 与本地路径是否一致。
- `check` 校验 pack/card，并返回 `team_knowledge.write_ready`。

## 2. Initialize And Configure

新建独立 team knowledge 仓库骨架：

```bash
aisee knowledge init-repo --dest <team-knowledge> --initial-pack web-app --json
aisee knowledge check --team-path <team-knowledge> --json
aisee knowledge configure --path <team-knowledge> --enable-pack web-app --json
aisee knowledge doctor --json
```

如果团队已有外部 Git 仓库，业务项目只 pin repo/ref/path：

```bash
aisee knowledge configure \
  --path .aisee/team-knowledge \
  --repo <git-url> \
  --ref <branch-or-tag> \
  --enable-pack web-app \
  --json
```

随后运行 `install` clone 到配置路径。

## 3. Sync

同步已配置的 Git team knowledge checkout：

```bash
aisee knowledge install --json
aisee knowledge update --json
```

边界：

- `install` 只 clone `aisee/knowledge.yaml` 中声明的 repo/path/ref。
- `update` 会拒绝 dirty checkout，除非用户明确选择 `--allow-dirty`。
- 失败时报告 issue code，不自动删除用户已有 worktree。

## 4. Query

直接按场景检索：

```bash
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
```

基于当前 OpenSpec change 检索：

```bash
aisee knowledge query --from-change <change> --for ce-work --json
```

给执行上下文注入少量 guardrails：

```bash
aisee context pack --change <change> --for ce-work --knowledge --json
```

读取结果时看：

- `knowledge.matches`：可使用的 active cards。
- `knowledge.explain`：被过滤原因，如 `status is candidate`。
- `config.retrieval.max_cards`：默认返回数量上限。

## 5. Index

索引只是可删除 cache，不是事实源：

```bash
aisee knowledge index --json
aisee knowledge index --team-path <team-knowledge> --json
```

项目侧 cache 默认写入 `aisee/cache/knowledge-index.json`；team repo cache 默认写入 `indexes/lexical-index.json`。

## 6. Promote Reviewed Drafts

如果用户还没有 curation report，先转交 `aisee:knowledge-curate` 生成审查报告和 card drafts。

已有 curation report 且用户明确授权写入本地 team knowledge worktree 后：

```bash
aisee knowledge check --team-path <team-knowledge> --json
aisee knowledge promote-batch \
  --curation <report> \
  --team-path <team-knowledge> \
  --pack web-app \
  --json
```

激活规则：

- 默认不传 `--activate`，写入 `candidate`。
- 只有用户明确说“激活 / active / 直接启用”时才传 `--activate`。
- `promote-batch` 不会 commit、push 或创建 PR。
