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

## 需求域扩展

当前模板可同时支持软件 / 全栈需求，以及早期硬件 / 嵌入式 / 混合系统需求。

对于硬件、嵌入式、固件或设备需求：
- 只有在通用 SRS 结构适配时才使用当前模板。
- 不要把软件场景扩展块强行套到硬件 / 设备需求上。
- 记录设备可见行为、操作者流程、运行环境、安全 / 可靠性约束、可观察状态和验收方向。
- 硬件架构、固件设计、引脚 / 寄存器 / 资源分配、验证计划细节交给 `aisee:architecture` 和 change artifacts。
- 如果通用模板承载不足，未来仍可增加硬件专用文件，例如：
  - `references/scenario-extension-blocks-device.md`
  - `assets/srs-template-device-standard.md`
  - `assets/srs-template-device-epic-main.md`
  - `assets/srs-template-device-epic-module.md`
