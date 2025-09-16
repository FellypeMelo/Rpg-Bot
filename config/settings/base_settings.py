import os

class BaseSettings:
    # Discord Bot Settings
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    COMMAND_PREFIX: str = "!"

    # MongoDB Settings
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    MONGODB_DATABASE_NAME: str = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")
    MONGODB_CHARACTER_COLLECTION: str = os.getenv("MONGODB_CHARACTER_COLLECTION", "characters")
    MONGODB_CLASS_TEMPLATE_COLLECTION: str = os.getenv("MONGODB_CLASS_TEMPLATE_COLLECTION", "class_templates")

    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_COMBAT_SESSION_TTL_HOURS: int = int(os.getenv("REDIS_COMBAT_SESSION_TTL_HOURS", 4))
    REDIS_MAX_SESSIONS_PER_USER: int = int(os.getenv("REDIS_MAX_SESSIONS_PER_USER", 3))

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/rpg_bot.log")
    AUDIT_LOG_FILE: str = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")

    # Security Settings
    RATE_LIMIT_COMMANDS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_COMMANDS_PER_MINUTE", 10))
    RATE_LIMIT_WINDOW_SECONDS: int = 60 # 1 minute

    # Backup Settings
    MONGODB_BACKUP_DIR: str = os.getenv("MONGODB_BACKUP_DIR", "backups/mongodb")
    REDIS_BACKUP_DIR: str = os.getenv("REDIS_BACKUP_DIR", "backups/redis")
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", 7))

    # Other
    DEFAULT_CLASS_TEMPLATES_PATH: str = "config/constants/default_class_templates.json"