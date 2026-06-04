# SVG Logo 设计

## 适用范围

用于创建 SVG logo、brand mark、wordmark、lettermark、组合标、图标标识和 logo 变体。输出是可缩放 SVG 资产和使用说明，不是完整品牌战略或商标法律审查。

## 需求澄清

Logo 任务开始前必须先确认关键需求。除非用户已经在同一条消息里提供足够约束，或明确说“不用问、直接生成、快速出稿”，否则先提问，不要直接生成 SVG 文件。

- 品牌/产品名称
- 行业和市场
- 目标用户
- 品牌个性：现代、经典、严肃、友好、科技、优雅、活泼等
- 品牌价值和想传达的信息
- 竞品或需要避开的相似方向
- 使用场景：网站、App、小程序、名片、印刷、周边、头像、favicon
- 是否需要中文、英文、缩写或纯图形
- 是否需要单色版、反白版、深浅背景版
- 概念数量和布局数量

最低澄清门槛：

1. 品牌/产品名称
2. 风格方向或品牌个性
3. 主要使用场景

每轮最多问 3 个关键问题。问题要简短、可直接回答。用户回答后再进入概念开发和 SVG 输出。

如果用户明确要求快速生成，可以基于合理假设先给 3 个方向或直接生成默认版本，但必须在回复和交付说明中标注假设。

推荐开场问题：

1. Logo 上显示的品牌/产品名称是什么？
2. 风格更偏科技工具、开源项目、设计资产库、企业品牌，还是其他方向？
3. 主要用于哪里：网站、App 图标、文档、头像、favicon、印刷或周边？

CHECKPOINT: 在创建 logo 文件、覆盖既有 logo、生成 guidelines、或输出多变体文件前，必须确认品牌名称、主要用途、风格方向、输出目录和覆盖策略。若只确认了方向但未确认输出路径，先给概念说明或 SVG 草案，不写文件。

## Logo 类型

- `wordmark`：文字标
- `lettermark`：字母/缩写标
- `pictorial-mark`：具象图形标
- `abstract-mark`：抽象几何标
- `mascot`：角色标，SVG 里只建议简单形象
- `combination-mark`：图形 + 文字
- `emblem`：徽章式标识

## 风格维度

- minimalist
- geometric
- organic
- bold
- elegant
- playful
- tech-modern
- vintage
- luxury
- friendly

## 概念开发

默认先输出 3 个概念方向；除非用户明确要求“直接生成文件”，否则先让用户选定方向再生成最终 SVG 变体。每个概念说明：

- 概念名称
- 视觉隐喻
- 为什么适合该品牌
- 适合场景
- 风险或需避开的相似方向

Logo 应遵循：

- 简单
- 易记
- 可缩放
- 可单色使用
- 与行业和目标用户匹配
- 避免过度细节和复杂渐变

不要伪造法律结论。可以提醒用户后续做商标检索和法律审查，但不要声称可注册、无侵权或已避开所有近似标识。

如果用户要求“确认能否注册商标”“判断是否侵权”“保证不像竞品”，停止给法律结论；只能提供视觉相似性风险提示和后续人工/法律审查建议。

## 布局变体

对选定或默认概念，按需生成：

- `horizontal`：图形在左、文字在右
- `vertical`：图形在上、文字在下
- `square`：居中方形布局
- `icon`：纯图形标
- `wordmark`：纯文字标

## 配色变体

常见变体：

- `full-color`
- `monochrome-dark`
- `monochrome-light`
- `reversed`

## SVG 要求

- 必须有 `viewBox`
- 使用 `<title>` 和 `<desc>` 提供基础可访问信息
- 用 `<g id="...">` 组织 symbol / wordmark / background
- 不使用脚本、事件属性、外链、`foreignObject`
- 字体优先用系统字体声明；若要长期稳定显示，建议后续转 path 或由设计工具处理
- 图标版尽量避免过细线条，保证小尺寸可识别
- 颜色变量可用 CSS custom properties，但不要依赖外部 CSS 文件
- 最终版必须通过 `scripts/validate_svg.py`，报告保存到 `reports/`

## 输出目录

```text
aisee/docs/svg-assets/logos/<brand-slug>/
├── concepts/
├── final/
├── guidelines/
└── reports/
```

文件命名：

```text
<brand>-logo-concept-1-horizontal-full-color.svg
<brand>-logo-concept-1-vertical-full-color.svg
<brand>-logo-concept-1-icon-monochrome-dark.svg
<brand>-logo-guidelines.md
```

## 使用规范

Logo 交付时应提供：

- 文件清单
- 颜色规格
- 最小尺寸建议
- clear space 建议
- 深浅背景使用方式
- 不正确用法：拉伸、改色、加阴影、旋转、放在复杂背景上
- Web 使用示例：inline SVG、`img`、CSS background
- SVG 转 PNG 命令建议

如果只交付草案，明确标注“草案”，不生成完整 guidelines。

## 色彩心理参考

- 蓝色：信任、专业、稳定；适合科技、金融、医疗
- 绿色：增长、健康、环保；适合环保、健康、金融
- 红色：能量、热情、紧迫；适合餐饮、娱乐、零售
- 紫色：创造力、精致、科技感；适合美妆、创意、科技
- 橙色：友好、活力、亲和；适合零售、餐饮、娱乐
- 黄色：乐观、清晰、温暖；适合儿童、食品、能源
- 黑/灰：成熟、现代、经典；适合奢侈品、时尚、科技

## 迭代方式

1. 先生成 3 个概念方向
2. 用户选 1 个方向
3. 调整颜色、比例、字体、图形细节
4. 生成最终布局和配色变体
5. 输出使用规范、校验报告和索引记录
