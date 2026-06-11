import json
from pathlib import Path

import pytest

from tvbox_config.models import AvailableSource


@pytest.fixture(autouse=True)
def _patch_dist_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("tvbox_config.json_builder.DIST_DIR", tmp_path / "dist")


class TestBuildAndSave:
    def test_generates_tvbox_and_my_json(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        sources = [
            AvailableSource(name="src1", url="http://a.com", r18=False),
            AvailableSource(name="src2", url="http://b.com", r18=False),
        ]
        build_and_save(sources)

        tvbox_path = DIST_DIR / "tvbox.json"
        my_path = DIST_DIR / "my.json"
        assert tvbox_path.exists()
        assert my_path.exists()

    def test_tvbox_excludes_r18(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        sources = [
            AvailableSource(name="normal", url="http://n.com", r18=False),
            AvailableSource(name="adult", url="http://a.com", r18=True),
        ]
        build_and_save(sources)

        tvbox_data = json.loads((DIST_DIR / "tvbox.json").read_text(encoding="utf-8"))
        urls = [item["url"] for item in tvbox_data["urls"]]
        assert "http://a.com" not in urls
        assert "http://n.com" in urls

    def test_my_includes_all(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        sources = [
            AvailableSource(name="normal", url="http://n.com", r18=False),
            AvailableSource(name="adult", url="http://a.com", r18=True),
        ]
        build_and_save(sources)

        my_data = json.loads((DIST_DIR / "my.json").read_text(encoding="utf-8"))
        urls = [item["url"] for item in my_data["urls"]]
        assert "http://a.com" in urls
        assert "http://n.com" in urls

    def test_r18_field_removed_from_output(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        sources = [AvailableSource(name="src", url="http://x.com", r18=True)]
        build_and_save(sources)

        my_data = json.loads((DIST_DIR / "my.json").read_text(encoding="utf-8"))
        item = my_data["urls"][0]
        assert "r18" not in item

    def test_empty_sources(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        build_and_save([])
        tvbox_data = json.loads((DIST_DIR / "tvbox.json").read_text(encoding="utf-8"))
        assert tvbox_data == {"urls": []}

    def test_timestamp_added_to_first_source_tvbox(self, monkeypatch, tmp_path) -> None:
        from tvbox_config.json_builder import build_and_save, DIST_DIR

        sources = [AvailableSource(name="src", url="http://x.com", r18=False)]
        build_and_save(sources)

        tvbox_data = json.loads((DIST_DIR / "tvbox.json").read_text(encoding="utf-8"))
        assert "[" in tvbox_data["urls"][0]["name"]
        assert "src" in tvbox_data["urls"][0]["name"]
