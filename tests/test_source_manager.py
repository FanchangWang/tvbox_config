from pathlib import Path

import pytest
import yaml

from tvbox_config.models import AvailableSource, Source
from tvbox_config.source_manager import SourceManager


@pytest.fixture
def manager(tmp_path: Path) -> SourceManager:
    m = SourceManager()
    m.config_dir = tmp_path / "config"
    m.sources_path = m.config_dir / "sources.yaml"
    m.history_path = m.config_dir / "history.yaml"
    m.config_dir.mkdir(exist_ok=True)
    return m


class TestLoadSources:
    def test_empty_when_file_missing(self, manager: SourceManager) -> None:
        assert manager.load_sources() == []

    def test_loads_sources(self, manager: SourceManager) -> None:
        data = {
            "sources": [
                {"name": "src1", "urls": ["http://a.com"], "encrypted": True, "r18": False},
                {"name": "src2", "urls": ["http://b.com"]},
            ]
        }
        manager.sources_path.write_text(yaml.dump(data), encoding="utf-8")
        sources = manager.load_sources()
        assert len(sources) == 2
        assert sources[0].name == "src1"
        assert sources[0].encrypted is True
        assert sources[1].name == "src2"
        assert sources[1].encrypted is False

    def test_creates_config_dir(self, manager: SourceManager, tmp_path: Path) -> None:
        manager.config_dir = tmp_path / "nonexistent"
        manager.sources_path = manager.config_dir / "sources.yaml"
        result = manager.load_sources()
        assert result == []
        assert manager.config_dir.exists()


class TestLoadHistory:
    def test_empty_when_file_missing(self, manager: SourceManager) -> None:
        assert manager.load_history() == []

    def test_loads_history(self, manager: SourceManager) -> None:
        data = [
            {"name": "src1", "url": "http://a.com", "r18": False},
            {"name": "src2", "url": "http://b.com", "r18": True},
        ]
        manager.history_path.write_text(yaml.dump(data), encoding="utf-8")
        history = manager.load_history()
        assert len(history) == 2
        assert history[0].name == "src1"
        assert history[1].r18 is True


class TestSaveHistory:
    def test_saves_and_roundtrips(self, manager: SourceManager) -> None:
        data = [
            AvailableSource(name="src1", url="http://a.com", r18=False),
            AvailableSource(name="src2", url="http://b.com", r18=True),
        ]
        manager.save_history(data)
        assert manager.history_path.exists()
        loaded = manager.load_history()
        assert loaded == data

    def test_creates_dir_if_not_exists(self, manager: SourceManager) -> None:
        import shutil
        shutil.rmtree(manager.config_dir)
        data = [AvailableSource(name="x", url="http://x.com", r18=False)]
        manager.save_history(data)
        assert manager.config_dir.exists()
        assert manager.history_path.exists()


class TestAreSourcesEqual:
    def test_equal_lists(self, manager: SourceManager) -> None:
        a = [AvailableSource("s", "http://a.com", False)]
        b = [AvailableSource("s", "http://a.com", False)]
        assert manager.are_sources_equal(a, b) is True

    def test_different_length(self, manager: SourceManager) -> None:
        a = [AvailableSource("s", "http://a.com", False)]
        b: list[AvailableSource] = []
        assert manager.are_sources_equal(a, b) is False

    def test_different_name(self, manager: SourceManager) -> None:
        a = [AvailableSource("a", "http://x.com", False)]
        b = [AvailableSource("b", "http://x.com", False)]
        assert manager.are_sources_equal(a, b) is False

    def test_different_r18(self, manager: SourceManager) -> None:
        a = [AvailableSource("s", "http://x.com", False)]
        b = [AvailableSource("s", "http://x.com", True)]
        assert manager.are_sources_equal(a, b) is False
