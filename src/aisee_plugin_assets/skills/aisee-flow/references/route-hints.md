# Route Hints

本文件只在 `aisee:flow` 需要把模糊请求映射到下一步入口时读取。普通 change 状态检查不要加载本文件。

## 入口映射

| 用户请求类型 | 推荐入口 |
|---|---|
| 发散想法、寻找值得做的方向 | `ce-ideate` |
| 深入一个已选功能、目标或产品方向 | `ce-brainstorm`；若结论需要规范化，再进入 `aisee:srs` |
| 找 bug 根因、解释失败、修复异常或测试失败 | `ce-debug` |
| 规划怎么实现、拆工程步骤 | `ce-plan`；若已有 OpenSpec change，结论必须回写当前 schema apply tracks / source-map（如适用） |
| 澄清业务需求、范围、非目标、验收方向 | `aisee:srs` |
| 拆 OpenSpec change、选择 schema、规划 change 依赖 | `aisee:change-plan` |
| 已有 change，需要判断能否实现、验证或归档 | `aisee:flow` 状态卡 |

## 输出约束

- 只给下一步入口和原因，不展开讨论内容。
- 不创建 OpenSpec change，不写 artifacts，不写 `tasks.md`。
- 需要长期保存的结论必须进入 CE artifact、Aisee 上游文档、当前 OpenSpec artifacts、schema apply tracks 或 source-map。
