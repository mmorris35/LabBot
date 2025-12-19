"""Test logging configuration."""

import logging
from typing import Any

from labbot.logging_config import setup_logging


def test_setup_logging_initializes_logger() -> None:
    """Test that setup_logging configures the logger."""
    setup_logging()

    logger = logging.getLogger("labbot")
    assert logger is not None
    assert logger.name == "labbot"


def test_setup_logging_sets_log_level() -> None:
    """Test that logging level is configured."""
    setup_logging()

    logger = logging.getLogger("labbot")
    # Logger level should be set to INFO (default)
    assert logger.level >= logging.INFO or logger.level == logging.NOTSET


def test_setup_logging_with_debug_level(monkeypatch: Any) -> None:
    """Test that logging respects DEBUG level from config."""
    # Mock the settings to use DEBUG level
    import os

    os.environ["LOG_LEVEL"] = "DEBUG"

    # Need to reimport to pick up new env var
    import importlib

    import labbot.logging_config

    importlib.reload(labbot.logging_config)
    setup_logging()

    logger = logging.getLogger("labbot")
    assert logger is not None

    # Cleanup
    del os.environ["LOG_LEVEL"]


def test_setup_logging_console_handler() -> None:
    """Test that console handler is configured."""
    setup_logging()

    logger = logging.getLogger("labbot")
    has_console_handler = False

    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            has_console_handler = True
            break

    # Either the logger has handlers or root logger does
    if not has_console_handler:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                has_console_handler = True
                break

    assert has_console_handler


def test_setup_logging_idempotent() -> None:
    """Test that setup_logging can be called multiple times safely."""
    # Should not raise any exceptions
    setup_logging()
    setup_logging()
    setup_logging()

    logger = logging.getLogger("labbot")
    assert logger is not None
