from dataclasses import dataclass
from typing import Self


@dataclass
class Source:
    name: str
    urls: list[str]
    encrypted: bool = False
    r18: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "urls": self.urls,
            "encrypted": self.encrypted,
            "r18": self.r18,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            urls=data["urls"],
            encrypted=data.get("encrypted", False),
            r18=data.get("r18", False),
        )


@dataclass
class AvailableSource:
    name: str
    url: str
    r18: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "r18": self.r18,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            url=data["url"],
            r18=data.get("r18", False),
        )
