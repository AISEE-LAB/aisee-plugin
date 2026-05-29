# Verification Contract: {{change-name}}

## 验证范围

| VER ID | 验证目标 | 关联 FR | 关联 HW / FW / RT / CONN / SEC / PROD / OPS | 方法 |
|---|---|---|---|---|
| VER-001 | | FR-001 | HW-001 / FW-001 / RT-001 / CONN-001 / SEC-001 / PROD-001 / OPS-001 | static / unit / sim / HIL / bench / integration / system / production / field / manual |

## 分层验证策略

| 层级 | 目标 | 工具 / 环境 | 通过标准 | 证据 |
|---|---|---|---|---|
| Static | lint / MISRA / cppcheck / clang-tidy / shellcheck / schema validation | | | |
| Unit | module / driver / parser / algorithm / tool function | | | |
| Simulation | QEMU / Renode / model / mock / virtual bus / software-in-loop | | | |
| Bring-up | clock / power / pin / peripheral / boot / basic IO | board / fixture / lab | | |
| Integration | hardware + firmware + runtime + connectivity | board / cloud / app / gateway / host | | |
| System | end-to-end user / production / operations scenario | full setup | | |
| Soak / stress | long-run / load / resource / reboot / network loss | | | |
| Production | factory programming / fixture / calibration / traceability | station / fixture | | |
| Field / operations | update / rollback / diagnostics / support workflow | field-like setup | | |

## 自动化验证

| 测试 | 工具 / 框架 | 环境 | 输入 | 期望结果 | 证据 |
|---|---|---|---|---|---|
| | Unity / CMock / pytest / QEMU / Renode / kernel test / custom / CI | | | | |

## 板级、仪器与系统验证

| 测试 | 设备 / 仪器 | 接线 / 配置 | 步骤 | 通过标准 | 证据 |
|---|---|---|---|---|---|
| | project instrument / oscilloscope / logic analyzer / power meter / protocol analyzer / serial log / JTAG / SWD / OS log | | | | |

## 连接与外部系统验证

| 测试 | 对端 / 环境 | 输入 | 期望结果 | 证据 |
|---|---|---|---|---|
| Protocol compatibility | cloud / APP / gateway / host / peer device / bus analyzer | | | |
| Offline / reconnect / retry | network loss / endpoint loss / bus fault | | | |
| OTA / remote config path | cloud / app / gateway / file server | | | |

## 安全验证

| 测试 | 方法 | 通过标准 | 证据 |
|---|---|---|---|
| Credential / key / token validation | invalid / expired / revoked / missing credential | access denied or safe failure | |
| Firmware / package tamper | modified binary / hash / signature | rejected or safe rollback | |
| Debug / readout / physical access | unauthorized debug/read attempt | blocked or documented risk | |
| Sensitive log/data check | inspect logs / crash / telemetry | no unintended secret/privacy leak | |

## 生产制造验证

| 测试 | 工装 / 设备 | 输入 | 通过标准 | 证据 |
|---|---|---|---|---|
| Factory programming / deployment | | | | |
| Serial / cert / key / config write | | | unique and traceable | |
| Calibration | | | within tolerance | |
| Production traceability | | | record complete | |

## 烧录、下载、部署与启动验证

| 场景 | 工具 / 配置 | 前置状态 | 步骤 | 通过标准 | 证据 |
|---|---|---|---|---|---|
| 空片 / clean target 部署 | ST-Link / J-Link / DAPLink / vendor tool / package manager / image flasher | blank / clean | program / install / deploy / verify / reset | 成功启动，日志或功能可确认 | tool log / screenshot / serial log |
| 已有程序 / 已安装版本覆盖 | | existing app/image/package present | sector erase / program / package upgrade / optional verify / reset | 不依赖 full erase 或明确必须 full erase | |
| 全片擦除 / clean image 后部署 | | full chip erase / clean rootfs / clean partition | program / deploy / reset | 用于区分保护、下载算法、残留状态问题 | |
| 不同下载/部署选项 | verify / reset and run / connect under reset / speed / package flags | | 对比测试 | 失败原因定位到选项或排除选项 | |
| 边界大小镜像 / 包 | map size / image size near limit | | build + deploy | 不超过 hardware/runtime 预算且可稳定部署 | map + deploy log |

## 固件版本、构建与环境

- 固件 / 软件 / 镜像版本：
- Build type / optimization：
- Toolchain / IDE / CMake / Make / Yocto / Buildroot / package manager：
- Startup / linker / scatter / DTS / image layout：
- Flash algorithm / downloader / deployment tool：
- Bootloader / partition / rootfs：
- 测试板卡 / 批次 / host 环境：
- 配置文件 / factory data：
- 回滚方法：

## 资源与预算验证

| 验证项 | 输入 | 通过标准 | 证据 |
|---|---|---|---|
| Flash / ROM / image / package budget | map / image / package | runtime-contract margin satisfied | |
| RAM / .bss / heap / stack / process memory budget | map / watermark / runtime monitor | runtime-contract margin satisfied | |
| Storage / filesystem / partition budget | image / df / partition table | runtime-contract margin satisfied | |
| CPU / event rate / throughput | profiler / benchmark / timing | runtime-contract margin satisfied | |
| 大库 / package 引入影响 | map / package delta | 已评估替代方案且未破坏预算 | |
| 型号/容量/硬件版本匹配 | device macro / linker / DTS / flash algorithm / package target | 与 hardware-contract 一致 | |

## 环境、可靠性与合规验证

| 项 | 方法 | 通过标准 | 证据 |
|---|---|---|---|
| Power loss / brown-out / reset | fault injection / lab test | safe recovery | |
| Low power / wakeup | measurement / wake test | meets requirement | |
| Long-run / aging / stress | soak test | no unacceptable drift/failure | |
| Thermal / environmental | chamber / thermal / humidity / vibration if applicable | meets requirement | |
| EMC / ESD / compliance | pre-compliance / lab / review if applicable | meets target or documented risk | |

## 验收追踪矩阵

| Spec 场景 | VER | 自动化 | 手工 / 仪器 / 外部系统 | 生产 / 运维 | 是否完整 |
|---|---|---|---|---|---|
| specs/... | VER-001 | 是 / 否 | 是 / 否 | 是 / 否 / N/A | 是 / 否 |