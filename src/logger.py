"""日志模块，负责输出控制台日志"""

import logging


class Logger:
    """日志管理类"""

    def __init__(self, name: str = "tvbox"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """配置日志"""
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
