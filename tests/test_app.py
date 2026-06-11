import httpx
import respx
import yaml

from tvbox_config.app import App
from tvbox_config.models import AvailableSource, Source

_VALID_JSON = '{"spider": "s", "sites": [{"key": "k", "name": "n", "type": 3}]}'


class TestCheckContentValid:
    def test_valid_json(self) -> None:
        assert App._check_content_valid(_VALID_JSON)

    def test_missing_spider(self) -> None:
        assert not App._check_content_valid('{"sites": []}')

    def test_missing_sites(self) -> None:
        assert not App._check_content_valid('{"spider": "s"}')

    def test_empty_spider(self) -> None:
        assert not App._check_content_valid('{"spider": "", "sites": []}')

    def test_empty_sites(self) -> None:
        assert not App._check_content_valid('{"spider": "s", "sites": []}')

    def test_invalid_json(self) -> None:
        assert not App._check_content_valid("not json")


class TestApplyGithubProxy:
    def test_github_url_gets_proxied(self) -> None:
        url = "https://raw.githubusercontent.com/user/repo/file.json"
        proxy = "https://proxy.example.com"
        result = App._apply_github_proxy(url, proxy)
        assert result == "https://proxy.example.com/https://raw.githubusercontent.com/user/repo/file.json"

    def test_non_github_url_unchanged(self) -> None:
        url = "http://example.com/data"
        proxy = "https://proxy.example.com"
        assert App._apply_github_proxy(url, proxy) == url


class TestCheckSource:
    def test_non_encrypted_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/data").respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="test", urls=["http://example.com/data"], encrypted=False)
        result = app.check_source(source)
        assert result is not None
        assert result.name == "test"
        assert result.url == "http://example.com/data"

    def test_non_encrypted_fail_then_next_url(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://first.com").respond(404)
        respx_mock.get("http://second.com").respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="test", urls=["http://first.com", "http://second.com"], encrypted=False)
        result = app.check_source(source)
        assert result is not None
        assert result.url == "http://second.com"

    def test_non_encrypted_all_fail(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://a.com").respond(404)
        respx_mock.get("http://b.com").respond(500)
        app = App()
        source = Source(name="test", urls=["http://a.com", "http://b.com"], encrypted=False)
        assert app.check_source(source) is None

    def test_encrypted_local_decrypt_success(self, respx_mock: respx.MockRouter) -> None:
        from tvbox_config.decrypt import pad_end
        from Crypto.Cipher import AES

        plaintext = _VALID_JSON
        key_str, iv_str = "k", "aaaaaaaaaaaaa"
        key = pad_end(key_str)
        iv = pad_end(iv_str)
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext.encode() + bytes([pad_len] * pad_len)
        ct = AES.new(key, AES.MODE_CBC, iv).encrypt(padded)
        encrypted_data = f"2423{key_str.encode().hex()}2324{ct.hex()}{iv_str.encode().hex()}"

        respx_mock.get("http://encrypted.com").respond(200, text=encrypted_data)
        app = App()
        source = Source(name="enc", urls=["http://encrypted.com"], encrypted=True)
        result = app.check_source(source)
        assert result is not None
        assert result.url == "http://encrypted.com"

    def test_encrypted_local_fail_api_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://encrypted.com").respond(200, text="garbage")
        for decrypt_url in App.DECRYPT_URLS:
            respx_mock.get(f"{decrypt_url}http://encrypted.com").respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="enc", urls=["http://encrypted.com"], encrypted=True)
        result = app.check_source(source)
        assert result is not None
        assert result.url == "http://encrypted.com"

    def test_encrypted_all_fail(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://encrypted.com").respond(200, text="garbage")
        for decrypt_url in App.DECRYPT_URLS:
            respx_mock.get(f"{decrypt_url}http://encrypted.com").respond(404)
        app = App()
        source = Source(name="enc", urls=["http://encrypted.com"], encrypted=True)
        assert app.check_source(source) is None

    def test_encrypted_local_fetch_fails_api_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://encrypted.com").mock(side_effect=httpx.ConnectError)
        for decrypt_url in App.DECRYPT_URLS:
            respx_mock.get(f"{decrypt_url}http://encrypted.com").respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="enc", urls=["http://encrypted.com"], encrypted=True)
        result = app.check_source(source)
        assert result is not None

    def test_encrypted_local_decrypt_exception(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://encrypted.com").respond(200, text="not valid hex for aes")
        for decrypt_url in App.DECRYPT_URLS:
            respx_mock.get(f"{decrypt_url}http://encrypted.com").respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="enc", urls=["http://encrypted.com"], encrypted=True)
        result = app.check_source(source)
        assert result is not None

    def test_encrypted_github_url_proxied(self, respx_mock: respx.MockRouter) -> None:
        raw_url = "https://raw.githubusercontent.com/user/repo/data"
        proxied = f"{App.GITHUB_PROXY}/{raw_url}"
        respx_mock.get(proxied).respond(200, text=_VALID_JSON)
        app = App()
        source = Source(name="gh", urls=[raw_url], encrypted=False)
        result = app.check_source(source)
        assert result is not None
        assert result.url == proxied


class TestRun:
    def test_no_changes_skips_save(self, tmp_path, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/data").respond(200, text=_VALID_JSON)
        app = App()
        app.source_manager.config_dir = tmp_path / "config"
        app.source_manager.sources_path = app.source_manager.config_dir / "sources.yaml"
        app.source_manager.history_path = app.source_manager.config_dir / "history.yaml"
        app.source_manager.config_dir.mkdir(exist_ok=True)

        sources_data = {"sources": [{"name": "test", "urls": ["http://example.com/data"]}]}
        app.source_manager.sources_path.write_text(yaml.dump(sources_data), encoding="utf-8")
        app.source_manager.save_history(
            [AvailableSource(name="test", url="http://example.com/data", r18=False)]
        )

        app.run()
        assert app.source_manager.history_path.exists()
