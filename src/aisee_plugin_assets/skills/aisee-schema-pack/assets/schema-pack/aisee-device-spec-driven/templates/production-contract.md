# Production Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 生产阶段与发布包

| 项 | 内容 | 来源 |
|---|---|---|
| 阶段 | EVT / DVT / PVT / MP / pilot / repair / N/A | |
| 发布包 | firmware / image / package / bitstream / script / fixture app / production tool | |
| 冻结内容 | source commit / binary hash / config / SDK / tool version / BOM / PCB version | |
| 生产入口 | factory programmer / CLI / GUI / station / cloud / manual | |

## 量产烧录 / 部署流程

| PROD ID | 步骤 | 输入 | 输出 | Pass/Fail 标准 | 证据 |
|---|---|---|---|---|---|
| PROD-001 | program / deploy / provision / verify | | | | |

## 设备身份、证书与配置写入

| 项 | 来源 | 写入位置 | 唯一性 / 范围 | 验证 | 失败处理 |
|---|---|---|---|---|---|
| Serial / MAC / IMEI / EUI / Device ID | | flash / EEPROM / file / secure storage / cloud | | | |
| Certificate / key / token | | secure storage / TPM / TEE / file / cloud | | | |
| Factory config | | | | | |
| Cloud / app / customer binding | | | | | |

## 校准与出厂参数

| 参数 | 单位 / 范围 | 校准设备 | 写入位置 | 有效期 / 版本 | 验证 |
|---|---|---|---|---|---|
| | | | | | |

## 工装、夹具与产测项目

| 测试项 | 工装 / 设备 | 测试时间预算 | 通过标准 | 数据记录 | 失败处理 |
|---|---|---|---|---|---|
| | | | | | |

## 追溯与记录

| 追溯字段 | 来源 | 保存位置 | 保留期限 | 用途 |
|---|---|---|---|---|
| PCB/BOM/firmware/tool/operator/time/result/batch | | local log / MES / cloud / file | | |

## 返修、重刷与解绑

| 场景 | 允许动作 | 风险 | 验证 | 记录 |
|---|---|---|---|---|
| repair / refurbish / reflash / unbind / re-calibrate | | | | |

## 生产追踪矩阵

| FR | PROD | HW | FW | RT | CONN | SEC | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | PROD-001 | HW-001 | FW-001 | RT-001 | CONN-001 | SEC-001 | OPS-001 | VER-001 | 是 / 否 |