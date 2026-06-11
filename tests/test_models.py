from tvbox_config.models import AvailableSource, Source


class TestSource:
    def test_to_dict(self) -> None:
        s = Source(name="test", urls=["http://a.com", "http://b.com"], encrypted=True, r18=False)
        assert s.to_dict() == {
            "name": "test",
            "urls": ["http://a.com", "http://b.com"],
            "encrypted": True,
            "r18": False,
        }

    def test_from_dict(self) -> None:
        data = {"name": "foo", "urls": ["http://x.com"], "encrypted": True, "r18": False}
        s = Source.from_dict(data)
        assert s.name == "foo"
        assert s.urls == ["http://x.com"]
        assert s.encrypted is True
        assert s.r18 is False

    def test_from_dict_defaults(self) -> None:
        s = Source.from_dict({"name": "bar", "urls": ["http://y.com"]})
        assert s.encrypted is False
        assert s.r18 is False

    def test_roundtrip(self) -> None:
        original = Source(name="x", urls=["http://z.com"], encrypted=True, r18=True)
        restored = Source.from_dict(original.to_dict())
        assert restored == original


class TestAvailableSource:
    def test_to_dict(self) -> None:
        s = AvailableSource(name="test", url="http://a.com", r18=False)
        assert s.to_dict() == {"name": "test", "url": "http://a.com", "r18": False}

    def test_from_dict(self) -> None:
        s = AvailableSource.from_dict({"name": "foo", "url": "http://x.com", "r18": True})
        assert s.name == "foo"
        assert s.url == "http://x.com"
        assert s.r18 is True

    def test_from_dict_defaults(self) -> None:
        s = AvailableSource.from_dict({"name": "bar", "url": "http://y.com"})
        assert s.r18 is False

    def test_roundtrip(self) -> None:
        original = AvailableSource(name="x", url="http://z.com", r18=True)
        restored = AvailableSource.from_dict(original.to_dict())
        assert restored == original
