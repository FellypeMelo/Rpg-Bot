from .base_settings import BaseSettings

class DevelopmentSettings(BaseSettings):
    # Override settings for development environment
    LOG_LEVEL: str = "DEBUG"
    # Other development-specific overrides