# 素材生成 Prompt 模板

```text
任务类型：生成单个可复用设计素材。
素材类型：<background | illustration | overlay | layout-layer | transparent>
目标平台：<mobile | mini-program | h5 | pc | desktop | multi>
使用位置：<页面/模块/组件>
建议尺寸：<WIDTHxHEIGHT>
透明输出：<yes | no>
风格依据：<reference path / StyleSpec path>
style_anchor：<主参考图 / StyleSpec / design-spec path>
style_lock：<必须保持的颜色、线条、圆角、材质、光照、构图密度、品牌元素>
allowed_variation：<允许变化的主体、尺寸、裁切、状态、背景或透明范围>
主体描述：<素材主体>
视觉风格：<色彩、材质、光影、图形语言>
构图要求：<居中/留白/边距/适合叠加>
一致性检查：生成后对照 style_anchor 检查色板、线条语言、阴影/光照、材质、构图密度和品牌元素。
必须避免：文字、Logo、水印、无关背景、错误图标含义、不可控 UI 控件。
输出要求：独立位图素材，可进入项目本地 assets 目录。
```

## 图标例外

通用 UI 图标、导航图标、操作图标和状态图标不要使用本位图生成模板。先按 `references/icon-library.md` 映射图标库，并记录语义、图标库、推荐图标、备选图标、尺寸和风格。

只有品牌符号、业务专属图形、IP 形象或插画型图标才允许作为自定义素材生成。此时素材类型写 `illustration` 或 `transparent`，并在主体描述中说明这是定制图形，不是通用 UI 图标。
