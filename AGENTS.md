# TVBox Config — 项目指引

## 概述

TVBox 数据源检测与 JSON 生成工具。获取 TVBox 源 URL，解密加密源（AES-CBC / base64），验证内容，并生成 `tvbox.json` / `my.json` 输出文件。通过 GitHub Actions 每日自动运行。

## 技术栈

| 类别           | 选型                                           |
| -------------- | ---------------------------------------------- |
| Python         | 3.12+（`.python-version` 固定 3.12）           |
| 包管理器       | `uv`（不使用 pip/poetry/conda）                |
| 检查 + 格式化  | `ruff`                                         |
| 类型检查       | `ty`                                           |
| 测试           | `pytest` + `pytest-cov`                        |
| HTTP 模拟      | `respx`                                        |
| 构建           | `uv_build`（src-layout，`module-root = "src"`） |

## 项目结构

```
tvbox_config/
├── src/tvbox_config/          # 源码包
│   ├── __init__.py            # 公开 API 导出
│   ├── app.py                 # 主 App 类，CLI 入口
│   ├── _check.py              # `uv run check` 入口（ruff + ty）
│   ├── decrypt.py             # AES-CBC / base64 解密函数
│   ├── http_client.py         # httpx 封装，okhttp UA
│   ├── json_builder.py        # JSON 输出模块级函数
│   ├── logger.py              # 日志输出到 stderr
│   ├── models.py              # Source / AvailableSource 数据类
│   └── source_manager.py      # YAML 配置加载/保存
├── config/
│   ├── sources.yaml           # 源定义
│   └── history.yaml           # 上次成功状态
├── dist/                      # 生成的 JSON 输出（被跟踪，见「仓库约定」）
├── tests/                     # pytest 测试
├── .github/workflows/         # CI：daily_update.yml
├── .python-version            # Python 版本（uv 自动读取）
├── .gitattributes             # 行尾约定
├── .gitignore
├── pyproject.toml
└── AGENTS.md
```

## 命令

```bash
uv sync                  # 安装/同步依赖
uv sync --upgrade        # 升级依赖并刷新 uv.lock
uv sync --no-dev         # 仅安装生产依赖（CI 运行程序时使用）
uv run tvbox-config      # 主程序：检测源，生成 JSON
uv run check             # 运行 ruff check + ruff format --check + ty check
uv run ruff check .      # 仅检查格式
uv run ruff format .     # 仅格式化
uv run ty check          # 仅类型检查
uv run pytest            # 运行测试（含覆盖率）
uv add <package>         # 添加生产依赖
uv add --dev <package>   # 添加开发依赖
```

## 仓库约定

这几条是硬约束，改动前先看清楚，别按 Python 模板的直觉来。

- **`dist/` 必须提交，不要忽略。** 它是本项目的 JSON 输出目录，由每日 workflow 写入并提交。
  `.gitignore` 里没有任何 `dist/` 规则；若加了 `dist/`（或 `dist/*`），被忽略的新文件不会出现在
  `git status --porcelain dist/` 中，每日更新会**静默不提交**。
- **行尾统一 LF。** `.gitattributes` 为 `* text=auto eol=lf`：二进制自动检测 + 工作区强制 LF。
  新增二进制类型要显式声明为 `binary`（如 `*.jar`、`*.zip`、图片），否则可能被当作文本归一化而损坏。
- **`.workbuddy/` 已忽略**，属于 AI 协作工作目录，不要提交。
- 需要停止跟踪某个已提交文件时，用 `git rm --cached <file>`（保留本地文件），并同时补上忽略规则；
  不要用 `git rm`（会连本地文件一起删）。

## 代码规范

### 结构
- **src-layout** 位于 `src/tvbox_config/`
- 无状态转换 → 模块级函数（`decrypt.py`, `json_builder.py`, `logger.py`, `_check.py`）
- 有状态/生命周期对象 → 类（`HttpClient`, `SourceManager`, `App`）
- 数据容器 → `@dataclass` 配合 `to_dict()` / `from_dict()`（`models.py`）

