# 依赖检查清单

运行：

```bash
python aisee-image-object/scripts/check_dependencies.py
python aisee-image-object/scripts/check_dependencies.py --json
python aisee-image-object/scripts/image_object_tool.py config-preview
```

## 核心依赖

核心依赖缺失时，CLI 基础链路不可完整运行。

| 依赖 | 用途 | 安装 |
| --- | --- | --- |
| Pillow | 读取图片、mask、cutout、导出与预览渲染 | `python -m pip install pillow` |
| numpy | 数组处理，OpenCV 和模型后端基础依赖 | `python -m pip install numpy` |
| OpenCV | 背景修补 fallback、图像处理辅助 | `python -m pip install opencv-python` |

## GUI 依赖

| 依赖 | 用途 | 安装 |
| --- | --- | --- |
| PySide6 | 中文双画布 GUI | `python -m pip install PySide6` |

## 去背景模型依赖

| 依赖 | 用途 | 安装 |
| --- | --- | --- |
| rembg | 去背景主路径，调用 BiRefNet / U2-Net 等模型 | `python -m pip install rembg` |
| onnxruntime | rembg ONNX 模型推理运行时 | `python -m pip install onnxruntime` |
| scikit-image | rembg 依赖，matting 质量辅助 | `python -m pip install scikit-image` |

## 可选重依赖

| 依赖 | 用途 | 说明 |
| --- | --- | --- |
| IOPaint | LaMa 背景修补优先 backend | 推荐 Python 3.10/3.11；当前 Python 3.13 环境可能因 Pillow 9.5.0 构建失败 |
| torch / torchvision | SAM2 推理依赖 | `sam2` 安装时通常会一并安装或升级 |
| SAM2 | 点选/框选分割 backend | 需要 Python 包、checkpoint 和 model_cfg；缺失时不影响 rembg 去背景和 GUI 预览导出 |
| LaMa | 背景修补高级 backend | 不进入 MVP 强依赖，OpenCV inpaint 作为 fallback |

## 当前策略

- 默认安装核心依赖、PySide6、rembg 和 onnxruntime，保证 GUI 与成熟去背景主链路可用。
- 背景修补优先使用 LaMa / IOPaint；OpenCV 只作为 fallback，不作为质量主路径。
- SAM2、LaMa 这类重依赖做 optional backend；只有用户明确要启用点选/框选模型或高质量背景修补时再配置 checkpoint。
- 依赖检查脚本只检查 Python 包是否可导入，不下载模型权重。

## 一次性安装

如果当前环境缺少依赖，可以使用：

```bash
python -m pip install -r aisee-image-object/assets/requirements-image-object.txt
```

注意：`sam2` 会安装或升级 `torch` / `torchvision`。如果项目已有固定 PyTorch 版本，先按项目锁文件处理，再单独安装兼容版本。

IOPaint 当前固定依赖旧版 Pillow，在 Python 3.13 下可能安装失败。若需要 LaMa 稳定可用，建议为 image-object backend 单独准备 Python 3.10/3.11 环境。

## LaMa 独立环境配置

推荐让当前 Python 3.13 环境继续承担 GUI、rembg、SAM2 和 CLI 主流程；为 LaMa / IOPaint 单独准备 Python 3.10/3.11 环境。

示例：

```bash
python3.11 -m venv .venv-aisee-lama
.venv-aisee-lama/bin/python -m pip install -U pip
.venv-aisee-lama/bin/python -m pip install iopaint
```

然后复制模板：

```bash
mkdir -p aisee/config/image-object
cp aisee-image-object/assets/config-template.json aisee/config/image-object/config.json
```

把 `iopaint_bin` 改成实际路径：

```json
{
  "lama_backend": {
    "enabled": true,
    "iopaint_bin": ".venv-aisee-lama/bin/iopaint",
    "device": "cpu"
  }
}
```

也可以不写配置文件，直接使用环境变量：

```bash
export AISEE_IMAGE_OBJECT_IOPAINT_BIN="$PWD/.venv-aisee-lama/bin/iopaint"
export AISEE_IMAGE_OBJECT_LAMA_DEVICE="cpu"
```

优先级：

1. CLI 参数：`--iopaint-bin`、`--device`
2. 环境变量：`AISEE_IMAGE_OBJECT_IOPAINT_BIN`、`AISEE_IMAGE_OBJECT_LAMA_DEVICE`
3. 配置文件：`aisee/config/image-object/config.json`，旧项目兼容读取 `.aisee/image-object/config.json`
4. 当前 `PATH` 中的 `iopaint`

执行：

```bash
python aisee-image-object/scripts/image_object_tool.py inpaint-background \
  --workspace aisee/docs/image-objects/product-card-hero \
  --mask mask_001 \
  --method lama
```
