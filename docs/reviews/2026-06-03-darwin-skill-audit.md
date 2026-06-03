# Aisee Skill Darwin 审查报告

审查日期：2026-06-03

审查范围：`skills/*/SKILL.md`，共 21 个 skill。

审查方式：使用 `darwin-skill` 的 9 维 rubric 做静态审查和 dry-run 推演。未运行独立子 agent 盲测，因此维度 8 标记为 `dry_run`，分数用于排序和发现缺口，不作为最终质量证明。

## 结论

整体主链路已经可用：`srs -> ui-content / design-spec / architecture -> change-plan -> change-author -> implementation-bridge -> verify -> archive-guard` 的职责边界清晰，OpenSpec、Aisee CLI、schema artifacts、source-map 和 apply tracks 的关系没有明显方向性冲突。

当前最大缺口不是缺少 skill，而是部分入口仍保留旧扫描习惯、部分长 skill 应继续拆 reference、需要补显性 CHECKPOINT，以及硬件旧入口尚未迁入 Aisee 统一体系。

## 方法说明

评分维度来自 `darwin-skill`：

| 维度 | 权重 | 本次审查口径 |
|---|---:|---|
| Frontmatter | 7 | 名称、触发场景、边界和 description 长度 |
| 工作流清晰度 | 12 | 是否有阶段、输入、输出和读取顺序 |
| 失败模式编码 | 12 | 是否有阻塞条件、fallback、不可用处理 |
| 检查点设计 | 6 | 是否有显性用户确认或停止门禁 |
| 可执行具体性 | 17 | 命令、路径、模板、输出格式是否明确 |
| 资源整合度 | 4 | references、assets、scripts 是否可达 |
| 整体架构 | 12 | 是否冗余、是否符合 Aisee/OpenSpec 边界 |
| 实测表现 | 23 | 本次为 dry-run 推演 |
| 反例与黑名单 | 6 | 是否明确“不要做什么” |

## 总览

| Skill | 分数 | 优先级 | 结论 |
|---|---:|---|---|
| `aisee:change-author` | 91 | P1 | schema-aware 能力强，但主文件偏长 |
| `aisee:verify` | 90 | P2 | 验证边界清楚，当前可用 |
| `aisee:archive-guard` | 90 | P2 | 归档门禁清楚，当前可用 |
| `aisee:flow` | 89 | P2 | 状态编排清楚，需保持不变成事实源 |
| `aisee:change-plan` | 88 | P2 | change 边界规则成熟，当前可用 |
| `aisee:image-object` | 88 | P2 | 最近已收敛扫描和缓存路径，当前可用 |
| `aisee:ui-content` | 87 | P1 | 内容边界清楚，但 Phase 0 仍有裸 `find` |
| `aisee:srs` | 86 | P1 | 需求边界清楚，但 Phase 0 仍有裸 `find` |
| `aisee:architecture` | 86 | P1 | 技术架构边界清楚，但 Phase 0 仍有裸 `find` |
| `aisee:spec-migrate` | 86 | P2 | `.gitignore` 扫描规则已较好，当前可用 |
| `aisee:reflect` | 85 | P2 | 候选区和 memory 边界清楚，有一处 fallback 扫描可收敛 |
| `aisee-schema-pack` | 84 | P2 | schema pack 职责清楚，命名格式需统一评估 |
| `aisee:init` | 83 | P1 | 初始化职责清楚，但 runtime 绑定和写入检查点需加强 |
| `aisee:svg-assets` | 82 | P1 | 资产边界清楚，但扫描仍用裸 `find` |
| `aisee:design-spec` | 81 | P1 | 设计规范边界清楚，但主文件偏长且扫描需收敛 |
| `aisee:design-assets` | 80 | P1 | 能力完整，但 prompt library 规则使主文件过厚，扫描需收敛 |
| `aisee:implementation-bridge` | 80 | P1 | 职责正确，但模板重复导致主文件过长 |
| `hw:change-plan` | 78 | P3 | 可用但属于旧硬件入口，暂缓深改 |
| `hw:architecture` | 77 | P3 | 可用但属于旧硬件入口，暂缓深改 |
| `hw:init` | 76 | P3 | 可用但属于旧硬件入口，暂缓深改 |
| `hw:srs` | 75 | P3 | 可用但属于旧硬件入口，暂缓深改 |

## 横向问题

### P0 暂无

没有发现会立即破坏主工作流的致命问题。`change-author`、`verify`、`archive-guard` 对轻量 schema 和 source-map N/A 的处理方向正确。

### P1 应优先处理

