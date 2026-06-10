from typing import ClassVar

import dirtyjson

from .http_client import HttpClient
from .json_builder import JsonBuilder
from .logger import get_logger
from .models import AvailableSource, Source
from .source_manager import SourceManager

logger = get_logger()


class App:
    DECRYPT_URLS: ClassVar[list[str]] = [
        "https://feiyangdigital.v1.mk/api/jiemi.php?url=",
        "https://www.饭太硬.net/jm/jiemi.php?url=",
    ]
    GITHUB_PROXY = "https://github.allproxy.dpdns.org"

    def __init__(self):
        self.source_manager = SourceManager()
        self.http_client = HttpClient()
        self.json_builder = JsonBuilder(self.GITHUB_PROXY)

    @staticmethod
    def _check_content_valid(content: str) -> bool:
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

    @staticmethod
    def _apply_github_proxy(url: str, proxy: str) -> str:
        if "raw.githubusercontent.com" in url:
            return f"{proxy}/{url}"
        return url

    def _try_fetch(self, url: str) -> str | None:
        content = self.http_client.get(url)
        if content and self._check_content_valid(content):
            return content
        return None

    def check_source(self, source: Source) -> AvailableSource | None:
        for url in source.urls:
            base_url = self._apply_github_proxy(url, self.GITHUB_PROXY)

            if source.encrypted:
                for decrypt_url in self.DECRYPT_URLS:
                    final_url = f"{decrypt_url}{base_url}"
                    logger.debug(f"⏳ 检查数据源: {source.name} - {final_url}")
                    if self._try_fetch(final_url):
                        logger.debug(f"✅ 可用数据源: {source.name} - {base_url}")
                        return AvailableSource(
                            name=source.name,
                            url=base_url,
                            r18=source.r18,
                        )
            else:
                logger.debug(f"⏳ 检查数据源: {source.name} - {base_url}")
                if self._try_fetch(base_url):
                    logger.debug(f"✅ 可用数据源: {source.name} - {base_url}")
                    return AvailableSource(
                        name=source.name,
                        url=base_url,
                        r18=source.r18,
                    )

        logger.error(f"🚫 不可用数据源: {source.name}")
        return None

    def run(self) -> None:
        logger.info("开始生成 tvbox 线路...")

        sources = self.source_manager.load_sources()
        history = self.source_manager.load_history()

        available_sources: list[AvailableSource] = []
        for source in sources:
            if result := self.check_source(source):
                available_sources.append(result)

        if self.source_manager.are_sources_equal(available_sources, history):
            logger.info("无差异, 无需更新! 脚本结束!")
            return

        self.source_manager.save_history(available_sources)
        self.json_builder.build_and_save(available_sources)

        tvbox_count = sum(1 for s in available_sources if not s.r18)
        my_count = len(available_sources)

        logger.info(f"tvbox.json 包含 {tvbox_count} 个可用数据源")
        logger.info(f"my.json 包含 {my_count} 个可用数据源")
        logger.info("生成完成! 脚本结束!")


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()
