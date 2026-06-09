import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import AvailableSource


class JsonBuilder:
    DIST_DIR = "dist"

    def __init__(self, github_proxy: str = ""):
        self.github_proxy = github_proxy
        self.dist_dir = Path(self.DIST_DIR)

    def _add_timestamp(self, sources: list[AvailableSource]) -> None:
        if sources:
            tz = timezone(timedelta(hours=8))
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
            sources[0].name = f"{sources[0].name} [{timestamp}]"

    def _save_json(self, data: list[AvailableSource], filename: str) -> None:
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

    def build_and_save(self, sources: list[AvailableSource]) -> None:
        tvbox_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources if not s.r18]
        my_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources]

        self._add_timestamp(tvbox_sources)
        self._add_timestamp(my_sources)

        self._save_json(tvbox_sources, "tvbox.json")
        self._save_json(my_sources, "my.json")
