# tvbox_config

自用 TVBox 线路配置生成工具

## 线路链接

**tvbox.json（不含 R18）**

- GitHub: [https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/dist/tvbox.json](https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/dist/tvbox.json)
- 代理: [https://fastly.jsdelivr.net/gh/FanchangWang/tvbox_config@main/dist/tvbox.json](https://fastly.jsdelivr.net/gh/FanchangWang/tvbox_config@main/dist/tvbox.json)

**my.json（含 R18）**

- GitHub: [https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/dist/my.json](https://raw.githubusercontent.com/FanchangWang/tvbox_config/main/dist/my.json)
- 代理: [https://fastly.jsdelivr.net/gh/FanchangWang/tvbox_config@main/dist/my.json](https://fastly.jsdelivr.net/gh/FanchangWang/tvbox_config@main/dist/my.json)

## 项目结构

```
tvbox_config/
├── config/                 # 配置文件
│   ├── sources.yaml        # 源列表配置
│   └── history.yaml        # 历史记录（自动生成）
├── dist/                   # 生成的 JSON 文件（被跟踪，由 workflow 提交）
│   ├── tvbox.json          # 不含 R18
│   └── my.json             # 含 R18
├── src/tvbox_config/       # 源代码包
│   ├── __init__.py         # 公开 API
│   ├── app.py              # 主程序入口
│   ├── _check.py           # `uv run check` 入口
│   ├── decrypt.py          # AES-CBC / base64 解密
│   ├── http_client.py      # HTTP 客户端 (httpx)
│   ├── json_builder.py     # JSON 输出生成
│   ├── logger.py           # 日志模块
│   ├── models.py           # 数据模型
│   └── source_manager.py   # YAML 配置管理
├── tests/                  # 测试
├── .python-version         # Python 版本（uv 自动读取）
├── .gitattributes          # 行尾约定（LF）
├── pyproject.toml
└── AGENTS.md               # AI 协作指引（WorkBuddy / CodeBuddy 读取）
```

## 环境要求

- Python 3.12+（`.python-version` 固定为 3.12）
- `uv` 包管理器

## 本地运行

```bash
# 安装依赖
uv sync

# 升级依赖（刷新 uv.lock）
uv sync --upgrade

# 运行程序
uv run tvbox-config

# 跑测试（含覆盖率）
uv run pytest
```

## 开发

```bash
# 一键检查（ruff check + ruff format --check + ty check）
uv run check

# 或分别执行
uv run ruff check src/tvbox_config/
uv run ruff format src/tvbox_config/
uv run ty check src/tvbox_config
```

> 质量检查只在本地执行，CI 不跑。提交前请自行跑通 `uv run check` 与 `uv run pytest`。

## 自动更新

项目配置了 GitHub Actions（`.github/workflows/daily_update.yml`），每天 03:00 UTC（11:00 北京时间）执行单一的 `update` job：

1. `uv sync --no-dev` 安装生产依赖
2. `uv run --no-dev tvbox-config` 检测源并重新生成 JSON
3. 若 `dist/` 或 `config/` 有变化 → 自动提交并推送

## 仓库约定

- **`dist/` 必须提交**：它是生成的输出目录，被 workflow 直接提交，不要加入 `.gitignore`。
- **行尾统一 LF**：`.gitattributes` 为 `* text=auto eol=lf`，二进制文件显式声明 `binary`。

## 配置文件说明

编辑 `config/sources.yaml` 添加或修改数据源：

```yaml
sources:
  - name: "源名称"
    urls:
      - "https://example.com/1.json"
      - "https://example.com/2.json"
    encrypted: false  # 是否为加密源
    r18: false       # 是否为 R18 源
```

- `name`: 数据源名称
- `urls`: URL 列表（按顺序检查，第一个可用的将被使用）
- `encrypted`: 是否为加密源（优先本地 Python 解密，失败后回退到解密 API）
- `r18`: 是否为 R18 源（R18 源只会出现在 my.json 中）
