# aisee:architecture — 模板入口

在 Phase 4 先读取本文件，再按技术域读取对应模板。不要一次性加载所有 domain 模板。

---

## 选择顺序

1. 判断技术域：software / web / backend / cli / job / integration / data / hardware / embedded / firmware / rtos / driver / hybrid
2. 始终读取 core 模板和 artifact hints 模板
3. 按技术域读取 software 或 embedded 扩展模板
4. 每次生成都读取写作规则

---

## 模板索引

| 模板 | 文件 | 使用时机 |
|------|------|----------|
| Core | `architecture-template-core.md` | 所有技术域都必须读取 |
| Software | `architecture-template-software.md` | software / web / backend / cli / job / integration / data |
| Embedded | `architecture-template-embedded.md` | hardware / embedded / firmware / rtos / driver |
| Artifact Hints | `architecture-template-artifact-hints.md` | 所有技术域都必须读取 |
| Writing Rules | `../references/writing-rules.md` | 每次生成都必须读取 |

---

## 读取规则

### 软件域

适用于 `software`、`web`、`backend`、`cli`、`job`、`integration`、`data`：

- `architecture-template-core.md`
- `architecture-template-software.md`
- `architecture-template-artifact-hints.md`
- `../references/writing-rules.md`

### 硬件 / 嵌入式域

适用于 `hardware`、`embedded`、`firmware`、`rtos`、`driver`：

- `architecture-template-core.md`
- `architecture-template-embedded.md`
- `architecture-template-artifact-hints.md`
- `../references/writing-rules.md`

### 混合域

适用于 `hybrid`：

- `architecture-template-core.md`
- `architecture-template-software.md`
- `architecture-template-embedded.md`
- `architecture-template-artifact-hints.md`
- `../references/writing-rules.md`

---

## 质量检查清单

- [ ] 没有输出 change 边界规划方案
- [ ] 没有输出 change 名称、phase、依赖图或 `/opsx:*` 命令
- [ ] 已识别技术域：software / web / backend / cli / job / integration / data / hardware / embedded / firmware / rtos / driver / hybrid
- [ ] 技术栈 / 工具链状态已标注：已确定 / 部分确定 / 未确定
- [ ] 每条关键技术事实都有来源和可信度
- [ ] 架构概览和架构决策已区分事实、已确认决策与待确认决策
- [ ] ARCH / DEC / CONSTRAINT / RISK ID 已来自 `aisee/registry/id-registry.json`，或已标注 `[ID-RESERVATION-REQUIRED]`
- [ ] 全局工程约定只记录已有事实或待决策缺口，没有创造新契约
- [ ] Schema Artifact Hints 只提示后续契约类型，不绑定具体 schema 文件名
- [ ] 技术栈缺失时使用 `[STACK-CONTEXT-MISSING]` 或 `[STACK-DECISION-REQUIRED]`
- [ ] 给 `aisee:change-plan` 的内容只包含事实、约束和原因
- [ ] 没有写数据库表结构、API endpoint、request/response 字段、CLI 参数完整契约、Job 详细调度策略、寄存器表、引脚表、时序表、ORM 代码或实现步骤
