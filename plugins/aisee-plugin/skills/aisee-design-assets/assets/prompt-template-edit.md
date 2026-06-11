# 受控图片编辑 Prompt 模板

本模板用于把用户的局部优化意图整理成受控图片编辑 brief。松散范围的视觉完善可由 `aisee:design-assets` 直接驱动 Image2 生成候选；需要精确对象、mask、bbox、cutout、去背景、边缘修复或背景修补时，必须先由 `aisee:image-object` 准备 handoff。

```text
任务类型：受控局部内容优化 / 基于 image-object workspace 的受控编辑候选。
目标模型：Image2 / gpt-image-2
编辑目标：<image path>
workspace：<可选；aisee/docs/image-objects/...>
目标平台：<mobile | mini-program | h5 | pc | desktop | multi>
用户意图摘要：<用户真正想改善的问题>
区域描述：<从对话提炼出的自然语言描述，说明需要优化的区域和问题>
区域定位：<自然语言区域；如有 mask 路径 / bbox / region id / object id 必须写>
保留项：<必须保持不变的主体、构图、风格、比例、颜色、文字区或未授权区域>
修改项：<本轮只允许新增、优化或修正的内容>
文本策略：<no-text | editable-text-zone | raster-text-confirmed>
局部范围：<semantic-area | mask path | bbox | object id>
handoff_required：<yes | no；需要精确 mask/object 时写 yes>
输出尺寸：<WIDTHxHEIGHT 或保持原尺寸>
输出格式：<png | webp | jpeg>
必须避免：新增文字、Logo、水印、无关主体、改变未授权区域、破坏原图风格一致性。
输出要求：生成新候选，不覆盖原图；如果来自 image-object，保存为 workspace 的 enhanced 候选。
```
