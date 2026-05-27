"""JSON 构建模块，负责生成和保存输出文件"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from .models import AvailableSource


class JsonBuilder:
    """JSON 构建输出类，负责生成 tvbox.json 和 my.json"""

    DIST_DIR = "dist"
    """输出目录"""

    def __init__(self, github_proxy: str = ""):
        """
        初始化 JSON 构建类

        Args:
            github_proxy: GitHub 代理地址，默认为空
        """
        self.github_proxy = github_proxy
        self.dist_dir = Path(self.DIST_DIR)

    def _add_timestamp(self, sources: List[AvailableSource]) -> None:
        """
        为第一个源添加时间戳

        Args:
            sources: 可用源列表
        """
        if sources:
            tz = timezone(timedelta(hours=8))
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
            sources[0].name = f"{sources[0].name} [{timestamp}]"

    def _save_json(self, data: List[AvailableSource], filename: str) -> None:
        """
        保存 JSON 文件到 dist 目录

        Args:
            data: 要保存的数据
            filename: 文件名
        """
        output_path = self.dist_dir / filename
        self.dist_dir.mkdir(exist_ok=True)
        
        dict_data = []
        for source in data:
            source_dict = source.to_dict()
            source_dict = {k: v for k, v in source_dict.items() if k != "r18"}
            dict_data.append(source_dict)
        
        result = {"urls": dict_data}
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def build_and_save(self, sources: List[AvailableSource]) -> None:
        """
        构建并保存 tvbox.json 和 my.json

        Args:
            sources: 可用源列表
        """
        # 深拷贝源对象，避免引用共享问题
        tvbox_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources if not s.r18]
        my_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources]

        self._add_timestamp(tvbox_sources)
        self._add_timestamp(my_sources)

        self._save_json(tvbox_sources, "tvbox.json")
        self._save_json(my_sources, "my.json")
