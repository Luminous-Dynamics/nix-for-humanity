"""Simple logging utilities"""

import logging
import sys


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name or __name__)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def set_log_level(level: str) -> None:
    """Set the global log level"""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logging.getLogger().setLevel(numeric_level)
