import httpx


class HttpClient:
    HEADERS = {
        "User-Agent": "okhttp/3.12.11",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    }

    CONNECT_TIMEOUT = 5
    READ_TIMEOUT = 30

    def __init__(self):
        self._client = httpx.Client(
            headers=self.HEADERS,
            timeout=httpx.Timeout(self.READ_TIMEOUT, connect=self.CONNECT_TIMEOUT),
        )

    def get(self, url: str) -> str | None:
        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError:
            return None
