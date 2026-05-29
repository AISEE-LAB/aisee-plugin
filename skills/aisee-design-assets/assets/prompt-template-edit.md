# 图片编辑 Prompt 模板

```text
任务类型：编辑已有图片。
编辑目标：<image path>
目标平台：<mobile | mini-program | h5 | pc | desktop | multi>
保留项：<必须保持不变的主体、构图、风格、比例、颜色或区域>
修改项：<本轮要修改的内容>
局部范围：<mask 区域 / 指定区域 / 全图轻微调整>
输出尺寸：<WIDTHxHEIGHT 或保持原尺寸>
输出格式：<png | webp | jpeg>
必须避免：新增文字、Logo、水印、无关主体、改变未授权区域、破坏原图风格一致性。
输出要求：保存为新版本，不覆盖原图。
```
