# 受控图片编辑 Handoff 模板

本模板只用于把 `aisee:image-object` 的 source、mask、cutout、bbox 和保护约束转成受控编辑 brief。不要用它替代对象提取、去背景、mask 生产、背景修补或图层包生成。

```text
任务类型：基于 image-object workspace 的受控编辑候选。
编辑目标：<image path>
workspace：<aisee/docs/image-objects/...>
目标平台：<mobile | mini-program | h5 | pc | desktop | multi>
区域描述：<从对话提炼出的自然语言描述，说明需要优化的区域和问题>
区域定位：<mask 路径 / bbox / region id / object id，必须能限制修改范围>
保留项：<必须保持不变的主体、构图、风格、比例、颜色或区域>
修改项：<本轮要修改的内容>
局部范围：<mask 路径 / bbox / object id / 指定区域>
输出尺寸：<WIDTHxHEIGHT 或保持原尺寸>
输出格式：<png | webp | jpeg>
必须避免：新增文字、Logo、水印、无关主体、改变未授权区域、破坏原图风格一致性。
输出要求：保存为 image-object workspace 的 enhanced 候选，不覆盖原图。
```
