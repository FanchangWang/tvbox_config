import httpx
import respx

from tvbox_config.http_client import HttpClient


class TestHttpClient:
    def test_get_success(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/data").respond(200, text="response body")
        client = HttpClient()
        result = client.get("http://example.com/data")
        assert result == "response body"

    def test_get_404_returns_none(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/notfound").respond(404)
        client = HttpClient()
        result = client.get("http://example.com/notfound")
        assert result is None

    def test_get_timeout_returns_none(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/timeout").mock(side_effect=httpx.TimeoutException)
        client = HttpClient()
        result = client.get("http://example.com/timeout")
        assert result is None

    def test_get_network_error_returns_none(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/error").mock(side_effect=httpx.ConnectError)
        client = HttpClient()
        result = client.get("http://example.com/error")
        assert result is None

    def test_follows_redirect(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.get("http://example.com/redirect").respond(301, headers={"Location": "/target"})
        respx_mock.get("http://example.com/target").respond(200, text="target content")
        client = HttpClient()
        result = client.get("http://example.com/redirect")
        assert result == "target content"

    def test_headers_set_correctly(self, respx_mock: respx.MockRouter) -> None:
        def check_headers(request: httpx.Request) -> httpx.Response:
            assert request.headers["User-Agent"] == "okhttp/4.12.0"
            assert request.headers["Accept-Encoding"] == "gzip"
            return httpx.Response(200, text="ok")

        respx_mock.get("http://example.com/check").mock(side_effect=check_headers)
        client = HttpClient()
        assert client.get("http://example.com/check") == "ok"
