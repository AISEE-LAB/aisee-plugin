# 图标库与组件库策略

## 目标

提高图标和通用 UI 符号的准确性、一致性和可复用性。通用图标不依赖图片模型重新绘制；图片模型只负责视觉方向、布局氛围和占位表达。

## 触发条件

仅在任务涉及以下内容时读取本文件：

- 参考图、UI 效果图或素材中包含导航图标、操作图标、状态图标、入口图标。
- 用户要求生成图标、图标集、组件风格或素材清单。
- 需要给 Figma、前端或素材 manifest 输出图标建议。

不要在纯背景、摄影、插画、纹理或非 UI 场景中注入图标库规则。

## 图标优先级

通用图标、导航图标、操作图标和状态图标：

1. 优先映射成熟图标库。
2. 再按 StyleSpec 调整尺寸、线宽、颜色、圆角和填充方式。
3. 交付时只说明使用了哪些图标库中的哪些图标，以及必要的尺寸、线宽、颜色和状态映射。
4. 只有品牌符号、业务专属图形、IP 形象或定制插画图标才允许生成新图。

推荐库：

- `lucide`：线性、简洁，适合 SaaS、后台、工具类和移动端通用操作。
- `heroicons`：适合 Tailwind / Web 产品常见 UI。
- `tabler-icons`：覆盖广，适合后台、数据产品和工具界面。
- `phosphor-icons`：风格权重丰富，适合需要多 weight 的产品。
- `material-symbols`：适合 Material Design 体系。
- `remix-icon`：适合移动端、内容产品和泛业务场景。
- `iconify`：作为跨库索引入口，不作为单一视觉风格来源。

## 可选检索工具

如果环境中已有 `better-icons` CLI/MCP，可用它搜索和获取 Iconify 生态中的图标，避免手写或臆造 SVG。`better-icons` 支持跨 150+ 图标集合搜索、按 `prefix:name` 获取 SVG、批量获取和项目图标文件同步；它是检索与同步工具，不改变“先选择统一图标库，再记录具体图标”的原则。

全局安装的 `better-icons` 启动和重复检索通常比每次 `npx` 快很多。日常实现阶段优先使用已全局安装的 `better-icons`；未安装时，若任务已经进入前端实现并需要跨库图标检索，可以按项目包管理器安装或用一次性命令执行，并记录命令。若只是规划、素材清单或 brief 阶段，不因缺少 `better-icons` 阻塞，先记录推荐图标库和候选语义。

使用顺序：

1. 先扫描项目已有图标文件、组件库和既定图标库。
2. 已有库能覆盖语义时，只在同库内搜索候选。
3. 需要跨库比较时优先使用全局 `better-icons search`，或 MCP 的 `search_icons` / `recommend_icons`。
4. 选中后在 manifest 中记录 `图标库` 和完整图标 ID，例如 `lucide:search`、`tabler:settings`。

示例：

```bash
better-icons search settings --prefix lucide --limit 10
npx better-icons search settings --prefix lucide --limit 10
npx better-icons get lucide:settings --color currentColor --size 24 --json
```

实现阶段缺少全局命令时可以安装或一次性执行；安装位置优先遵循项目包管理器和用户环境约定。规划阶段不可用时直接按推荐库和项目现有依赖做人工映射。

## Prompt 中的最小表达

参考图生成时，不要求模型精确绘制某个官方图标。只在确实需要时加入一句：

```text
Use simple standard icon placeholders for common actions; final icons will be replaced from Lucide/Iconify according to the icon manifest.
```

如果已有 StyleSpec 指定图标风格，可更具体：

```text
Use simple 24px outline icon placeholders with consistent stroke weight; final icons will be replaced from the selected icon library.
```

不要把完整图标库列表注入图片生成 prompt。

## 组件库参考

组件库只作为视觉语言和下游实现建议，不要求图片模型精确复刻组件源码。

常见选择：

- Web 管理后台：Ant Design、shadcn/ui、Material UI、Radix UI、Arco Design。
- 移动 H5：Vant、NutUI、Arco Mobile。
- 小程序：TDesign Mini Program、WeUI、Vant Weapp。
- 桌面工具：PySide / Qt 原生控件、Fluent UI、Material Design。

选择组件库时记录：

- 平台和端类型
- 组件库名称
- 图标库名称
- 适用范围
- 不适用或需要定制的部分

## Manifest 建议字段

图标素材清单建议记录语义，而不是只记录图片文件：

```markdown
| 语义 | 图标库 | 推荐图标 | 备选 | 尺寸 | 风格 | 用途 | 状态 |
|------|--------|----------|------|------|------|------|------|
| search | lucide | lucide:search | tabler:search | 24 | outline | 搜索入口 | usable |
```

## 尺寸规则

- SVG 优先；不要为了通用图标生成大尺寸位图。
- 预览 PNG 通常使用 `128x128` 或 `256x256`。
- 工具栏/操作图标通常是 `24x24` SVG，PNG 导出为 `48x48` / `72x72`。
- App / 小程序 tab 图标按目标端导出 `1x/2x/3x`，保持线宽和留白一致。
- 自定义小图标源图通常使用 `256x256` 或 `512x512`；只有复杂插画型图标才考虑更大尺寸。
