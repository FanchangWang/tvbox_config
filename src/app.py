"""主程序模块，整合所有功能"""

from typing import List, Optional

import dirtyjson

from .http_client import HttpClient
from .json_builder import JsonBuilder
from .logger import Logger
from .models import AvailableSource, Source
from .source_manager import SourceManager


class App:
    """主程序入口类，整合所有模块执行主要流程"""

    # 配置常量
    DECRYPT_URL = "https://feiyangdigital.v1.mk/api/jiemi.php?url="
    """解密接口 URL"""
    GITHUB_PROXY = "https://github.allproxy.dpdns.org"
    """GitHub 代理地址"""

    def __init__(self):
        """初始化 App 类"""
        self.logger = Logger()
        self.source_manager = SourceManager()
        self.http_client = HttpClient(self.DECRYPT_URL)
        self.json_builder = JsonBuilder(self.GITHUB_PROXY)

    def _check_content_valid(self, content: str) -> bool:
        """
        检查响应内容是否有效

        Args:
            content: 响应内容

        Returns:
            如果内容有效返回 True，否则返回 False
        """
        try:
            data = dirtyjson.loads(content)
            return (
                isinstance(data, dict)
                and "spider" in data
                and "sites" in data
                and data["spider"]
                and data["sites"]
            )
        except dirtyjson.error.Error:
            return False

    def _process_github_url(self, url: str) -> str:
        """
        处理 GitHub 链接，添加代理

        Args:
            url: 原始 URL

        Returns:
            处理后的 URL
        """
        if "raw.githubusercontent.com" in url:
            return f"{self.GITHUB_PROXY}/{url}"
        return url

    def check_source(self, source: Source) -> Optional[AvailableSource]:
        """
        检查单个源是否可用

        Args:
            source: Source 对象

        Returns:
            可用的 AvailableSource 对象，如果不可用返回 None
        """
        for url in source.urls:
            self.logger.debug(f"⏳ 检查数据源: {source.name} - {url}")
            processed_url = self._process_github_url(url)
            if (
                content := self.http_client.get(processed_url, source.encrypted)
            ) and self._check_content_valid(content):
                self.logger.debug(f"✅ 可用数据源: {source.name} - {url}")
                return AvailableSource(
                    name=source.name,
                    url=processed_url,
                    r18=source.r18,
                )

        self.logger.error(f"🚫 不可用数据源: {source.name}")
        return None

    def run(self) -> None:
        """执行主程序流程"""
        self.logger.info("开始生成 tvbox 线路...")

        sources = self.source_manager.load_sources()
        history = self.source_manager.load_history()

        available_sources: List[AvailableSource] = []
        for source in sources:
            if result := self.check_source(source):
                available_sources.append(result)

        if self.source_manager.are_sources_equal(available_sources, history):
            self.logger.info("无差异，无需更新！脚本结束！")
            return

        self.source_manager.save_history(available_sources)

        self.json_builder.build_and_save(available_sources)

        tvbox_count = len([s for s in available_sources if not s.r18])
        my_count = len(available_sources)

        self.logger.info(f"tvbox.json 包含 {tvbox_count} 个可用数据源")
        self.logger.info(f"my.json 包含 {my_count} 个可用数据源")
        self.logger.info("生成完成！脚本结束！")
