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
├── config/              # 配置文件
│   ├── sources.yaml     # 源列表配置
│   └── history.yaml     # 历史记录（自动生成）
├── dist/                # 生成的 JSON 文件
│   ├── tvbox.json       # 不含 R18
│   └── my.json          # 含 R18
├── src/
│   └── tvbox_config/    # 源代码包
│       ├── app.py           # 主程序入口
│       ├── http_client.py   # HTTP 客户端 (httpx)
│       ├── json_builder.py  # JSON 构建器
│       ├── logger.py        # 日志模块
│       ├── models.py        # 数据模型
│       └── source_manager.py # 源管理器
├── pyproject.toml       # 项目配置
└── uv.lock              # 依赖锁定文件
```

## 本地运行

```bash
# 安装依赖
uv sync

# 运行程序
uv run tvbox-config
```

## 开发

```bash
# 安装依赖（含开发依赖）
uv sync --dev

# 代码格式化
uv run ruff format src/tvbox_config/

# 代码检查
uv run ruff check src/tvbox_config/
```

## 自动更新

项目配置了 GitHub Actions，每天 11:00（北京时间）自动检测并更新可用的 TVBox 线路。

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
- `encrypted`: 是否为加密源（会通过解密接口获取内容）
- `r18`: 是否为 R18 源（R18 源只会出现在 my.json 中）
