# Delta for {{capability}}

<!-- 基于 threat-model.md 的威胁缓解措施，转化为具体需求和验证场景 -->

## ADDED Requirements

### Requirement: {{需求名称}}

The system SHALL {{描述系统行为，使用 SHALL/MUST}}.

**Security Control**：对应 threat-model.md 中的 {{威胁类型}} 缓解措施

#### Scenario: {{正常路径场景}}

- GIVEN {{合法用户/正常输入的前置条件}}
- WHEN {{触发动作}}
- THEN {{期望的正常结果}}

#### Scenario: {{攻击/异常路径场景}}

- GIVEN {{攻击者/异常输入的前置条件}}
- WHEN {{攻击或异常触发动作}}
- THEN {{系统应拒绝并返回安全的错误响应}}
- AND {{不应泄露内部信息}}

#### Scenario: {{边界条件场景}}

<!-- 根据具体需求补充：过期令牌、权限不足、重复提交、超长输入等 -->

- GIVEN
- WHEN
- THEN

---

### Requirement: {{安全相关需求名称}}

The system MUST {{描述安全约束}}.

#### Scenario: {{验证场景}}

- GIVEN
- WHEN
- THEN