1. 多个 skill 的 Phase 0 仍使用裸 `find`。应统一改为 `rg --files`，并明确 fallback `find` 必须排除 `.git`、依赖、构建产物、缓存和生成产物。
2. 多个会写文件或做不可逆决策的 skill 缺少显性 `CHECKPOINT` 标记。已有“等待用户确认”语义，但对 agent 来说不够醒目。
3. `aisee:implementation-bridge`、`aisee:design-spec`、`aisee:change-author`、`aisee:design-assets` 主文件偏长，应继续把模板、示例和细则拆到 `references/`。
4. `aisee:init` 目前天然偏 Codex hooks。这个定位可以保留，但应更明确“当前支持 Codex hook target”，避免被理解为 Aisee 只能服务 Codex。
5. 硬件旧入口暂时不深改，但应在后续统一迁入 Aisee 体系，避免 `hw:*` 与 `aisee:*` 并行扩张。

### P2 可后续优化

1. 资产类 skill 可以统一 `OpenSpec 接入` 的表述，减少 `ui-contract/source-map/tasks` 说明重复。
2. 前置文档 skill 的 ID 规则写法接近，可考虑抽公共 reference，避免未来 ID policy 改动时多处同步。
3. schema-aware skill 中的输出模板可以保留，但长表格更适合拆到 reference。

## 逐个审查

### `aisee:srs`

分数：86。状态：可用，P1 优化。

优点：SRS 与 UI 内容、Architecture、change artifacts 的边界清楚；ID 类型边界明确；Epic 模式和模块划分风险已编码。

问题：

- Phase 0 使用 `find openspec/specs`、`find openspec/changes`、`find aisee/docs/...`，未明确 `.gitignore` 语义。
- 确认门禁存在，但没有显性 `CHECKPOINT` 标记。
- 失败模式主要在 guardrails，缺少 Phase 0 扫描失败的统一 fallback 规则。

建议：

- 将 Phase 0 扫描改为 `rg --files`。
- 在生成 SRS 前增加 `CHECKPOINT: 用户确认需求摘要后才生成`。
- 补一条扫描 fallback 规则。

### `aisee:ui-content`

分数：87。状态：可用，P1 优化。

优点：UI 内容与视觉设计、组件库、实现方案边界清楚；二开场景的 Existing / Changed / New / Deprecated / Unknown 处理正确。

问题：

- Phase 0 仍使用 `find openspec/specs`、`find openspec/changes`。
- 平台不明确时先问，但缺少醒目的检查点。
- UI Content 与 change 内 `ui-contract.md` 的关系已经写清楚，仍可进一步减少重复表达。

建议：

- 收敛扫描命令。
- 增加平台确认和生成前确认 `CHECKPOINT`。

### `aisee:architecture`

分数：86。状态：可用，P1 优化。

优点：Architecture 取代 tech-context 后边界更清楚；不会做技术选型，不写 API/DB 详细契约；schema artifact hints 不绑定固定文件名。

问题：

- Phase 0 使用多条 `find`，可能扫到 ignored 文件。
- 对具体框架/SDK 使用 Context7 或官方文档的规则是对的，但没有写成失败分支。
- 确认门禁不够显性。

建议：

- 改为 `rg --files` 组合筛选。
- 增加 `[STACK-CONTEXT-MISSING]` 下的下一步动作表。

### `aisee:change-plan`

分数：88。状态：可用，P2 优化。

优点：不重新做需求、不默认套 app schema、不把页面/技术层/schema artifact 当 change 的规则已经明确。schema selection 和 source-map seed 条件清楚。

问题：

- 对原始需求输入的允许范围较宽，可能让用户跳过 SRS 直接进入 change-plan。
- 阶段 3 有澄清规则，但没有显性 `CHECKPOINT`。

建议：

- 在输入模式识别后输出“是否需要回到 SRS/UI/Architecture”的门禁。
- 只在规划可执行 changes 前加 `CHECKPOINT`。

### `aisee:change-author`

分数：91。状态：可用，P1 优化。

优点：这是当前最完整的 schema-aware skill。author-check、artifact DAG、ID preflight、轻量 schema 例外、N/A 规则和 app schema v2 顺序都很清楚。

问题：

- 239 行，主文件承担了太多 artifact 编写细节。
- Artifact 编写边界表和 app schema 顺序适合拆到 reference。
- 最后输出中有“建议下一步”，可保留，但应避免被理解为事实源。

建议：

- 保留 SKILL.md 的门禁和总流程，把 artifact 表、app schema v2、N/A 规则拆到 `references/authoring-rules.md`。

### `aisee:implementation-bridge`

分数：80。状态：可用，P1 优化。

优点：定位正确，不生成长期文档，不替代 ce-work，不修补 artifacts；只能从当前 change 和 context pack 获取实现上下文。