### 风格（ruff 强制）
- 目标 Python 3.12，行宽 100
- 字符串使用双引号
- 缩进使用空格
- 导入顺序：标准库 → 第三方 → 本地（空行分隔）
- 所有函数需标注返回类型
- 类级常量使用 `ClassVar`（`RUF012` 虽被豁免，但仍按此写）
- `@classmethod` 返回类型使用 `Self`
- 代码中不写注释（`pyproject.toml` 配置中的文档字符串除外）

### 格式化（ruff）
```bash
ruff format . && ruff check . --fix
```

### 日志
- 通过 `logger.py` 的 `get_logger()` 使用 `logging`
- 格式：`[HH:MM:SS] [LEVEL] message`
- 输出到 stderr
- `logger.info()` 用于里程碑
- `logger.debug()` 用于每个 URL 的进度
- `logger.error()` 用于失败
- 数据源日志模板：
  - 加密：以 `⏳ 解密数据源: {name} - {url}` 开头
  - 非加密：以 `⏳ 检查数据源: {name} - {url}` 开头
  - 成功：`✅ 可用数据源: {name} - {url}`
  - 所有 URL 用尽：`🚫 不可用数据源: {name}`

### HTTP 客户端
- UA：`okhttp/4.12.0`
- `follow_redirects=True`
- 连接超时：5s，读取超时：30s
- 任何 `httpx.HTTPError` → 返回 `None`

### 解密（source.encrypted == true）
- 优先本地 Python 解密：
  1. 获取源 URL 的原始内容
  2. 如果已是 JSON（包含 `spider` + `sites` 键的 dict）→ 跳过解密
  3. 如果包含 `xxxxxxxx**` 模式 → 尝试 base64 解码
  4. 如果以 `2423` 开头 → 尝试 AES-CBC 解密
- 回退：尝试远程解密 API 端点（`DECRYPT_URLS`）

### 解密 API URL（定义在 `App.DECRYPT_URLS`）
1. `https://feiyangdigital.v1.mk/api/jiemi.php?url=`
2. `https://www.饭太硬.net/jm/jiemi.php?url=`

## 依赖

### 生产依赖
- `dirtyjson` — 宽松 JSON 解析器
- `httpx` — HTTP 客户端
- `pyyaml` — YAML 配置解析器
- `pycryptodome` — AES-CBC 解密

### 开发依赖
- `ruff` — 检查器 + 格式化工具
- `ty` — 类型检查器
- `pytest` + `pytest-cov` — 测试 + 覆盖率
- `respx` — HTTP 模拟测试

## GitHub Actions

`.github/workflows/daily_update.yml` 只有一个 job `update`，每天 03:00 UTC（11:00 北京时间）运行：

1. 检出代码（`fetch-depth: 0`）+ 安装 uv（`enable-cache`）+ `uv python install 3.12`
2. `uv sync --no-dev`
3. `uv run --no-dev tvbox-config`
4. `git status --porcelain dist/ config/` 有变化 → `git add dist/ config/` → 用 bot 身份提交并推送

**CI 不跑质量检查。** `ruff` / `ty` / `pytest` 只在本地通过 `uv run check` + `uv run pytest` 执行——
所以提交前必须自己跑一遍，别指望流水线兜底。若日后要把门禁搬进 CI，做法是加一个 `quality` job
（`uv sync` + `uv run check` + `uv run pytest`）并让 `update` 声明 `needs: quality`。

> 依赖升级后 ty / ruff 常新增规则（例如 ty 0.0.81 引入 `unsound-return-statement`），
> 升级 `pyproject.toml` 里的下限后要在本地把 `uv run check` 跑通再提交。

## 内容验证（JSON）

使用 `dirtyjson` 解析后得到包含 **同时存在** 且非空的 `"spider"` 和 `"sites"` 键的 dict，则该源有效。

## 测试

测试文件放在 `tests/`，目录结构与源码对应。

覆盖率由 `[tool.pytest.ini_options]` 提供（`--cov=src/tvbox_config --cov-report=term-missing`），
因此 `uv run pytest` 默认输出覆盖率，无需在命令行重复传参：

```bash
uv run pytest -v -s    # 详细模式，不截断输出
uv run pytest          # 默认模式（含覆盖率）
```

对测试网络相关代码时，使用 `respx` 模拟 HTTP。
