# Tasks: {{change-name}}

> 严格按顺序执行，完成一项打一个勾。
> 发现安全问题：暂停 → 更新 threat-model.md / design.md → 通知 Security Reviewer → 继续。
> 标注 [SECURITY-CRITICAL] 的 task 完成后必须通知 Security Reviewer。

## Phase 1：Setup

- [ ] 1.1 确认 threat-model.md 已由 Security Reviewer 审查通过
- [ ] 1.2
- [ ] 1.3

## Phase 2：核心实现

- [ ] 2.1 实现 [SECURITY-CRITICAL] 路径：{{具体内容}}
- [ ] 2.2
- [ ] 2.3
- [ ] 2.4 通知 Security Reviewer 对 [SECURITY-CRITICAL] 路径进行中间 review

## Phase 3：测试

- [ ] 3.1 单元测试：覆盖所有安全场景（含攻击路径场景）
- [ ] 3.2 集成测试：验证认证 / 授权流程
- [ ] 3.3 边界测试：超长输入、特殊字符、空值、重复提交
- [ ] 3.4 运行 SAST 静态代码分析，零 High/Critical 问题

## Phase 4：安全验收

- [ ] 4.1 运行依赖漏洞扫描（`npm audit` 或等效工具），无 High/Critical
- [ ] 4.2 检查所有密钥/凭证均不在代码中硬编码
- [ ] 4.3 确认所有外部输入均有验证和过滤
- [ ] 4.4 Security Reviewer 完成全面 review
- [ ] 4.5 **Security Reviewer 签字**：@ \_\_\_\_\_\_ 日期：\_\_\_\_\_\_

## Phase 5：上线

- [ ] 5.1 部署到 staging，执行安全验证场景
- [ ] 5.2 `aisee:verify` 通过
- [ ] 5.3 部署到生产环境