问题：

- 251 行，Brief 模板和规则重复出现，主文件偏重。
- `Implementation Brief 输出必须包含` 与 `Brief 输出模板` 可以合并或拆 reference。
- 作为交接器，缺少显性“不得进入 ce-work”的 CHECKPOINT 标记。

建议：

- 将 Brief 模板拆到 `references/brief-template.md`。
- 保留入口门禁、读取顺序和 ce-plan 边界在主文件。

### `aisee:verify`

分数：90。状态：可用，P2 优化。

优点：schema-aware 验证边界清楚，不把 app schema 要求套到轻量 schema。BLOCKER/RISK/INFO 输出明确。

问题：

- dry-run 认为输出模板已足够，但缺少“CLI 不可用时检查哪些最小文件”的更紧凑速查。

建议：

- 可补一个小型 fallback checklist，不急。

### `aisee:archive-guard`

分数：90。状态：可用，P2 优化。

优点：archive 前最终门禁定位清楚，不替代 OpenSpec archive。缺少 verify 或 archive-check 时不得输出“可以 archive”的规则正确。

问题：

- 判定语义较完整，但可进一步压缩 schema 门槛表。

建议：

- 暂不改。等 verify 稳定后再考虑共同抽取 schema gate reference。

### `aisee:flow`

分数：89。状态：可用，P2 优化。

优点：状态编排器定位清楚，不写 SRS、不拆 change、不生成 artifacts。对 `flow inspect/next` 的 CLI 输出解释合理。

问题：

- `recommended path` 中 design-assets / design-spec 的出现顺序可以保持弹性，避免被误读为固定流程。
- 如果没有明确 change 时的前置文档判断可以更 schema-aware。

建议：

- 小幅补充“设计资产与设计规范无固定先后”的说明即可。

### `aisee:init`

分数：83。状态：可用，P1 优化。

优点：`aisee/` 新布局、memory、reflect、hooks 和 schema-pack 的边界清楚；迁移默认只提示不自动执行，方向正确。

问题：

- description 和目标中强调 Codex 配置，runtime-neutral gate 会标记为有绑定风险。
- INIT/OPTIMIZE 会写文件和 hooks，但缺少显性 `CHECKPOINT`。
- `node aisee-init/scripts/setup-hooks.js` 的路径在目标项目中可能依赖安装布局，需确保模板不指向 skill 安装路径。

建议：

- 表述为“当前 hook target 支持 Codex”，不要暗示 Aisee 只支持 Codex。
- 在写 `AGENTS.md`、hooks、memory 或迁移前增加显性确认。

### `aisee-schema-pack`

分数：84。状态：可用，P2 优化。

优点：schema pack 职责和 `aisee:init` 边界清楚；多 schema 推荐规则完整。

问题：

- skill name 是 `aisee-schema-pack`，不是冒号格式，和其他 Aisee skill 命名不完全一致。
- 安装命令同时列 Aisee CLI 和 Node fallback，清楚但略重。

建议：

- 是否改名需要单独讨论；当前不建议为统一格式立刻改名。
- 可把安装命令矩阵拆 reference。

### `aisee:spec-migrate`

分数：86。状态：可用，P2 优化。

优点：已经明确 `.gitignore` 扫描规则；baseline 与 active change 的事实源边界清楚；不再默认 spec-driven 模板。

问题：

- 对写入 baseline specs 前的用户确认可更醒目。
- 迁移索引不是事实源的表达已经清楚，不需要加重。

建议：

- 增加写入前 `CHECKPOINT`。

### `aisee:reflect`

分数：85。状态：可用，P2 优化。

优点：候选区、memory 和真实 skill 目录的边界清楚；不会把 reflect 文档当规范事实源。

问题：

- Phase 0 中第二条命令仍使用 `find aisee/docs/reflect`，虽然范围小，但可统一为 `rg --files aisee/docs/reflect`。
- “主动建议使用本技能”容易扩大触发范围，但当前还可接受。

建议：

- 收敛扫描命令。
- 保持“不自动写 memory”的门禁。

### `aisee:design-assets`

分数：80。状态：可用，P1 优化。

优点：设计资产与 design-spec 的边界清楚；不会把参考图当最终设计稿；OpenSpec 接入只引用路径和约束。

问题：

- Phase 0 使用多条裸 `find`。
- prompt library 规则占据主文件较大篇幅，使入口显得偏重。
- 图片生成/编辑涉及成本和外部 API，检查点可更显性。

建议：

- 将内置提示词库规则拆到 `references/prompt-library.md`。
- Phase 0 改为 `rg --files`。
- API 调用、刷新来源、覆盖文件前增加 `CHECKPOINT`。

