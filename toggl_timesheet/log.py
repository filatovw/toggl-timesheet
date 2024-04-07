import logging


def get_logger(name: str, level: int) -> logging.Logger:
    logger = logging.getLogger(name)
    logging.basicConfig(encoding="utf-8", level=level)
    return logger
