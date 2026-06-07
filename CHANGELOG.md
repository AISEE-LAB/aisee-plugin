# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 的结构，并使用 SemVer 管理版本。

## [Unreleased]

### Added

- 暂无。

## [0.1.0] - 2026-06-08

### Added

- 初始 Aisee skills 工作流，覆盖 SRS、UI 内容规格、架构上下文、change planning、实现交接、verify、archive guard 和 reflect。
- OpenSpec schema pack，覆盖 app、device、docsite、infra、security、quick-fix、quick-research 和 collaboration 场景。
- Aisee CLI context bus，支持 doctor、bootstrap、OpenSpec 初始化桥接、schema pack 安装、context pack、ID registry、source-map、contract context 和 team knowledge 查询。
- 插件打包资源与多运行时 metadata，支持 Codex、Claude 和 Cursor 的 plugin export。
- 版本治理脚本，使用 `pyproject.toml` 作为唯一版本事实源，并同步 CLI 与 plugin metadata。
- 公开 README、workflow、best practices、release governance 和团队知识文档。
