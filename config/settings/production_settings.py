from .base_settings import BaseSettings

class ProductionSettings(BaseSettings):
    # Override settings for production environment
    LOG_LEVEL: str = "INFO"
    # Ensure sensitive data is not logged in production
    # MONGODB_CONNECTION_STRING should be a secure URI
    # REDIS_HOST should be a secure endpoint
    # Other production-specific overrides