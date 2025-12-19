"""Test configuration settings."""

import os

from labbot.config import Settings


def test_settings_default_values() -> None:
    """Test that default settings are properly initialized."""
    settings = Settings()

    assert settings.app_title == "LabBot"
    assert settings.app_version == "0.1.0"
    assert settings.log_level == "INFO"
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0
    assert "localhost" in str(settings.cors_origins)
    assert settings.cors_credentials is True
    assert settings.cors_methods == ["*"]
    assert settings.cors_headers == ["*"]


def test_settings_cors_configuration() -> None:
    """Test that CORS origins are properly configured."""
    settings = Settings()

    expected_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    for origin in expected_origins:
        assert origin in settings.cors_origins


def test_settings_anthropic_api_key_empty() -> None:
    """Test that anthropic_api_key is empty by default."""
    # Ensure env var is not set
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

    settings = Settings()
    assert settings.anthropic_api_key == ""


def test_settings_anthropic_api_key_from_env() -> None:
    """Test that anthropic_api_key can be loaded from environment."""
    test_key = "test_key_12345"
    os.environ["ANTHROPIC_API_KEY"] = test_key

    settings = Settings()
    assert settings.anthropic_api_key == test_key

    # Cleanup
    del os.environ["ANTHROPIC_API_KEY"]


def test_settings_log_level_from_env() -> None:
    """Test that log_level can be overridden from environment."""
    os.environ["LOG_LEVEL"] = "DEBUG"

    settings = Settings()
    assert settings.log_level == "DEBUG"

    # Cleanup
    del os.environ["LOG_LEVEL"]


def test_settings_to_dict() -> None:
    """Test that settings can be converted to dictionary."""
    settings = Settings()
    settings_dict = settings.to_dict()

    assert isinstance(settings_dict, dict)
    assert "app_title" in settings_dict
    assert "app_version" in settings_dict
    assert "cors_origins" in settings_dict
    assert "anthropic_api_key" in settings_dict
    assert "log_level" in settings_dict
    assert settings_dict["app_title"] == "LabBot"
    assert settings_dict["app_version"] == "0.1.0"


def test_settings_immutable_properties() -> None:
    """Test that key settings properties are set correctly."""
    settings = Settings()

    assert settings.app_title == "LabBot"
    assert settings.app_version == "0.1.0"
    assert "Lab results interpreter" in settings.app_description
    assert isinstance(settings.log_format, str)
    assert "asctime" in settings.log_format
