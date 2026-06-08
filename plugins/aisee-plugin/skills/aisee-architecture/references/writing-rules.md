# aisee:architecture — 写作规则

每次生成技术架构文档时读取。

## 通用规则

- 默认使用中文；除非用户明确要求其他语言。
- 删除所有未使用的模板占位段落，不要留下 `{placeholder}`。
- 如果某节确实无内容，写“无”，不要删除关键章节。
- Open Questions 不得为空白占位；没有问题时写“无”。
- 如果某项信息未确认，写“未确认”，不要猜。
- 如果没有发现某类能力，写“未发现可信来源”，不要写“无”。

## 边界规则

- 不要规划 change 边界，不要命名 change，不要输出 phase、依赖图或 `/opsx:*` 命令。
- 不要做技术栈 / 工具链选型；缺失时标注 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`。
- 不要靠记忆判断框架、SDK、CLI、云服务、数据库或工具链能力；项目来源和官方文档不可用时标注 `[DOC-CONTEXT-MISSING]`。
- 不要输出数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 详细调度策略、ORM 代码或实现步骤。
- 不要输出硬件架构、固件设计、引脚、寄存器、RTOS 任务、驱动结构、BOM、PCB 或制造细节。
- 给 `aisee:change-plan` 的提示只能是事实、约束和原因，不是边界规划结果。
- 架构决策必须区分“已确认”和“待确认”；没有可信来源时只能写入 `[ARCH-DECISION-REQUIRED]`、待确认决策、阻塞项或 Open Questions。

## 来源规则

- 每条关键技术事实都要有来源和可信度：high / medium / low。
- `high`：来自 `openspec/project.md`、代码、schema、配置、官方架构文档。
- `medium`：来自 SRS、UI Content、Design Spec、用户明确说明。
- `low`：从命名或上下文推断，必须标注为假设。
- `low` 可信度事实不能直接作为 change-plan 输入；必须附带后续确认动作。

## 全局工程约定

- 全局工程约定只记录已有事实或待决策缺口。
- 不要在 architecture 中创造新的 API、数据、CLI、Job、设备协作、硬件或固件详细契约。
- 全局工程约定缺失时使用 `[TECH-CONVENTION-MISSING]`，不要替项目制定新约定。

## Domain Blocks

- 只保留与当前需求相关的 domain block。
- 当前主流程只输出软件域块。
- 带设备的软件需求可以输出 Device Collaboration Context，但只写软件可见的设备状态、上报、告警、协作边界和可靠性约束。
- 纯硬件、嵌入式、固件、RTOS、驱动或板级架构不在当前主流程展开，写入 Open Questions 或后续专用硬件流程提示。

## Schema Artifact Hints

- 使用“建议 artifact 类型”，不要绑定具体文件名。
- artifact 名称以 schema pack 为准；schema 未来可以调整。
- 如果后续契约类型不明确，使用 `[SCHEMA-HINT-UNCLEAR]`。
