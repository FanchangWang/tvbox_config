import logging
import sys


def get_logger(name: str = "tvbox_config") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        stderr_stream = open(sys.stderr.fileno(), "w", encoding="utf-8", closefd=False)
        handler = logging.StreamHandler(stream=stderr_stream)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    return logger
