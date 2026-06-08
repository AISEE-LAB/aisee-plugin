# Proposal: {{change-name}}

## Intent

<!-- 用 1-3 句话说明：为什么要做这个，解决什么安全问题或业务需求 -->

## Scope

### In Scope

<!-- 本次变更要覆盖的功能和安全边界 -->

- **功能范围**：
- **安全边界**（认证 / 授权 / 数据流 / 外部接口）：

### Out of Scope

<!-- 明确不做的事，防止范围蔓延 -->

-

## Security Context

<!-- 为什么这个变更需要走 security-audit schema？ -->

- **涉及认证/授权**：是 / 否
- **涉及用户数据（PII）**：是 / 否
- **涉及外部输入处理**：是 / 否
- **涉及加密/密钥**：是 / 否
- **涉及第三方依赖**：是 / 否，依赖名称：

## Success Criteria

<!-- 什么情况下算成功完成？至少包含一条安全标准 -->

- [ ] 功能验收：
- [ ] 安全验收：所有 STRIDE 威胁均有对应缓解措施
- [ ] 安全验收：SAST 扫描零 High/Critical 问题
- [ ] 安全验收：Security Reviewer 签字通过

## Owners

- **Spec Owner**：@
- **Security Reviewer**：@（必须与 Spec Owner 不同）

## Rollback Plan

<!-- 如果需要回滚，如何快速恢复，特别是密钥/数据的处理 -->
