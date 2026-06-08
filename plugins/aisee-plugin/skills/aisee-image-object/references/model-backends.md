# 模型后端

## 默认策略

第一版以成熟模型为基准，Pillow/OpenCV 只做确定性辅助处理。

- 去背景：优先 rembg 已集成模型。
- 高质量通用：`birefnet-general`。
- 快速或资源受限：`birefnet-general-lite`、`u2netp`。
- 通用兼容 fallback：`u2net`。
- 动漫：`isnet-anime`。
- 人像：`birefnet-portrait`。
- 点选/框选：SAM/SAM2 可选 backend。
- 背景修补：LaMa / IOPaint 优先；OpenCV 只做 fallback。

## Profile

- `quality`：`birefnet-general` → `birefnet-general-lite` → `isnet-general-use` → `u2net`
- `fast`：`birefnet-general-lite` → `u2netp` → `u2net`
- `product`：`birefnet-general` → `isnet-general-use` → `u2net`
- `portrait`：`birefnet-portrait` → `u2net_human_seg` → `u2net`
- `anime`：`isnet-anime` → `u2net`
- `compat`：`u2net` → `u2netp`

## 依赖缺失

依赖缺失时必须返回结构化错误，并写入 operation：

- `rembg` 缺失：提示安装 `rembg`
- `sam2` 或 checkpoint 缺失：提示配置 SAM2 backend
- `cv2` 缺失：背景修补不可用

不要静默改用图片生成模型伪造分割结果。
