"""Centralized logging configuration for LabBot."""

import logging
import logging.config
from typing import Any


def setup_logging() -> None:
    """Configure logging for the application.

    Sets up structured logging with consistent format across all modules.
    Configures log level from environment settings.
    """
    from labbot.config import settings

    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "labbot": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(log_config)
    logger = logging.getLogger("labbot")
    logger.info("Logging configured with level %s", settings.log_level)
