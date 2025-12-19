"""Configuration settings for LabBot."""

import os
from typing import Any


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # API Configuration
        self.cors_origins: list[str] = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
        self.cors_credentials: bool = True
        self.cors_methods: list[str] = ["*"]
        self.cors_headers: list[str] = ["*"]

        # API Keys
        self.anthropic_api_key: str = os.getenv(
            "ANTHROPIC_API_KEY", ""
        )

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Application
        self.app_title: str = "LabBot"
        self.app_version: str = "0.1.0"
        self.app_description: str = (
            "Lab results interpreter API helping patients understand their tests"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "cors_origins": self.cors_origins,
            "cors_credentials": self.cors_credentials,
            "cors_methods": self.cors_methods,
            "cors_headers": self.cors_headers,
            "anthropic_api_key": self.anthropic_api_key,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "app_title": self.app_title,
            "app_version": self.app_version,
            "app_description": self.app_description,
        }


# Global settings instance
settings = Settings()
