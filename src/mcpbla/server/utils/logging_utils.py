import logging
from typing import Optional


_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def setup_logging(level: str = "INFO", logger_name: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger with a standard format.

    If a logger with handlers already exists, only updates its level.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(numeric_level)
    return logger
