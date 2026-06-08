# aisee:srs — SRS 模板索引

在 Phase 4（生成 SRS）开始时读取本文件。本文件是模板路由索引，不是完整模板。

## 模板选择

根据 `SKILL.md` Phase 3 的输出模式选择模板：

| Output mode | Read these files |
|-------------|------------------|
| Standard | `references/writing-rules.md` + `assets/srs-template-standard.md` + relevant blocks from `references/scenario-extension-blocks.md` |
| Epic main document | `references/writing-rules.md` + `assets/srs-template-epic-main.md` |
| Epic module document | `references/writing-rules.md` + `assets/srs-template-epic-module.md` + relevant blocks from `references/scenario-extension-blocks.md` |

## 读取规则

- 生成任何 SRS 文档前，始终读取 `references/writing-rules.md`。
- 确认需求域和交付形态前，始终读取 `references/domain-rules.md`。
- 决定 Epic 模块或写模块标题前，始终读取 `references/module-boundary-rules.md`。
- 只读取当前输出模式需要的模板文件。
- 只读取与当前 FR 匹配的场景扩展块。
- 不要在场景不匹配时机械复制场景扩展块。
- SRS 保持规划级详细度：足够交接给 UI Content、Architecture 和 Change Plan，但不写实现级 API、数据库、代码或任务设计。

## 设备约束说明

当前模板主线支持软件 / 全栈需求。若软件需求涉及设备、上位机、IoT 或现场硬件协作，只记录软件可见的设备约束：

- 设备能力、状态、告警、输入输出信号在业务上的含义。
- 用户、操作者或软件系统可观察的异常和降级行为。
- 与 App、Web、后台、上位机或外部系统的协作目的。
- 业务级安全、可靠性和验收方向。

不要在当前模板中展开硬件架构、固件设计、引脚 / 寄存器 / 资源分配、BOM、PCB、制造或验证计划细节。纯硬件 / 嵌入式 / 固件需求应进入后续专用硬件流程。
