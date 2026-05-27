"""数据模型模块，定义数据类"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Source:
    """源信息数据类"""
    name: str
    urls: List[str]
    encrypted: bool = False
    r18: bool = False

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "urls": self.urls,
            "encrypted": self.encrypted,
            "r18": self.r18,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        """从字典创建实例"""
        return cls(
            name=data["name"],
            urls=data["urls"],
            encrypted=data.get("encrypted", False),
            r18=data.get("r18", False),
        )


@dataclass
class AvailableSource:
    """可用源信息数据类"""
    name: str
    url: str
    r18: bool = False

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "url": self.url,
            "r18": self.r18,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AvailableSource":
        """从字典创建实例"""
        return cls(
            name=data["name"],
            url=data["url"],
            r18=data.get("r18", False),
        )
