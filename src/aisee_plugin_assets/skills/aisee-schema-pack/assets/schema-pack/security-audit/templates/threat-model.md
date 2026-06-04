# Threat Model: {{change-name}}

> 基于 STRIDE 模型分析。每个 Critical/High 威胁必须有缓解措施，
> 或写明接受风险的理由并由 Security Owner 签字。

## 系统边界图

<!-- 用文字或 ASCII 图描述数据流和信任边界（Trust Boundary） -->

```
[外部用户] ──请求──► [Trust Boundary] ──► [应用层] ──► [数据层]
                          ↑
                     认证/授权检查
```

**关键资产**（需要保护的数据/功能）：

-

**信任边界**（Trust Boundary 位置）：

-

## STRIDE 威胁分析

### S — Spoofing（身份伪造）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

### T — Tampering（数据篡改）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

### R — Repudiation（抵赖）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

### I — Information Disclosure（信息泄露）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

### D — Denial of Service（拒绝服务）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

### E — Elevation of Privilege（权限提升）

| 威胁描述 | 影响级别 | 缓解措施 |
|---------|---------|---------|
|  | Critical / High / Medium / Low |  |

## 第三方依赖安全

<!-- 列出本次变更引入或更新的第三方依赖 -->

| 依赖名称 | 版本 | 已知 CVE | 处理方式 |
|---------|------|---------|---------|
|  |  | 无 / CVE-XXXX-XXXX |  |

## 接受风险清单

<!-- 有缓解措施成本过高、决定接受的风险，需要 Security Owner 签字 -->

| 威胁 | 接受原因 | Security Owner 签字 |
|------|---------|-------------------|
|  |  |  |

## 威胁模型结论

**整体风险等级**：Critical / High / Medium / Low

**必须在实现前解决的问题**：

-

**Security Reviewer**：@ \_\_\_\_\_\_ **签字日期**：
