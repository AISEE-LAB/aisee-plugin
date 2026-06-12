# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 的结构，并使用 SemVer 管理版本。

## [0.10.0] - 2026-06-12

### Changed

- `aisee openspec ensure --json` 改为默认按当前 agent runtime 自动选择 OpenSpec `--tools`，在 Codex 下会安装或刷新项目目录内的 `.codex/skills`，不再默认走 `--tools none`。
- `aisee openspec ensure --json` 的初始化检测兼容新版 OpenSpec 目录结构；已有 `openspec/specs` 与 `openspec/changes` 的项目现在也能正确补装项目内 OpenSpec instructions / skills。
- `aisee openspec ensure --json` 的文档、help 和 workflow 说明统一明确：`openspec config profile` 只负责全局配置对齐，项目目录写入由 `openspec init/update` 完成。
- 版本治理说明收敛到 `CHANGELOG.md`、`docs/compatibility-policy.md` 与 `CONTRIBUTING.md`；删除 `docs/release.md`，并移除 `Unreleased` 段，避免双重维护和发布后漏改文档。

## [0.9.1] - 2026-06-11

### Added

- `aisee:design-assets` 新增素材生成前的 Asset Intent Scan、banner 文本策略、受控局部内容优化 prompt 与对应 eval 覆盖。
- `aisee:image-object` 新增透明素材 handoff、全局运行环境复用、GUI 预览缓存治理与对应 eval 覆盖。

### Changed

- `aisee:image-object` 主 skill 精简为轻量路由文档，详细 GUI、依赖、workflow 和 handoff 规则下沉到 references。
- `aisee:design-assets` 明确 Image2 / `gpt-image-2` 为参考图、视觉变体和生成型素材默认目标模型。

### Added

- `source-map.md` 新增 `intake_sources` 兼容路径，支持无 SRS / UI / Architecture 前置文档时记录精简 intake 来源。

### Changed

- `aisee context pack --for ce-work --json` 改为输出 lean execution brief，并移除 `ce-work` target 中的 artifact 正文副本。
- author / verify / implementation / flow 路径新增 schema metadata、schema mismatch 与 schema installed gate；缺 metadata 或仅有 plugin source 而未安装 schema 时会阻断执行。
- `aisee:change-plan`、`aisee:change-author`、`aisee:implementation-bridge`、`aisee:verify`、`aisee:archive-guard` 和 `aisee:flow` 明确自动消费只读 CLI JSON、intake 路径和 `aisee-schema-pack` 转交流程。
- app schema proposal / source-map 模板改为显式支持 `Intake 来源`，并避免伪造 SRS anchor。

## [0.6.0] - 2026-06-10

### Added

- CLI context pack traceability 新增 `intake_sources` 和 `mode`，区分 `anchor`、`intake`、`mixed`、`empty` 四种来源状态。
- `ce-work` target 新增 `facts.derived.execution.brief`，作为面向执行器的最小交接索引。

### Changed

- `upstream_refs=[]` 不再被误判为“没有来源”；只要存在 intake 来源和当前 change 产出 local IDs，即视为合法 traceability 路径。
- `aisee-app-spec-driven` 模板与相关 skill 规则改为支持无前置 planning docs 的 authoring 路径，并把 schema availability / metadata gate 提前到 planning 与 authoring 前置。
- 发布说明明确区分 PyPI CLI 合同与 marketplace plugin assets：PyPI 承载 CLI JSON 合同，plugin 承载 skills、references、schema pack assets 与模板。

## [0.5.0] - 2026-06-09

### Added

- 新增 skill taxonomy 合同与全量 skill eval 准入，固定 core 11、可选扩展、知识循环与硬件 / 实验域分层。

### Changed

- `aisee index --json` 与 `aisee doctor --json` 新增 planning doc lifecycle 只读诊断，覆盖缺失 frontmatter、无效状态和 stale active 风险。
- `resolve_project_root` 改为优先识别最近的 Aisee/OpenSpec project marker，再 fallback 到 Git 顶层，修复 monorepo / fixture 子项目误判。
- `scripts/smoke_release.py` 改为验证当前 CLI 命令面：CLI-only wheel、marketplace setup hint、`plugin export` invalid choice 和未创建目标目录。

## [0.4.0] - 2026-06-09

### Added

- 新增 `aisee knowledge init-repo` 和 `aisee knowledge configure`，用于初始化独立 team knowledge 仓库并写入业务项目侧 `aisee/knowledge.yaml`。

### Changed

- 为 `aisee knowledge promote-batch` 增加 `.aisee-team-knowledge` marker 和基础目录结构校验，避免误写业务项目根目录。
- 修正 marketplace bundled team knowledge template，使其与当前 card/pack contract 保持一致。

## [0.3.0] - 2026-06-09

### Changed

- 移除公开 CLI 中无单一 owner 的遗留内容分发入口：`aisee plugin export`、`aisee schemas install`、`aisee knowledge scaffold` 和 `aisee bootstrap --apply`。
- 将 Aisee reviewer 统一为只读 review lens，并把 Aisee reviewer evidence 与 CE review evidence 在 context pack 中分离。
- 为 planning docs 增加统一 YAML frontmatter 合同，并同步主要模板、技能文档、README、workflow 和兼容性文档。
- 将缺少 `id-registry.json` 调整为历史兼容状态，不再视为当前 authoring / lookup / traceability 的 blocker。

## [0.1.3] - 2026-06-08

### Changed

- 删除 README、贡献指南和发布文档中易过期的发布状态说明，避免 PyPI 长描述出现旧版本状态。
- 将兼容策略文档中的 `0.x` 规则保留为版本治理规则，不再标注为当前 pre-release 状态。

## [0.1.2] - 2026-06-08

### Changed

- 更新 README 和 PyPI metadata，增加 `https://aisee.wiki` 文档站入口。
- 将项目 Homepage 切换到文档站，并保留 GitHub Source 链接。

## [0.1.1] - 2026-06-08

### Changed

- 将 README 安装说明更新为正式 PyPI / pipx 公开安装指引。
- 将 README 语言切换链接改为仓库绝对链接，避免 PyPI 页面上的相对链接无法预览英文文档。

## [0.1.0] - 2026-06-08

### Added

- 初始 Aisee skills 工作流，覆盖 SRS、UI 内容规格、架构上下文、change planning、实现交接、verify、archive guard 和 reflect。
- OpenSpec schema pack，覆盖 app、device、docsite、infra、security、quick-fix、quick-research 和 collaboration 场景。
- Aisee CLI context bus，支持 doctor、bootstrap、OpenSpec 初始化桥接、schema pack 安装、context pack、ID registry、source-map、contract context 和 team knowledge 查询。
- 插件打包资源与多运行时 metadata，支持 Codex、Claude 和 Cursor 的 plugin export。
- 版本治理脚本，使用 `pyproject.toml` 作为唯一版本事实源，并同步 CLI 与 plugin metadata。
- 公开 README、workflow、best practices、release governance 和团队知识文档。
