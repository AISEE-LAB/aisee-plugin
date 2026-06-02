# 项目本地输出布局

默认目录：

```text
aisee/docs/svg-assets/
├── index.md
├── index.json
├── generated/
├── logos/
├── traced/
├── optimized/
├── sources/
└── reports/
```

## 文件命名

```text
generated/icon-settings.svg
traced/logo-mark.svg
optimized/logo-mark.svg
logos/acme/acme-logo-concept-1-horizontal-full-color.svg
logos/acme/guidelines/acme-logo-guidelines.md
reports/logo-mark.validate.json
```

## 索引原则

- `index.md` 给人读
- `index.json` 给自动化读取
- 记录来源、输出、转换方式、用途、校验状态
- 不把用户私密图片内容写入索引，只记录项目相对路径和摘要
- 索引只记录最终或明确保留的草案，不记录每一次失败中间产物
- 更新索引前读取现有内容，保持已有条目，不重排无关条目
- 校验失败的文件可以登记为 `failed`，但备注中要说明不能直接 inline 或导入生产资产库

## JSON 字段

每条 `assets[]` 建议包含：

```json
{
  "id": "stable-asset-id",
  "file": "generated/stable-asset-id.svg",
  "source": "local-generation",
  "usage": "frontend-inline-icon",
  "method": "handwritten-svg",
  "validation": "passed",
  "report": "reports/stable-asset-id.validate.json",
  "notes": ""
}
```
