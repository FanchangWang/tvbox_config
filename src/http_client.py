"""HTTP 客户端模块，负责发送 HTTP 请求"""

from typing import Optional

import requests


class HttpClient:
    """HTTP 客户端类，支持普通请求和加密源请求"""

    HEADERS = {
        "User-Agent": "okhttp/3.12.11",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    }
    """HTTP 请求头"""

    CONNECT_TIMEOUT = 5
    """连接超时时间（秒）"""
    READ_TIMEOUT = 30
    """读取超时时间（秒）"""

    def __init__(self, decrypt_url: str):
        """
        初始化 HTTP 客户端

        Args:
            decrypt_url: 解密接口 URL
        """
        self.decrypt_url = decrypt_url

    def get(self, url: str, encrypted: bool = False) -> Optional[str]:
        """
        发送 GET 请求

        Args:
            url: 请求的 URL
            encrypted: 是否为加密源，默认为 False

        Returns:
            响应内容，如果请求失败返回 None
        """
        request_url = self._build_request_url(url, encrypted)
        try:
            response = requests.get(
                request_url,
                headers=self.HEADERS,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
            )
            response.raise_for_status()
            return response.text
        except (requests.RequestException, Exception):
            return None

    def _build_request_url(self, url: str, encrypted: bool) -> str:
        """
        构建请求 URL

        Args:
            url: 原始 URL
            encrypted: 是否为加密源

        Returns:
            构建后的完整请求 URL
        """
        if encrypted:
            return f"{self.decrypt_url}{url}"
        return url
