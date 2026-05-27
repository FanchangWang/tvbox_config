"""
TVBox 源检查和 JSON 生成工具

这是一个用于检查 TVBox 源是否可用并生成 tvbox.json 和 my.json 的工具。

主要模块：
- logger: 控制台日志输出
- source_manager: 源列表管理（读取和保存 YAML）
- http_client: HTTP 客户端（支持加密源）
- json_builder: JSON 文件构建
- app: 主程序入口
- models: 数据模型

使用示例：
```python
from src import App

app = App()
app.run()
```
"""

from .app import App
from .http_client import HttpClient
from .json_builder import JsonBuilder
from .logger import Logger
from .models import AvailableSource, Source
from .source_manager import SourceManager

__all__ = [
    "Logger",
    "SourceManager",
    "HttpClient",
    "JsonBuilder",
    "App",
    "Source",
    "AvailableSource",
]
"""公共 API 导出列表"""