### `aisee:design-spec`

分数：81。状态：可用，P1 优化。

优点：设计规范、资产、UI Content、实现和 Figma 的边界清楚；Screen Patterns 不固定枚举，符合之前讨论结论。

问题：

- 251 行，主文件偏长。
- Phase 0 使用多条裸 `find`。
- 设计策略会影响范围，但缺少显性 `CHECKPOINT`。

建议：

- 扫描收敛为 `rg --files`。
- 将 Design Read、参数表、来源映射规则拆 reference。
- 在 adopt/extend/rewrite 策略确认前加 `CHECKPOINT`。

### `aisee:svg-assets`

分数：82。状态：可用，P1 优化。

优点：SVG 生成、trace、optimize、validate 的边界清楚；安全校验和 OpenSpec 接入明确。

问题：

- Phase 0 使用裸 `find`。
- 覆盖同名文件要求确认，但缺少显性 `CHECKPOINT`。
- Logo 模式有澄清门槛，质量不错。

建议：

- 改扫描命令。
- 在覆盖和 logo 生成前增加 `CHECKPOINT`。

### `aisee:image-object`

分数：88。状态：可用，P2 优化。

优点：近期已改为 `rg --files` 并明确 `.gitignore`；对象处理、design-assets、Figma 和前端实现边界清楚；GUI/CLI/source.json 合同完整。

问题：

- 模型 backend 和 GUI 功能较多，dry-run 认为主文件仍接近上限，但尚可接受。
- 图像编辑涉及外部模型时，可进一步强调成本和敏感信息检查点。

建议：

- 暂不改。后续只在模型调用或 GUI 行为变化时再优化。

### `hw:srs`

分数：75。状态：暂缓深改，P3。

优点：硬件需求与适配评估结合得较完整，有确认门禁和硬件 fit loop。

问题：

- 使用 `hw:*` 命名，与当前 Aisee 主体系并行。
- Phase 0 的 POSIX 部分仍有 `find openspec/changes`。
- ID 仍是 `FR-001` 形式，未接入当前 Aisee ID registry。

建议：

- 本轮不深改。未来迁入 `aisee` 体系时，重做 ID、schema 和命名边界。

### `hw:architecture`

分数：77。状态：暂缓深改，P3。

优点：硬件全局接口、资源、时钟、存储、模块和预算门禁完整。

问题：

- 与 `aisee:architecture` 在“架构”概念上并行，未来需要统一。
- 使用 `docs/modules/`、`docs/project-structure.md` 等路径，未完全进入 `aisee/` 新布局。

建议：

- 暂缓深改。后续硬件统一设计时，考虑迁移为 Aisee device architecture 或纳入 device schema 前置文档。

### `hw:change-plan`

分数：78。状态：暂缓深改，P3。

优点：硬件 change 边界、初始化 change、source-map seed 和 device contracts 适用性写得清楚。

问题：

- 默认 schema 固定 `aisee-device-spec-driven`，与当前 `aisee:change-plan` 的 schema auto 策略不同。
- `hw:*` 路径和 Aisee 主链路并行。

建议：

- 暂缓深改。未来应与 `aisee:change-plan` 合并或变成 device-domain reference，而不是继续作为独立主入口扩张。

### `hw:init`

分数：76。状态：暂缓深改，P3。

优点：scan-existing 和 generate-skeleton 边界清楚；明确生成工程骨架必须在 OpenSpec change 内。

问题：

- `generate-skeleton` 会创建/修改工程文件，需要更强 CHECKPOINT。
- 路径和硬件旧体系绑定，未迁入 `aisee/` 新布局。
- 输入仍假设 device schema 的 `design.md` 存在，未来 schema 定型后需复核。

建议：

- 暂缓深改。硬件体系重设时重新设计，不建议继续单点修补。

## 建议执行顺序

1. 先统一修扫描规则：`aisee:srs`、`aisee:ui-content`、`aisee:architecture`、`aisee:design-assets`、`aisee:design-spec`、`aisee:svg-assets`、`aisee:reflect`。
2. 再补显性 `CHECKPOINT`：优先涉及写文件、覆盖、外部 API、hooks、生成正式文档的 skill。
3. 再拆长 skill：`aisee:implementation-bridge`、`aisee:design-spec`、`aisee:change-author`、`aisee:design-assets`。
4. 最后处理命名和硬件旧入口：不在当前软件主线里继续深改 `hw:*`。

## 本次未做

- 未修改任何 skill 本体。
- 未生成 `test-prompts.json`。
- 未执行独立 judge 或 full_test。
- 未生成 Darwin result card。
