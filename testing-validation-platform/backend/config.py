"""
Centralized configuration for testing-validation-platform.

Loads settings from environment variables or .env file.
Single source of truth for tracker URL, project name, and other settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment or .env file."""

    # Tracker Configuration
    tracker_url: str = "http://127.0.0.1:8001"
    project_name: str = "investing-platform"
    project_id: Optional[int] = None

    # Sync Configuration
    sync_interval: int = 300  # 5 minutes
    sync_retries: int = 3
    sync_retry_delay: int = 2  # seconds (exponential backoff)

    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8004
    api_timeout: int = 30  # seconds

    # Dashboard Configuration
    dashboard_auto_refresh: int = 30  # seconds

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def validate_settings() -> bool:
    """Validate that all required settings are present and valid.

    Returns:
        True if all settings are valid

    Raises:
        ValueError: If required settings are missing
    """
    if not settings.tracker_url:
        raise ValueError("TRACKER_URL is required")
    if not settings.project_name:
        raise ValueError("PROJECT_NAME is required")
    return True
