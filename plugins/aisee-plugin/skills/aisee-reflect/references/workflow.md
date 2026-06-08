# Reflect 工作流

本文维护 `aisee:reflect` 的主流程、分类和路由。长模板见 `output-templates.md`；跨项目复用、可复用知识候选和 Compound 边界见 `knowledge-candidates.md`。

## Phase 1 — 收集信号

文件扫描必须遵守 `.gitignore`。优先使用 `rg --files`，因为它默认跳过 Git ignore 的文件；如果必须使用 `find`，要显式排除 `.git`、`node_modules`、`.venv`、`dist`、`build`、`.next`、`.cache`、临时目录和生成产物。不要把 ignored 文件、依赖包、构建输出或缓存内容沉淀为项目事实、memory 候选或技能证据。

关注以下信号：

- 用户目标：本次会话实际想完成什么。
- 重复流程：是否出现可固化为技能、脚本或检查清单的步骤。
- 纠错记录：模型哪里误判、遗漏、过度设计或输出格式不合适。
- 稳定偏好：用户明确或反复体现的语言、格式、验证、工具偏好。
- 项目事实：路径、命名、配置、约束、团队流程等可复用信息。
- 验证缺口：哪些测试、浏览器检查、命令或审查步骤应该补上。
- 具体解决方案：是否有刚解决的工程问题，应该交给 `ce-compound` 写入 `docs/solutions/`。
- 跨项目复用信号：是否有可去敏、可标注适用范围、可被其他项目按需检索的经验。

不要把一次性偶然事件写成长期规则。优先沉淀“未来再次发生时会节省时间或降低风险”的内容。

## Phase 2 — 分类判断

把发现归入以下类别；没有发现的类别不要输出。

### 新技能候选

适合沉淀为 skill 的信号：

- 形成了 4 步以上稳定流程。
- 用户未来很可能重复执行。
- 涉及特定领域、工具链、文档格式或团队规范。
- 现有技能无法覆盖，或覆盖后仍需要大量临场补充。

每条包含建议技能名、触发场景、核心流程、本次会话证据和不应覆盖的边界。

### 现有技能优化

适合写 skill patch 的信号：

- 技能触发描述不够明确，导致该用未用。
- 技能步骤遗漏关键检查、确认门或验证。
- 输出格式让用户反复纠正。
- 技能边界过宽或过窄。

每条包含技能名、问题、建议修改位置、替换或新增文本、预期收益与风险。

### Memory 候选

适合作为 memory 候选写入 reflect doc 的信号：

- 用户明确表达偏好或团队约定。
- 项目路径、命名、配置、流程被确认。
- 某个检查步骤被证明必要。
- 某个默认行为在本项目中应避免。

每条写成可执行规则，而不是观察记录。

### 可复用知识候选

当用户要求“跨项目复用 / 以后其他项目也用 / 避免重复犯错”，或复盘中出现可泛化经验时，读取 `knowledge-candidates.md` 并按其中规则判断。

### Compound solution follow-up

当本次会话刚解决了具体 bug、构建失败、测试失败、集成问题或工程排查问题时，优先建议 `ce-compound`，不要在 reflect 中重写 solution 正文。详细边界见 `knowledge-candidates.md`。

### 工作流修复

适合写 workflow fix 的信号：

- 某个协作步骤反复产生摩擦。
- 可通过执行顺序、确认门、验证命令或输出模板降低风险。
- 该修复不属于单个技能，也不是项目事实本身。

每条包含问题、新行为、适用范围和建议加入的规则文本。

## Phase 3 — 输出复盘报告

报告要简洁、可执行。需要完整报告模板时读取 `output-templates.md` 的 `Reflect 报告模板`。

最低结构：

```markdown
# Reflect 报告

## 会话概览

## 新技能候选

## 现有技能优化

## Memory 候选

## 可复用知识候选

## Compound Solution Follow-up

## 工作流修复

## 优先建议

## 可执行选项
```

如果用户已经要求写入文件，省略“可执行选项”中的等待语气，改为列出已写入路径。

## Phase 4 — 写入文件

只有用户明确要求保存、写入、生成文档或全部落盘时执行。写文件前先创建目录：

```bash
mkdir -p aisee/docs/reflect aisee/docs/reflect/skills aisee/docs/reflect/skill-patches aisee/docs/reflect/workflow-fixes aisee/docs/reflect/knowledge-candidates
```

按产物类型读取 `output-templates.md` 或 `knowledge-candidates.md`：

- 会话复盘文档：`output-templates.md`
- 提升为项目 memory：`output-templates.md`
- 新技能草案：`output-templates.md`
- 技能优化建议：`output-templates.md`
- 工作流修复建议：`output-templates.md`
- 可复用知识候选：`knowledge-candidates.md`

写入原则：

- `aisee/docs/reflect/` 是候选区，不是规范事实源。
- `aisee/memory/` 只有用户明确要求时才写，并必须先读取 `aisee/memory/rules.md` 和 `aisee/memory/index.md`。
- 可复用知识候选只是候选卡片，不自动进入全局知识库、用户主目录、其他项目或 active skill。
- 具体已解决工程问题应建议 `ce-compound`，不要复制 solution 正文。

## Phase 5 — 更新索引

写入任何 `aisee/docs/reflect/` 产物后，检查项目根目录是否有 `AGENTS.md` 或其他项目规则索引。

- 如果已有 `aisee/docs/reflect` 入口，不重复添加。
- 如果存在项目规则文件但没有入口，建议用户确认是否添加索引；不要擅自改全局规则。
- 如果没有项目规则文件，只在最终回复中说明未更新索引。

建议索引文本见 `output-templates.md` 的 `Reflect Docs 索引文本`。
