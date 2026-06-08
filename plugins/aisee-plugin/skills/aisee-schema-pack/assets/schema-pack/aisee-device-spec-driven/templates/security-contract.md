# Security Contract: {{change-name}}

状态：适用 / N/A

N/A 原因与接受依据：

## 安全范围与信任边界

| SEC ID | 资产 / 边界 | 威胁 / 风险 | 保护目标 | 关联 FR / HW / FW / CONN |
|---|---|---|---|---|
| SEC-001 | firmware / key / config / user data / protocol / debug port / production data | | confidentiality / integrity / availability / authenticity / safety | |

## 身份、认证与授权

| 项 | 机制 | 存储 / 来源 | 轮换 / 失效 | 验证 |
|---|---|---|---|---|
| Device identity | serial / cert / key / token / TPM / secure element / N/A | | | |
| User/operator identity | password / token / local role / cloud account / N/A | | | |
| Authorization | role / command whitelist / ACL / capability / physical access | | | |
| Provisioning / binding | factory / first boot / app / cloud / field tool | | | |

## 密钥、证书与敏感数据

| 数据 | 位置 | 访问者 | 保护方式 | 擦除 / 备份 / 恢复 |
|---|---|---|---|---|
| key / cert / token / calibration secret / user data / production credential | secure storage / flash / file / TPM / TEE / HSM / cloud | | encryption / access control / readout protection | |

## 启动、调试与固件保护

| 项 | 决策 | 影响 | 验证 |
|---|---|---|---|
| Secure boot / verified boot | enabled / disabled / N/A | | |
| Firmware / package signature | required / optional / N/A | | |
| Anti-rollback | required / optional / N/A | | |
| Debug port / readout protection | locked / restricted / open / N/A | | |
| Factory reset security | preserves / erases / re-provisions | | |
| Bootloader recovery security | | | |

## 通信与数据保护

| 场景 | 保护方式 | 失败处理 | 证据 |
|---|---|---|---|
| Local bus / protocol | plaintext / MAC / encryption / physical trust / N/A | | |
| Cloud / gateway / APP traffic | TLS / DTLS / VPN / signed payload / N/A | | |
| Log / crash / telemetry data | redaction / anonymization / access control / N/A | | |
| OTA / package download | signature / hash / secure channel / rollback protection | | |

## 安全测试与响应

| 测试 / 流程 | 方法 | 通过标准 | 证据 |
|---|---|---|---|
| Negative auth test | invalid cert/token/key/role | access denied and logged | |
| Tamper/update test | modified firmware/package/config | rejected or safe recovery | |
| Debug/readout test | unauthorized debug/read | blocked or documented risk | |
| Credential rotation/revoke | rotate/revoke credential | device recovers or reports clear failure | |
| Vulnerability response | triage/update/rollback | documented owner and SLA | |

## 安全追踪矩阵

| FR | SEC | HW | FW | RT | CONN | PROD | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | SEC-001 | HW-001 | FW-001 | RT-001 | CONN-001 | PROD-001 | OPS-001 | VER-001 | 是 / 否 |