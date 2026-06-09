from pathlib import Path

import yaml

from .models import AvailableSource, Source


class SourceManager:
    CONFIG_DIR = "config"
    SOURCES_FILE = "sources.yaml"
    HISTORY_FILE = "history.yaml"

    def __init__(self):
        self.config_dir = Path(self.CONFIG_DIR)
        self.sources_path = self.config_dir / self.SOURCES_FILE
        self.history_path = self.config_dir / self.HISTORY_FILE

    def load_sources(self) -> list[Source]:
        self.config_dir.mkdir(exist_ok=True)
        sources: list[Source] = []
        if self.sources_path.exists():
            with self.sources_path.open("r", encoding="utf-8") as f:
                for item in yaml.safe_load(f).get("sources", []):
                    sources.append(Source.from_dict(item))
        return sources

    def load_history(self) -> list[AvailableSource]:
        sources: list[AvailableSource] = []
        if self.history_path.exists():
            with self.history_path.open("r", encoding="utf-8") as f:
                for item in yaml.safe_load(f) or []:
                    sources.append(AvailableSource.from_dict(item))
        return sources

    def save_history(self, data: list[AvailableSource]) -> None:
        self.config_dir.mkdir(exist_ok=True)
        dict_data = [source.to_dict() for source in data]
        with self.history_path.open("w", encoding="utf-8") as f:
            yaml.dump(dict_data, f, allow_unicode=True, indent=2)

    @staticmethod
    def are_sources_equal(list1: list[AvailableSource], list2: list[AvailableSource]) -> bool:
        if len(list1) != len(list2):
            return False
        return all(s1.to_dict() == s2.to_dict() for s1, s2 in zip(list1, list2, strict=True))
