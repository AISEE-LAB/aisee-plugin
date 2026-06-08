# 平台差异模板

仅当多端差异复杂时生成 `platform-diff.md`。平台差异只写内容、入口、操作、授权、反馈和能力限制，不写视觉布局。

```markdown
# 平台差异规格：{功能名}

**所属索引**：[`./00-index.md`](./00-index.md)

## 1. 平台能力差异

| 能力 | PC Web / Admin | H5 | App | 微信小程序 |
|------|----------------|----|-----|------------|
| 登录 / 授权 | {rule} | {rule} | {rule} | {rule} |
| 文件上传 | {rule} | {rule} | {rule} | {rule} |
| 下载 / 导出 | {rule} | {rule} | {rule} | {rule} |
| 推送 / 通知 | {rule} | {rule} | {rule} | {rule} |
| 分享 | {rule} | {rule} | {rule} | {rule} |
| 支付 | {rule} | {rule} | {rule} | {rule} |
| 扫码 / 相机 / 定位 | {rule} | {rule} | {rule} | {rule} |

## 2. 页面差异总表

| 页面 | PC Web / Admin | H5 | App | 微信小程序 |
|------|----------------|----|-----|------------|
| PAGE-001 | {content/action diff} | {diff} | {diff} | {diff} |

## 3. 流程差异总表

| 流程 | PC Web / Admin | H5 | App | 微信小程序 |
|------|----------------|----|-----|------------|
| FLOW-001 | {entry/action/feedback diff} | {diff} | {diff} | {diff} |

## 4. 平台特有待确认事项

| 编号 | 问题 | 平台 | 影响页面 | 影响 FR |
|------|------|------|----------|---------|
| Q-001 | {question or 无} | {platform} | PAGE-xxx | FR-xxx |
```
