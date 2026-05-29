# Tasks: {{change-name}}

## 生成前一致性检查

- [ ] 每个 FR 已映射到 specs。
- [ ] 涉及硬件资源、型号、引脚、时钟、电源、启动/链接/下载/部署配置的 FR 已映射到 hardware-contract.md。
- [ ] 涉及固件、驱动、协议、工程目录、ISR/DMA、数据所有权、配置或日志的 FR 已映射到 firmware-contract.md。
- [ ] 涉及时序、内存、功耗、调度、map、image/package、Linux service、heap/stack 或库资源成本的 FR 已映射到 runtime-contract.md。
- [ ] 涉及通信、云端、APP、网关、协议、远程配置或 OTA 数据路径的 FR 已映射到 connectivity-contract.md。
- [ ] 涉及身份、证书、密钥、debug lock、secure boot、敏感数据、权限或安全更新的 FR 已映射到 security-contract.md。
- [ ] 涉及量产、产测、工装、校准、序列号、证书写入、追溯或返修的 FR 已映射到 production-contract.md。
- [ ] 涉及现场部署、升级、回滚、日志、诊断、兼容、RMA 或维护的 FR 已映射到 operations-contract.md。
- [ ] 每个验收场景、烧录/部署风险、资源风险、连接风险、安全风险、生产风险、运维风险和边界场景已映射到 verification-contract.md。
- [ ] N/A artifact 已写明原因。
- [ ] source-map.md 的阻塞项已处理或明确保留风险。
- [ ] 本 change 未违反 docs/architecture 中的架构规则。
- [ ] 涉及工程初始化时，已包含 hw:init generate-skeleton 任务。

## 1. Change 类型选择

保留适用于本 change 的任务块，删除或标注 N/A 不适用块。

- [ ] 1.1 类型：initialize / hardware bring-up / driver / runtime / connectivity / security / production / operations / algorithm-library / bugfix / other。
- [ ] 1.2 确认本 change 的依赖 change 已完成或明确阻塞。
- [ ] 1.3 确认本 change 的 source-map seed 已写入 source-map.md。

## 2. Bring-up / 环境准备

- [ ] 2.1 确认目标板卡、工具链、SDK/BSP/OS、工程目录和烧录/部署链路。
- [ ] 2.2 确认硬件资源、型号、storage、引脚、外设、硬件版本和文档版本。
- [ ] 2.3 确认 startup、linker/scatter、DTS、partition、flash algorithm、deployment config 与目标一致。
- [ ] 2.4 如本 change 是 initialize-hardware-project，使用 hw:init generate-skeleton 生成或校验工程骨架与 project/clock/memory contracts。

## 3. 实现

- [ ] 3.1 实现硬件 / 固件 / 运行时 / 连接 / 安全 / 生产 / 运维中适用的最小闭环。
- [ ] 3.2 更新配置、构建文件、生成文件或工具脚本。
- [ ] 3.3 更新必要的错误处理、日志、诊断和恢复路径。
- [ ] 3.4 更新资源预算、版本、兼容或 N/A 说明。

## 4. 验证

- [ ] 4.1 运行单元测试 / 静态分析 / 仿真。
- [ ] 4.2 执行板级验证 / HIL / 仪器测量 / OS 集成测试。
- [ ] 4.3 执行连接/协议/云端/APP/网关联调验证，如适用。
- [ ] 4.4 执行安全验证，如证书、密钥、权限、debug lock、secure boot、OTA 签名，如适用。
- [ ] 4.5 执行生产验证，如工装、产测、序列号/证书写入、校准、追溯，如适用。
- [ ] 4.6 执行运维验证，如升级、回滚、日志、诊断、现场恢复，如适用。
- [ ] 4.7 审查 map/image/package，确认 Flash/RAM/storage/.bss/heap/stack/library delta 未超过 runtime-contract 预算。
- [ ] 4.8 执行烧录/下载/部署验证，覆盖本 change 相关的 clean target、已有版本覆盖、clean install 或明确 N/A 原因。
- [ ] 4.9 验证 specs 中的验收场景。
- [ ] 4.10 验证 FR / HW / FW / RT / CONN / SEC / PROD / OPS / VER 追踪关系闭合。

## 5. 收尾

- [ ] 5.1 更新必要文档、版本号、配置、map/image/package 摘要、烧录/部署/运维说明。
- [ ] 5.2 确认无未处理的 [SPEC-GAP] / [HW-DOC-MISSING] / [CONNECTIVITY-SPEC-MISSING] / [SECURITY-DECISION-REQUIRED] / [PRODUCTION-DECISION-REQUIRED] / [OPS-DECISION-REQUIRED] / [BUDGET-RISK] / [FLASH-DOWNLOAD-RISK] / [SAFETY-RISK]。
- [ ] 5.3 如果保留风险，已写入 verification-contract.md 和后续 change 计划。