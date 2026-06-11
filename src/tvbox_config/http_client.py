from typing import ClassVar

import httpx


class HttpClient:
    HEADERS: ClassVar[dict[str, str]] = {
        "User-Agent": "okhttp/4.12.0",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    }

    CONNECT_TIMEOUT = 5
    READ_TIMEOUT = 30

    def __init__(self):
        self._client = httpx.Client(
            headers=self.HEADERS,
            timeout=httpx.Timeout(self.READ_TIMEOUT, connect=self.CONNECT_TIMEOUT),
            follow_redirects=True,
        )

    def get(self, url: str) -> str | None:
        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        else:
            return response.text
