# Logo Usage Guidelines

## 文件清单

| 文件 | 布局 | 配色 | 用途 |
|------|------|------|------|

## 品牌色

| 名称 | HEX | 用途 |
|------|-----|------|

## 布局版本

- Horizontal：
- Vertical：
- Square：
- Icon only：
- Wordmark：

## Clear Space

- 最小留白：
- 周围不要放置：

## Minimum Size

- Digital：
- Print：

## 正确使用

- 

## 错误使用

- 不要拉伸或压缩
- 不要随意改色
- 不要添加阴影、发光或描边
- 不要旋转或倾斜
- 不要放在复杂背景上
- 不要重绘或替换局部元素

## Web 使用

```html
<img src="logo.svg" alt="<Brand> logo" />
```

```css
.logo {
  width: 100%;
  max-width: 200px;
  height: auto;
}
```

## 导出 PNG

Inkscape：

```bash
inkscape logo.svg --export-type=png --export-filename=logo.png --export-width=1000
```

ImageMagick：

```bash
magick logo.svg logo.png
```
