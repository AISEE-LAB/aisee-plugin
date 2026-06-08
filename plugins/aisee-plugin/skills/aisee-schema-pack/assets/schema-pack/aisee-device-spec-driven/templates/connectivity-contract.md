# Connectivity Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 连接范围

| CONN ID | 连接对象 | 介质 / 通道 | 协议 | 方向 | 关联 FR / FW / RT |
|---|---|---|---|---|---|
| CONN-001 | cloud / APP / gateway / peer device / host / local bus / file / IPC | Ethernet / Wi-Fi / cellular / BLE / LoRa / Zigbee / RS485 / CAN / USB / UART / custom / local IPC | MQTT / HTTP / CoAP / Modbus / CANopen / custom / file / socket | uplink / downlink / bidirectional | |

## 设备身份与 Provisioning

| 项 | 内容 | 存储位置 | 写入时机 | 验证 |
|---|---|---|---|---|
| Device ID / Serial / MAC / IMEI / EUI | | hardware / secure storage / file / cloud | factory / first boot / user bind | |
| Certificate / key / token | | secure storage / TPM / TEE / file / N/A | factory / enrollment / rotation | |
| Binding / unbinding | | | app / cloud / factory / field service | |
| Time sync / trust anchor | | | boot / network ready | |

## 端点、Topic、寄存器或路径

| CONN ID | 端点 / Topic / Path / Register / Frame | 方向 | QoS / Ack | 权限 | 兼容规则 |
|---|---|---|---|---|---|
| CONN-001 | | publish / subscribe / request / response / read / write | | | |

## 数据模型与 Payload

| 数据类型 | 字段 / Schema | 单位 / 范围 | 版本 | 编码 | 兼容规则 |
|---|---|---|---|---|---|
| telemetry / event / command / config / shadow / file / stream / alarm | | | | JSON / CBOR / protobuf / binary / text / custom | |

## 协议语义

| 项 | 规则 | 失败处理 | 验证 |
|---|---|---|---|
| Endianness / alignment / frame boundary | | | |
| Checksum / CRC / signature | | | |
| Sequence / timestamp / dedup | | | |
| Retry / backoff / timeout | | | |
| Offline cache / store-and-forward | | | |
| Rate limit / batching / compression | | | |
| Protocol version negotiation | | | |

## OTA / 远程配置数据路径

| 项 | 内容 | 验证 |
|---|---|---|
| Remote config path | | |
| OTA metadata / manifest | | |
| Download / resume / checksum | | |
| Activation / reboot / rollback trigger | | |
| Cloud / app / gateway compatibility | | |

## 连接追踪矩阵

| FR | CONN | FW | RT | SEC | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|
| FR-001 | CONN-001 | FW-001 | RT-001 | SEC-001 | OPS-001 | VER-001 | 是 / 否 |