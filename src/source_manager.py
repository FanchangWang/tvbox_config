"""源管理模块，负责读取和保存源列表"""

from pathlib import Path
from typing import List

import yaml

from .models import AvailableSource, Source


class SourceManager:
    """源管理类，负责源列表的读取和历史记录管理"""

    CONFIG_DIR = "config"
    """配置目录"""
    SOURCES_FILE = "sources.yaml"
    """源列表文件名"""
    HISTORY_FILE = "history.yaml"
    """历史记录文件名"""

    def __init__(self):
        """初始化源管理类"""
        self.config_dir = Path(self.CONFIG_DIR)
        self.sources_path = self.config_dir / self.SOURCES_FILE
        self.history_path = self.config_dir / self.HISTORY_FILE

    def load_sources(self) -> List[Source]:
        """
        读取源列表配置文件

        Returns:
            Source 对象列表，如果文件不存在或读取失败返回空列表
        """
        self.config_dir.mkdir(exist_ok=True)
        sources: List[Source] = []
        if self.sources_path.exists():
            with self.sources_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for item in data.get("sources", []):
                    sources.append(Source.from_dict(item))
        return sources

    def load_history(self) -> List[AvailableSource]:
        """
        读取历史记录文件

        Returns:
            AvailableSource 对象列表，如果文件不存在或读取失败返回空列表
        """
        sources: List[AvailableSource] = []
        if self.history_path.exists():
            with self.history_path.open("r", encoding="utf-8") as f:
                for item in yaml.safe_load(f) or []:
                    sources.append(AvailableSource.from_dict(item))
        return sources

    def save_history(self, data: List[AvailableSource]) -> None:
        """
        保存历史记录文件

        Args:
            data: 要保存的 AvailableSource 列表
        """
        self.config_dir.mkdir(exist_ok=True)
        dict_data = [source.to_dict() for source in data]
        with self.history_path.open("w", encoding="utf-8") as f:
            yaml.dump(dict_data, f, allow_unicode=True, indent=2)

    @staticmethod
    def are_sources_equal(
        list1: List[AvailableSource], list2: List[AvailableSource]
    ) -> bool:
        """
        比较两个源列表是否相等（按顺序）

        Args:
            list1: 第一个源列表
            list2: 第二个源列表

        Returns:
            如果两个列表相等返回 True，否则返回 False
        """
        if len(list1) != len(list2):
            return False
        for s1, s2 in zip(list1, list2):
            if s1.to_dict() != s2.to_dict():
                return False
        return True
