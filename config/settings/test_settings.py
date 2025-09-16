from config.settings.base_settings import BaseSettings

class TestSettings(BaseSettings):
    # Override settings for test environment
    MONGODB_DATABASE_NAME: str = "test_rpg_bot_db"
    REDIS_DB: int = 1 # Use a different Redis DB for testing
    LOG_LEVEL: str = "DEBUG"
    # Other test-specific overrides