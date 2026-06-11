import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import AvailableSource

DIST_DIR = Path("dist")


def _add_timestamp(sources: list[AvailableSource]) -> None:
    if sources:
        tz = timezone(timedelta(hours=8))
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
        sources[0].name = f"{sources[0].name} [{timestamp}]"


def _save_json(data: list[AvailableSource], filename: str) -> None:
    output_path = DIST_DIR / filename
    DIST_DIR.mkdir(exist_ok=True)

    dict_data = []
    for source in data:
        source_dict = source.to_dict()
        source_dict = {k: v for k, v in source_dict.items() if k != "r18"}
        dict_data.append(source_dict)

    result = {"urls": dict_data}
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def build_and_save(sources: list[AvailableSource]) -> None:
    tvbox_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources if not s.r18]
    my_sources = [AvailableSource(s.name, s.url, s.r18) for s in sources]

    _add_timestamp(tvbox_sources)
    _add_timestamp(my_sources)

    _save_json(tvbox_sources, "tvbox.json")
    _save_json(my_sources, "my.json")
