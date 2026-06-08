# 导出选项

导出变体不修改原始 mask 和 cutout，只在 `exports/` 中生成新文件。

## 透明

- `transparent=true`：保留 alpha，推荐 PNG 或 WebP。
- `transparent=false`：合成到背景色或背景图。

## 背景

- 默认背景：白色。
- 可传入十六进制颜色，如 `#ffffff`。
- 可传入背景图路径，背景图会按输出尺寸居中裁切。

## 圆角

圆角作用在导出画布 alpha 上。透明导出时保留圆角 alpha；非透明导出时圆角区域由背景承接。

## Padding

Padding 在对象外侧增加留白。若导出透明图，留白区域透明；若导出非透明图，留白区域使用背景。

## 裁切模式

- `bbox`：按对象非透明区域裁切。
- `original-canvas`：保持原图画布。
- `square`：以对象中心生成正方形画布。

## 格式

- PNG：透明优先。
- WebP：透明且体积敏感时使用。
- JPG/JPEG：不支持透明，必须合成背景。
