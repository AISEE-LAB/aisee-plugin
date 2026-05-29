# openspec/project.md 模板

用于 INIT。替换 `{placeholder}` 后写入 `openspec/project.md`。
本文件只描述项目事实，不放 AI 行为规则。

```markdown
# 项目上下文

> 本文件描述项目技术上下文。Codex 行为规则见 `AGENTS.md`。
> 最后更新：{date}

## 项目概览

- 名称：{project name}
- 类型：{Web app / CLI / Library / Other}
- 目标：{one-sentence goal}
- 主要用户：{target users}

## 技术栈

> 项目级技术栈的权威来源。未确认项写“未确认”，不要让 AI 在 change 阶段临时选型。

**技术栈状态**：已确定 / 部分确定 / 未确认
**技术栈来源**：用户确认 / 既有代码 / 架构文档 / 待确认

### 核心

- 语言：{language + version}
- 框架：{framework}
- 数据库：{database}
- 运行环境：{runtime}
- 客户端形态：{PC Web / H5 / App / 微信小程序 / CLI / Other}

### 工具链

- 包管理器：{package manager}
- 测试：{test framework}
- 格式化 / Lint：{formatter/linter}
- CI/CD：{platform}

### 基础设施

- 鉴权 / 权限：{auth / permissions}
- ORM / 数据访问：{ORM / data access}
- 队列 / 异步任务：{queue / jobs}
- 缓存：{cache}
- 文件存储：{file storage}
- 通知 / 消息：{notification / messaging}
- 部署环境：{deployment target}

### 未确认技术决策

| 决策 | 影响范围 | 当前状态 | 负责人 |
|---|---|---|---|
| {decision} | {scope} | 未确认 | {owner} |

## 架构概览

{brief architecture description}

## 模块划分

| 模块 | 路径 | 职责 |
|---|---|---|
| {module} | `{path}` | {responsibility} |

## 开发约定

- 分支命名：{branch convention}
- 提交格式：{commit convention}
- 代码风格：{style convention}
- 测试策略：{test strategy}

## 外部依赖和服务

| 服务 | 用途 | 环境变量 |
|---|---|---|
| {service} | {purpose} | `{ENV_VAR}` |

## 环境设置

```bash
{setup commands}
```

## 常用命令

```bash
# 开发
{dev command}

# 测试
{test command}

# 构建
{build command}
```
```
