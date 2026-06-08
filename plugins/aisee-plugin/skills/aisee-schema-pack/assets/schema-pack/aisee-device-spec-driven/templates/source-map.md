# Source Map: {{change-name}}

## 上游规划来源

| 来源 | 路径 / 描述 | 状态 | 备注 |
|---|---|---|---|
| Hardware SRS | aisee/docs/requirements/...-hw-srs.md | 已确认 / 缺失 / N/A | 需求、约束、硬件适配取舍的来源 |
| Hardware Architecture | aisee/docs/architecture/...-hw-architecture.md | 已确认 / 缺失 / N/A | 全局架构、资源分配、预算和规则来源 |
| Module Architecture | docs/modules/... | 已确认 / 缺失 / N/A | 模块数 >= 5 时应引用 |
| Hardware Change Plan | aisee/docs/change-plan/...-hw-change-plan.md | 已确认 / 缺失 / N/A | 本 change 边界、依赖和 source-map seed 来源 |
| Project Structure Contract | docs/project-structure.md | 已确认 / 缺失 / N/A | 工程目录、厂商库、构建入口 |
| Clock Contract | docs/clock-contract.md | 已确认 / 缺失 / N/A | 系统时钟、外设时钟、项目相关时序 |
| Memory / Device Contract | docs/memory-device-contract.md | 已确认 / 缺失 / N/A | 型号、Flash/RAM/storage、启动文件、linker/scatter、下载/部署配置 |

## 上游事实来源

| 来源 | 路径 / 描述 | 状态 | 备注 |
|---|---|---|---|
| 原理图 / PCB / Pinout / BOM | | 已确认 / 缺失 / N/A | 版本必须可追溯 |
| 数据手册 / Reference Manual / Errata | | 已确认 / 缺失 / N/A | 芯片、外设、传感器、执行器、通信器件或其他目标设备 |
| BSP / SDK / HAL / Vendor Library | | 已确认 / 缺失 / N/A | 厂商库版本、示例工程、生成工具 |
| Build / Map / Image / Flash Log | | 已确认 / 缺失 / N/A | 涉及资源、链接、烧录、部署问题时必须引用 |
| Protocol / Cloud / APP / Gateway Contract | | 已确认 / 缺失 / N/A | Topic、API、payload、command、device shadow、register map 等 |
| Security Policy / Key Provisioning Spec | | 已确认 / 缺失 / N/A | 证书、密钥、secure boot、debug lock、数据保护 |
| Manufacturing / Calibration / Test Spec | | 已确认 / 缺失 / N/A | 工装、产测、序列号、证书写入、校准、追溯 |
| Compliance / Environmental Requirement | | 已确认 / 缺失 / N/A | EMC、ESD、法规、温度、湿度、振动、安规等 |
| Field Log / Failure Report / User Input | | 已确认 / 缺失 / N/A | 现场问题、对话结论、板级测试现象、仪器数据 |

## 本 Change 覆盖

| 类型 | ID | 标题 / 名称 | 来源 | 后续 artifact |
|---|---|---|---|---|
| FR | FR-001 | | Hardware SRS / proposal | specs |
| HW | HW-001 | | Architecture / schematic / datasheet / project contracts | hardware-contract |
| FW | FW-001 | | Architecture / module docs / project structure | firmware-contract |
| RT | RT-001 | | Architecture / clock / memory / map / runtime facts | runtime-contract |
| CONN | CONN-001 | | protocol / cloud / app / gateway contract | connectivity-contract |
| SEC | SEC-001 | | security policy / provisioning / design | security-contract |
| PROD | PROD-001 | | manufacturing / calibration / test spec | production-contract |
| OPS | OPS-001 | | deployment / field / support plan | operations-contract |
| VER | VER-001 | | specs / architecture / known risks | verification-contract |

## 不在本 Change 范围

- 

## Implementation Paths

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | Core/... / src/... / drivers/... | {{scope}}:FW-001 / {{scope}}:RT-001 | add / modify / remove / reference | |
| config | linker / device-tree / build config path | {{scope}}:HW-001 / {{scope}}:RT-001 | add / modify / reference / N/A | |
| test | tests/... / scripts/... / HIL log path | {{scope}}:VER-001 | add / modify / manual / N/A | |
| docs | docs/verification/... | {{scope}}:VER-001 | update / reference | |

## Verification Evidence

| Type | Path / Command | Status | IDs | Notes |
|---|---|---|---|---|
| openspec-validate | `openspec validate {{change-name}}` | pending / passed / failed / blocked | {{scope}}:FR-001 | 结果文件建议写入 docs/verification/{{change-name}}-openspec-validate.md |
| test | docs/verification/{{change-name}}-test-results.md | pending / passed / failed / blocked | {{scope}}:VER-001 | 单元 / 仿真 / HIL / 板级 / 系统测试 |
| manual | docs/verification/{{change-name}}-manual.md | pending / passed / failed / N/A | {{scope}}:VER-001 | 仪器、烧录、板级或现场验证 |

## Artifact 适用性

| Artifact | Required | 原因 |
|---|---:|---|
| hardware-contract.md | yes / no | |
| firmware-contract.md | yes / no | |
| runtime-contract.md | yes / no | |
| connectivity-contract.md | yes / no | |
| security-contract.md | yes / no | |
| production-contract.md | yes / no | |
| operations-contract.md | yes / no | |
| verification-contract.md | yes | verification-contract.md 通常必须适用；如无硬件验证也必须说明验证方式 |

## 阻塞项 / 假设

- [ASSUMPTION] 
- [SPEC-GAP] 
- [HW-DOC-MISSING] 
- [PROJECT-STRUCTURE-MISSING] 
- [CLOCK-CONTRACT-MISSING] 
- [MEMORY-DEVICE-CONTRACT-MISSING] 
- [CONNECTIVITY-SPEC-MISSING] 
- [SECURITY-DECISION-REQUIRED] 
- [PRODUCTION-DECISION-REQUIRED] 
- [OPS-DECISION-REQUIRED] 
- [STACK-CONTEXT-MISSING] 
- [STACK-DECISION-REQUIRED] 
- [BUDGET-RISK] 
- [FLASH-DOWNLOAD-RISK] 
- [SAFETY-RISK] 

## 追踪规则

- specs 必须覆盖本 change 的全部 FR。
- hardware-contract.md 必须覆盖 Required=yes 的 HW。
- firmware-contract.md 必须覆盖 Required=yes 的 FW。
- runtime-contract.md 必须覆盖 Required=yes 的 RT。
- connectivity-contract.md 必须覆盖 Required=yes 的 CONN。
- security-contract.md 必须覆盖 Required=yes 的 SEC。
- production-contract.md 必须覆盖 Required=yes 的 PROD。
- operations-contract.md 必须覆盖 Required=yes 的 OPS。
- verification-contract.md 必须覆盖全部验收场景和已知风险。
- 涉及工程初始化、型号变更、时钟、Flash/RAM/storage、启动文件、linker/scatter、下载/部署、连接协议、安全凭据、生产校准或现场运维时，必须引用对应 contract。
- tasks.md 生成前必须确认上述追踪关系闭合。
