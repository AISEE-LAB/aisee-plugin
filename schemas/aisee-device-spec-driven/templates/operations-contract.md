# Operations Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 部署与生命周期

| OPS ID | 场景 | 方式 | 影响对象 | 证据 |
|---|---|---|---|---|
| OPS-001 | factory / field / OTA / package / image / container / manual service | | device / cloud / app / gateway / production / support | |

## 版本、兼容与升级路径

| 项 | 策略 | 约束 | 验证 |
|---|---|---|---|
| Versioning | semantic / build number / git hash / binary hash / product version | | |
| Compatibility | hardware rev / BOM / cloud / app / gateway / protocol / config | | |
| Upgrade path | factory / OTA / package / service tool / manual | | |
| Rollback path | A/B / backup image / bootloader / package downgrade / manual | | |
| Config migration | preserve / migrate / reset / user-confirmed | | |
| Data retention | preserve / erase / backup / N/A | | |

## 观测性、日志与诊断

| 项 | 内容 | 权限 / 隐私 | 证据 |
|---|---|---|---|
| Logs | serial / file / journald / cloud / debug interface / none | | |
| Metrics / health | heartbeat / watchdog / uptime / error counters / resource usage | | |
| Crash / fault dump | memory dump / coredump / fault registers / reboot reason | | |
| Remote diagnostics | command / cloud / app / gateway / support tool / N/A | | |
| Evidence retention | local / cloud / support ticket / production log | | |

## 现场恢复与支持

| 场景 | 恢复方式 | 用户/工程师动作 | 风险 | 验证 |
|---|---|---|---|---|
| power loss / failed update / bad config / lost connectivity / corrupted storage / hardware fault | safe mode / factory reset / rollback / rebind / reflash / RMA | | | |

## 运维文档与交接

| 文档 / 工具 | 受众 | 必要内容 | 位置 |
|---|---|---|---|
| release notes / flashing guide / field guide / support playbook / diagnostic CLI / production SOP | developer / factory / field / support / customer | | |

## 运维追踪矩阵

| FR | OPS | FW | RT | CONN | SEC | PROD | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|
| FR-001 | OPS-001 | FW-001 | RT-001 | CONN-001 | SEC-001 | PROD-001 | VER-001 | 是 / 否 |